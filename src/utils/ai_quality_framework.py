"""
AI Quality Assurance Framework - Multi-layered AI output validation and enhancement.

This module provides comprehensive validation, scoring, and quality assurance
for AI-generated content in the blueprint generation system.
"""

import json
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import statistics
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality assessment dimensions"""
    FACTUAL_ACCURACY = "factual_accuracy"
    CONTENT_RELEVANCE = "content_relevance"
    STRUCTURAL_QUALITY = "structural_quality"
    ORIGINALITY_SCORE = "originality_score"
    BIAS_DETECTION = "bias_detection"

@dataclass
class WeightedScore:
    """Weighted score for quality dimensions"""
    weight: float
    score: float = 0.0
    max_score: float = 100.0
    
    @property
    def weighted_value(self) -> float:
        """Calculate weighted value"""
        return (self.score / self.max_score) * self.weight * 100

@dataclass
class ValidationResult:
    """Result of a validation check"""
    dimension: QualityDimension
    score: float
    max_score: float
    issues: List[str]
    recommendations: List[str]
    confidence: float
    execution_time: float
    details: Dict[str, Any]

@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    overall_score: float
    dimension_scores: Dict[QualityDimension, ValidationResult]
    recommendations: List[str]
    critical_issues: List[str]
    quality_grade: str
    timestamp: str
    metadata: Dict[str, Any]

class BaseValidator(ABC):
    """Base class for all quality validators"""
    
    def __init__(self, weight: float = 1.0):
        self.weight = weight
        self.name = self.__class__.__name__
    
    @abstractmethod
    def validate(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate the given data and return results"""
        pass
    
    def _calculate_score(self, positive_factors: List[float], 
                        negative_factors: List[float]) -> float:
        """Calculate score based on positive and negative factors"""
        if not positive_factors:
            return 0.0
        
        positive_score = statistics.mean(positive_factors)
        negative_penalty = sum(negative_factors) if negative_factors else 0.0
        
        # Apply penalty and ensure score is between 0 and 100
        final_score = max(0.0, min(100.0, positive_score - negative_penalty))
        return final_score

class FactCheckValidator(BaseValidator):
    """Validator for factual accuracy and consistency"""
    
    def __init__(self, weight: float = 0.3):
        super().__init__(weight)
        self.fact_patterns = {
            'statistics': r'\d+%|\d+\.\d+%|\d+ percent',
            'dates': r'\d{4}|\d{1,2}/\d{1,2}/\d{4}',
            'numbers': r'\$[\d,]+|\d+,\d+|\d+\.\d+',
            'claims': r'(studies show|research indicates|according to)',
            'absolutes': r'(always|never|all|none|every|completely)'
        }
    
    def validate(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate factual accuracy"""
        start_time = datetime.now()
        issues = []
        recommendations = []
        positive_factors = []
        negative_factors = []
        
        # Extract text content for analysis
        text_content = self._extract_text_content(data)
        
        # Check for unsupported claims
        unsupported_claims = self._check_unsupported_claims(text_content)
        if unsupported_claims:
            issues.extend(unsupported_claims)
            negative_factors.append(len(unsupported_claims) * 10)
        else:
            positive_factors.append(85.0)
        
        # Check for consistency in data
        consistency_score = self._check_internal_consistency(data)
        positive_factors.append(consistency_score)
        
        # Check for absolute statements that might be inaccurate
        absolute_statements = self._check_absolute_statements(text_content)
        if absolute_statements:
            issues.extend([f"Absolute statement: {stmt}" for stmt in absolute_statements])
            negative_factors.append(len(absolute_statements) * 5)
        
        # Check for proper attribution
        attribution_score = self._check_attribution(text_content)
        positive_factors.append(attribution_score)
        
        # Generate recommendations
        if issues:
            recommendations.extend([
                "Verify claims with authoritative sources",
                "Add proper citations and references",
                "Consider qualifying absolute statements",
                "Cross-check data for consistency"
            ])
        
        # Calculate final score
        score = self._calculate_score(positive_factors, negative_factors)
        confidence = max(0.7, min(1.0, len(positive_factors) / 4))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ValidationResult(
            dimension=QualityDimension.FACTUAL_ACCURACY,
            score=score,
            max_score=100.0,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            execution_time=execution_time,
            details={
                'unsupported_claims': len(unsupported_claims) if unsupported_claims else 0,
                'consistency_score': consistency_score,
                'absolute_statements': len(absolute_statements) if absolute_statements else 0,
                'attribution_score': attribution_score
            }
        )
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from blueprint data"""
        text_parts = []
        
        # Extract from different sections
        if 'heading_structure' in data:
            heading_data = data['heading_structure']
            if isinstance(heading_data, dict):
                if 'h1' in heading_data:
                    text_parts.append(heading_data['h1'])
                if 'h2_sections' in heading_data:
                    for section in heading_data['h2_sections']:
                        if isinstance(section, dict) and 'title' in section:
                            text_parts.append(section['title'])
        
        if 'content_outline' in data:
            outline_data = data['content_outline']
            text_parts.append(str(outline_data))
        
        if 'seo_recommendations' in data:
            seo_data = data['seo_recommendations']
            text_parts.append(str(seo_data))
        
        return ' '.join(text_parts)
    
    def _check_unsupported_claims(self, text: str) -> List[str]:
        """Check for claims that might need verification"""
        claims = []
        claim_patterns = [
            r'studies show that [^.]+',
            r'research indicates [^.]+',
            r'experts believe [^.]+',
            r'\d+% of [^.]+ (are|do|have) [^.]+',
            r'most [^.]+ (are|do|have) [^.]+'
        ]
        
        for pattern in claim_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                claims.append(match.group())
        
        return claims[:5]  # Limit to top 5 for relevance
    
    def _check_internal_consistency(self, data: Dict[str, Any]) -> float:
        """Check for internal consistency in the data"""
        consistency_score = 80.0  # Base score
        
        # Check keyword consistency
        keyword = data.get('keyword', '').lower()
        if keyword:
            text_content = self._extract_text_content(data).lower()
            keyword_mentions = text_content.count(keyword)
            
            if keyword_mentions >= 3:
                consistency_score += 10.0
            elif keyword_mentions == 0:
                consistency_score -= 20.0
        
        # Check topic cluster consistency
        if 'topic_clusters' in data:
            clusters = data['topic_clusters']
            if isinstance(clusters, dict) and 'primary_cluster' in clusters:
                primary_topics = clusters['primary_cluster']
                if len(primary_topics) >= 3:
                    consistency_score += 5.0
        
        return min(100.0, consistency_score)
    
    def _check_absolute_statements(self, text: str) -> List[str]:
        """Check for potentially inaccurate absolute statements"""
        absolutes = []
        absolute_patterns = [
            r'[^.]*\b(always|never|all|none|every|completely|totally|absolutely)\b[^.]*',
            r'[^.]*\b(100%|zero percent|no one|everyone)\b[^.]*'
        ]
        
        for pattern in absolute_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                absolutes.append(match.group().strip())
        
        return absolutes[:3]  # Limit to top 3
    
    def _check_attribution(self, text: str) -> float:
        """Check for proper attribution and sources"""
        attribution_score = 70.0  # Base score
        
        # Look for attribution indicators
        attribution_patterns = [
            r'according to',
            r'source:',
            r'study by',
            r'research from',
            r'data from'
        ]
        
        attribution_count = 0
        for pattern in attribution_patterns:
            attribution_count += len(re.findall(pattern, text.lower()))
        
        if attribution_count > 0:
            attribution_score += min(20.0, attribution_count * 5)
        
        return min(100.0, attribution_score)

class RelevanceScorer(BaseValidator):
    """Validator for content relevance to the target keyword and context"""
    
    def __init__(self, weight: float = 0.25):
        super().__init__(weight)
    
    def validate(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate content relevance"""
        start_time = datetime.now()
        issues = []
        recommendations = []
        positive_factors = []
        negative_factors = []
        
        keyword = data.get('keyword', '').lower()
        if not keyword:
            issues.append("No target keyword provided")
            negative_factors.append(50.0)
        
        # Extract text content
        text_content = self._extract_text_content(data)
        
        # Check keyword presence and density
        keyword_score = self._calculate_keyword_relevance(keyword, text_content)
        positive_factors.append(keyword_score)
        
        # Check semantic relevance
        semantic_score = self._calculate_semantic_relevance(keyword, data)
        positive_factors.append(semantic_score)
        
        # Check topic cluster alignment
        cluster_score = self._calculate_cluster_alignment(keyword, data)
        positive_factors.append(cluster_score)
        
        # Check for off-topic content
        off_topic_score = self._check_off_topic_content(keyword, text_content)
        if off_topic_score < 70:
            issues.append("Content contains potentially off-topic sections")
            negative_factors.append(80 - off_topic_score)
        else:
            positive_factors.append(off_topic_score)
        
        # Generate recommendations
        if keyword_score < 70:
            recommendations.append(f"Increase focus on target keyword: '{keyword}'")
        
        if semantic_score < 75:
            recommendations.append("Add more semantically related terms and concepts")
        
        if cluster_score < 70:
            recommendations.append("Align topic clusters better with target keyword")
        
        # Calculate final score
        score = self._calculate_score(positive_factors, negative_factors)
        confidence = 0.85
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ValidationResult(
            dimension=QualityDimension.CONTENT_RELEVANCE,
            score=score,
            max_score=100.0,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            execution_time=execution_time,
            details={
                'keyword_score': keyword_score,
                'semantic_score': semantic_score,
                'cluster_score': cluster_score,
                'off_topic_score': off_topic_score
            }
        )
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from blueprint data"""
        text_parts = []
        
        # Extract from various sections
        sections_to_extract = [
            'heading_structure', 'content_outline', 'seo_recommendations',
            'topic_clusters', 'content_insights'
        ]
        
        for section in sections_to_extract:
            if section in data:
                text_parts.append(str(data[section]))
        
        return ' '.join(text_parts).lower()
    
    def _calculate_keyword_relevance(self, keyword: str, text: str) -> float:
        """Calculate keyword relevance score"""
        if not keyword or not text:
            return 0.0
        
        # Count keyword appearances
        exact_matches = text.count(keyword)
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        # Calculate keyword density (target: 1-3%)
        keyword_density = (exact_matches / total_words) * 100
        
        # Score based on density
        if 1.0 <= keyword_density <= 3.0:
            density_score = 100.0
        elif 0.5 <= keyword_density < 1.0 or 3.0 < keyword_density <= 5.0:
            density_score = 80.0
        elif keyword_density > 0:
            density_score = 60.0
        else:
            density_score = 20.0
        
        # Check for keyword variations
        keyword_words = keyword.split()
        variation_score = 0.0
        for word in keyword_words:
            variation_score += text.count(word) * 5
        
        variation_score = min(30.0, variation_score)
        
        return min(100.0, density_score + variation_score)
    
    def _calculate_semantic_relevance(self, keyword: str, data: Dict[str, Any]) -> float:
        """Calculate semantic relevance based on related terms"""
        # Generate expected related terms for common keywords
        semantic_terms = self._generate_semantic_terms(keyword)
        
        text_content = self._extract_text_content(data)
        
        found_terms = 0
        for term in semantic_terms:
            if term in text_content:
                found_terms += 1
        
        if not semantic_terms:
            return 75.0  # Default score if no semantic terms
        
        semantic_score = (found_terms / len(semantic_terms)) * 100
        return min(100.0, semantic_score + 50)  # Add base score
    
    def _generate_semantic_terms(self, keyword: str) -> List[str]:
        """Generate semantically related terms for a keyword"""
        # Basic semantic term generation (could be enhanced with NLP models)
        semantic_map = {
            'content marketing': ['strategy', 'blog', 'social media', 'engagement', 'brand'],
            'seo': ['search engine', 'ranking', 'keywords', 'optimization', 'google'],
            'digital marketing': ['online', 'campaign', 'conversion', 'analytics', 'roi'],
            'web development': ['programming', 'website', 'frontend', 'backend', 'api'],
            'machine learning': ['algorithm', 'data', 'model', 'training', 'prediction']
        }
        
        # Get specific terms or generate generic ones
        if keyword in semantic_map:
            return semantic_map[keyword]
        
        # Generate basic related terms
        keyword_words = keyword.split()
        related_terms = []
        
        for word in keyword_words:
            related_terms.extend([
                f"{word} guide",
                f"{word} tips",
                f"{word} strategy",
                f"best {word}",
                f"{word} tutorial"
            ])
        
        return related_terms[:10]
    
    def _calculate_cluster_alignment(self, keyword: str, data: Dict[str, Any]) -> float:
        """Calculate alignment between keyword and topic clusters"""
        if 'topic_clusters' not in data:
            return 60.0  # Default score if no clusters
        
        clusters = data['topic_clusters']
        alignment_score = 60.0  # Base score
        
        # Check primary cluster
        if isinstance(clusters, dict) and 'primary_cluster' in clusters:
            primary_cluster = clusters['primary_cluster']
            if isinstance(primary_cluster, list):
                keyword_in_primary = any(keyword in term.lower() for term in primary_cluster)
                if keyword_in_primary:
                    alignment_score += 25.0
        
        # Check related keywords
        if isinstance(clusters, dict) and 'related_keywords' in clusters:
            related_keywords = clusters['related_keywords']
            if isinstance(related_keywords, list):
                keyword_related = any(keyword in term.lower() for term in related_keywords)
                if keyword_related:
                    alignment_score += 15.0
        
        return min(100.0, alignment_score)
    
    def _check_off_topic_content(self, keyword: str, text: str) -> float:
        """Check for potentially off-topic content"""
        # This is a simplified implementation
        # In practice, you might use more sophisticated NLP models
        
        keyword_words = set(keyword.split())
        text_words = set(text.split())
        
        if not text_words:
            return 0.0
        
        # Calculate overlap ratio
        overlap = len(keyword_words.intersection(text_words))
        overlap_ratio = overlap / len(keyword_words) if keyword_words else 0
        
        # Score based on overlap
        if overlap_ratio >= 0.8:
            return 95.0
        elif overlap_ratio >= 0.5:
            return 85.0
        elif overlap_ratio >= 0.3:
            return 75.0
        else:
            return 60.0

class StructuralAnalyzer(BaseValidator):
    """Validator for content structure and organization"""
    
    def __init__(self, weight: float = 0.2):
        super().__init__(weight)
    
    def validate(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate content structure"""
        start_time = datetime.now()
        issues = []
        recommendations = []
        positive_factors = []
        negative_factors = []
        
        # Check heading structure
        heading_score = self._analyze_heading_structure(data)
        positive_factors.append(heading_score)
        
        # Check content organization
        organization_score = self._analyze_content_organization(data)
        positive_factors.append(organization_score)
        
        # Check completeness
        completeness_score = self._analyze_completeness(data)
        positive_factors.append(completeness_score)
        
        # Check hierarchy depth
        hierarchy_score = self._analyze_hierarchy_depth(data)
        positive_factors.append(hierarchy_score)
        
        # Generate recommendations based on analysis
        if heading_score < 75:
            recommendations.append("Improve heading structure and hierarchy")
        
        if organization_score < 70:
            recommendations.append("Better organize content sections")
        
        if completeness_score < 80:
            recommendations.append("Add missing content sections")
        
        # Calculate final score
        score = self._calculate_score(positive_factors, negative_factors)
        confidence = 0.9
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ValidationResult(
            dimension=QualityDimension.STRUCTURAL_QUALITY,
            score=score,
            max_score=100.0,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            execution_time=execution_time,
            details={
                'heading_score': heading_score,
                'organization_score': organization_score,
                'completeness_score': completeness_score,
                'hierarchy_score': hierarchy_score
            }
        )
    
    def _analyze_heading_structure(self, data: Dict[str, Any]) -> float:
        """Analyze the quality of heading structure"""
        if 'heading_structure' not in data:
            return 30.0
        
        heading_data = data['heading_structure']
        score = 50.0  # Base score
        
        # Check for H1
        if 'h1' in heading_data and heading_data['h1']:
            score += 20.0
        
        # Check for H2 sections
        if 'h2_sections' in heading_data:
            h2_sections = heading_data['h2_sections']
            if isinstance(h2_sections, list) and len(h2_sections) >= 3:
                score += 20.0
                
                # Check for H3 subsections
                h3_count = 0
                for section in h2_sections:
                    if isinstance(section, dict) and 'h3_subsections' in section:
                        h3_subsections = section['h3_subsections']
                        if isinstance(h3_subsections, list):
                            h3_count += len(h3_subsections)
                
                if h3_count >= 6:  # Average of 2 H3s per H2
                    score += 10.0
        
        return min(100.0, score)
    
    def _analyze_content_organization(self, data: Dict[str, Any]) -> float:
        """Analyze overall content organization"""
        score = 60.0  # Base score
        
        # Check for logical flow in sections
        if 'heading_structure' in data:
            heading_data = data['heading_structure']
            if 'h2_sections' in heading_data:
                h2_sections = heading_data['h2_sections']
                if isinstance(h2_sections, list):
                    # Look for logical progression
                    section_titles = [s.get('title', '') for s in h2_sections if isinstance(s, dict)]
                    if self._check_logical_flow(section_titles):
                        score += 20.0
        
        # Check for topic clusters organization
        if 'topic_clusters' in data:
            clusters = data['topic_clusters']
            if isinstance(clusters, dict) and len(clusters) >= 3:
                score += 10.0
        
        # Check for SEO recommendations organization
        if 'seo_recommendations' in data:
            seo_data = data['seo_recommendations']
            if isinstance(seo_data, (list, dict)) and seo_data:
                score += 10.0
        
        return min(100.0, score)
    
    def _check_logical_flow(self, section_titles: List[str]) -> bool:
        """Check if section titles follow a logical flow"""
        # Simple heuristic for logical flow
        flow_indicators = {
            'introduction': 0,
            'what is': 1,
            'how to': 2,
            'benefits': 3,
            'examples': 4,
            'conclusion': 5
        }
        
        title_scores = []
        for title in section_titles:
            title_lower = title.lower()
            for indicator, score in flow_indicators.items():
                if indicator in title_lower:
                    title_scores.append(score)
                    break
        
        # Check if generally increasing (logical flow)
        if len(title_scores) >= 2:
            increasing_count = sum(1 for i in range(1, len(title_scores)) 
                                 if title_scores[i] >= title_scores[i-1])
            return increasing_count >= len(title_scores) - 2
        
        return True  # Default to true for short lists
    
    def _analyze_completeness(self, data: Dict[str, Any]) -> float:
        """Analyze completeness of the blueprint"""
        required_sections = [
            'keyword', 'heading_structure', 'topic_clusters', 
            'content_insights', 'seo_recommendations'
        ]
        
        present_sections = sum(1 for section in required_sections if section in data and data[section])
        completeness_ratio = present_sections / len(required_sections)
        
        return completeness_ratio * 100
    
    def _analyze_hierarchy_depth(self, data: Dict[str, Any]) -> float:
        """Analyze the depth and appropriateness of content hierarchy"""
        score = 70.0  # Base score
        
        if 'heading_structure' not in data:
            return score
        
        heading_data = data['heading_structure']
        
        # Check hierarchy depth (H1 -> H2 -> H3)
        has_h1 = 'h1' in heading_data and heading_data['h1']
        has_h2 = 'h2_sections' in heading_data and isinstance(heading_data['h2_sections'], list)
        has_h3 = False
        
        if has_h2:
            for section in heading_data['h2_sections']:
                if isinstance(section, dict) and 'h3_subsections' in section:
                    has_h3 = True
                    break
        
        # Score based on hierarchy presence
        if has_h1 and has_h2 and has_h3:
            score = 100.0
        elif has_h1 and has_h2:
            score = 85.0
        elif has_h1:
            score = 70.0
        
        return score

class OriginalityChecker(BaseValidator):
    """Validator for content originality and uniqueness"""
    
    def __init__(self, weight: float = 0.15):
        super().__init__(weight)
    
    def validate(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate content originality"""
        start_time = datetime.now()
        issues = []
        recommendations = []
        positive_factors = []
        negative_factors = []
        
        # Check for unique perspectives
        uniqueness_score = self._check_unique_perspectives(data)
        positive_factors.append(uniqueness_score)
        
        # Check for generic content patterns
        generic_score = self._check_generic_patterns(data)
        if generic_score < 70:
            issues.append("Content contains generic patterns")
            negative_factors.append(80 - generic_score)
        else:
            positive_factors.append(generic_score)
        
        # Check for creative elements
        creativity_score = self._check_creative_elements(data)
        positive_factors.append(creativity_score)
        
        # Generate recommendations
        if uniqueness_score < 75:
            recommendations.append("Add more unique perspectives and insights")
        
        if generic_score < 70:
            recommendations.append("Reduce generic content patterns")
        
        if creativity_score < 65:
            recommendations.append("Include more creative and engaging elements")
        
        # Calculate final score
        score = self._calculate_score(positive_factors, negative_factors)
        confidence = 0.75  # Lower confidence as this is harder to assess
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ValidationResult(
            dimension=QualityDimension.ORIGINALITY_SCORE,
            score=score,
            max_score=100.0,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            execution_time=execution_time,
            details={
                'uniqueness_score': uniqueness_score,
                'generic_score': generic_score,
                'creativity_score': creativity_score
            }
        )
    
    def _check_unique_perspectives(self, data: Dict[str, Any]) -> float:
        """Check for unique perspectives in the content"""
        # This is a simplified implementation
        # In practice, you might compare against a database of existing content
        
        unique_indicators = [
            'case study', 'personal experience', 'unique approach',
            'innovative method', 'exclusive insight', 'original research',
            'expert interview', 'real-world example'
        ]
        
        text_content = str(data).lower()
        found_indicators = sum(1 for indicator in unique_indicators if indicator in text_content)
        
        # Score based on unique indicators found
        uniqueness_score = 60.0 + (found_indicators * 8)
        return min(100.0, uniqueness_score)
    
    def _check_generic_patterns(self, data: Dict[str, Any]) -> float:
        """Check for overly generic content patterns"""
        generic_patterns = [
            r'in this article, we will',
            r'this comprehensive guide',
            r'everything you need to know',
            r'the ultimate guide to',
            r'step-by-step guide',
            r'best practices for'
        ]
        
        text_content = str(data).lower()
        generic_count = 0
        
        for pattern in generic_patterns:
            matches = re.findall(pattern, text_content)
            generic_count += len(matches)
        
        # Score inversely related to generic patterns
        if generic_count == 0:
            return 100.0
        elif generic_count <= 2:
            return 85.0
        elif generic_count <= 4:
            return 70.0
        else:
            return 50.0
    
    def _check_creative_elements(self, data: Dict[str, Any]) -> float:
        """Check for creative and engaging elements"""
        creative_indicators = [
            'analogy', 'metaphor', 'story', 'anecdote', 'example',
            'comparison', 'contrast', 'illustration', 'scenario'
        ]
        
        text_content = str(data).lower()
        found_creative = sum(1 for indicator in creative_indicators if indicator in text_content)
        
        # Score based on creative elements
        creativity_score = 50.0 + (found_creative * 10)
        return min(100.0, creativity_score)

class BiasDetector(BaseValidator):
    """Validator for bias detection and mitigation"""
    
    def __init__(self, weight: float = 0.1):
        super().__init__(weight)
        self.bias_patterns = {
            'gender': [r'\b(he|his|him)\b(?! or she)', r'\bmankind\b', r'\bguys\b'],
            'cultural': [r'obviously', r'clearly', r'everyone knows'],
            'ageism': [r'digital natives', r'millennials are', r'boomers'],
            'assumption': [r'of course', r'naturally', r'it goes without saying']
        }
    
    def validate(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate for bias and inclusive language"""
        start_time = datetime.now()
        issues = []
        recommendations = []
        positive_factors = []
        negative_factors = []
        
        text_content = str(data).lower()
        
        # Check for different types of bias
        bias_scores = {}
        total_bias_count = 0
        
        for bias_type, patterns in self.bias_patterns.items():
            bias_count = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_content)
                bias_count += len(matches)
            
            bias_scores[bias_type] = bias_count
            total_bias_count += bias_count
            
            if bias_count > 0:
                issues.append(f"Potential {bias_type} bias detected ({bias_count} instances)")
        
        # Calculate bias score
        if total_bias_count == 0:
            bias_score = 100.0
        elif total_bias_count <= 2:
            bias_score = 85.0
        elif total_bias_count <= 5:
            bias_score = 70.0
        else:
            bias_score = 50.0
        
        positive_factors.append(bias_score)
        
        # Check for inclusive language
        inclusive_score = self._check_inclusive_language(text_content)
        positive_factors.append(inclusive_score)
        
        # Generate recommendations
        if total_bias_count > 0:
            recommendations.extend([
                "Review content for inclusive language",
                "Consider diverse perspectives and audiences",
                "Use gender-neutral language where appropriate",
                "Avoid cultural assumptions"
            ])
        
        # Calculate final score
        score = self._calculate_score(positive_factors, negative_factors)
        confidence = 0.8
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ValidationResult(
            dimension=QualityDimension.BIAS_DETECTION,
            score=score,
            max_score=100.0,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            execution_time=execution_time,
            details={
                'bias_scores': bias_scores,
                'total_bias_count': total_bias_count,
                'inclusive_score': inclusive_score
            }
        )
    
    def _check_inclusive_language(self, text: str) -> float:
        """Check for inclusive language usage"""
        inclusive_indicators = [
            'they/them', 'people', 'individuals', 'everyone',
            'all backgrounds', 'diverse', 'inclusive', 'accessible'
        ]
        
        found_inclusive = sum(1 for indicator in inclusive_indicators if indicator in text)
        
        # Score based on inclusive language
        inclusive_score = 70.0 + (found_inclusive * 5)
        return min(100.0, inclusive_score)

class AIQualityFramework:
    """
    Multi-layered AI output validation and enhancement framework
    """
    
    def __init__(self):
        """Initialize the quality framework with validators"""
        self.validators = {
            QualityDimension.FACTUAL_ACCURACY: FactCheckValidator(0.3),
            QualityDimension.CONTENT_RELEVANCE: RelevanceScorer(0.25),
            QualityDimension.STRUCTURAL_QUALITY: StructuralAnalyzer(0.2),
            QualityDimension.ORIGINALITY_SCORE: OriginalityChecker(0.15),
            QualityDimension.BIAS_DETECTION: BiasDetector(0.1)
        }
        
        self.quality_thresholds = {
            'excellent': 90.0,
            'good': 75.0,
            'fair': 60.0,
            'poor': 45.0
        }
        
        logger.info("AI Quality Framework initialized with {} validators".format(len(self.validators)))
    
    def assess_quality(self, data: Dict[str, Any], 
                      context: Dict[str, Any] = None) -> QualityReport:
        """
        Perform comprehensive quality assessment
        
        Args:
            data: Blueprint data to assess
            context: Additional context for assessment
            
        Returns:
            Comprehensive quality report
        """
        logger.info("Starting comprehensive quality assessment")
        start_time = datetime.now()
        
        dimension_results = {}
        all_recommendations = []
        critical_issues = []
        
        # Run all validators
        for dimension, validator in self.validators.items():
            try:
                result = validator.validate(data, context)
                dimension_results[dimension] = result
                
                # Collect recommendations
                all_recommendations.extend(result.recommendations)
                
                # Identify critical issues (score < 50)
                if result.score < 50.0:
                    critical_issues.extend(result.issues)
                
                logger.debug(f"Validator {dimension.value} completed with score: {result.score:.2f}")
                
            except Exception as e:
                logger.error(f"Validator {dimension.value} failed: {str(e)}")
                # Create error result
                dimension_results[dimension] = ValidationResult(
                    dimension=dimension,
                    score=0.0,
                    max_score=100.0,
                    issues=[f"Validation failed: {str(e)}"],
                    recommendations=["Fix validation error"],
                    confidence=0.0,
                    execution_time=0.0,
                    details={'error': str(e)}
                )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(dimension_results)
        
        # Determine quality grade
        quality_grade = self._determine_quality_grade(overall_score)
        
        # Remove duplicate recommendations
        unique_recommendations = list(set(all_recommendations))
        
        # Create quality report
        report = QualityReport(
            overall_score=overall_score,
            dimension_scores=dimension_results,
            recommendations=unique_recommendations[:10],  # Top 10 recommendations
            critical_issues=list(set(critical_issues)),
            quality_grade=quality_grade,
            timestamp=datetime.now().isoformat(),
            metadata={
                'total_execution_time': (datetime.now() - start_time).total_seconds(),
                'validators_run': len(dimension_results),
                'average_confidence': statistics.mean([r.confidence for r in dimension_results.values()]),
                'framework_version': '1.0.0'
            }
        )
        
        logger.info(f"Quality assessment completed. Overall score: {overall_score:.2f} ({quality_grade})")
        return report
    
    def _calculate_overall_score(self, dimension_results: Dict[QualityDimension, ValidationResult]) -> float:
        """Calculate weighted overall score"""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dimension, result in dimension_results.items():
            validator = self.validators[dimension]
            weighted_score = (result.score / 100.0) * validator.weight
            total_weighted_score += weighted_score
            total_weight += validator.weight
        
        if total_weight == 0:
            return 0.0
        
        return (total_weighted_score / total_weight) * 100.0
    
    def _determine_quality_grade(self, overall_score: float) -> str:
        """Determine quality grade based on score"""
        if overall_score >= self.quality_thresholds['excellent']:
            return 'A'
        elif overall_score >= self.quality_thresholds['good']:
            return 'B'
        elif overall_score >= self.quality_thresholds['fair']:
            return 'C'
        elif overall_score >= self.quality_thresholds['poor']:
            return 'D'
        else:
            return 'F'
    
    def get_framework_stats(self) -> Dict[str, Any]:
        """Get framework statistics and configuration"""
        return {
            'validators': {dim.value: {'weight': val.weight, 'name': val.name} 
                          for dim, val in self.validators.items()},
            'quality_thresholds': self.quality_thresholds,
            'total_weight': sum(v.weight for v in self.validators.values()),
            'framework_version': '1.0.0'
        }

# Decorator for automatic quality assessment
def assess_ai_quality(cache_results: bool = True):
    """
    Decorator for automatic AI quality assessment
    
    Args:
        cache_results: Whether to cache quality assessment results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Perform quality assessment if result is a blueprint
            if isinstance(result, dict) and 'keyword' in result:
                quality_framework = AIQualityFramework()
                quality_report = quality_framework.assess_quality(result)
                
                # Add quality report to result
                result['quality_assessment'] = asdict(quality_report)
                
                logger.info(f"Quality assessment added to result. Score: {quality_report.overall_score:.2f}")
            
            return result
        
        return wrapper
    return decorator

# Global framework instance
_global_quality_framework = None

def get_default_quality_framework() -> AIQualityFramework:
    """Get the default global quality framework instance"""
    global _global_quality_framework
    if _global_quality_framework is None:
        _global_quality_framework = AIQualityFramework()
    return _global_quality_framework