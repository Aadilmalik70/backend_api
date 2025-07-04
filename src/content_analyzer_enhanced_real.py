"""
Enhanced Content Analyzer with Google Natural Language API Integration - Phase 2.2

This module provides enhanced content analysis functionality using Google's Natural Language API
as the primary client, with intelligent fallback to Gemini API clients.

Phase 2.2 Implementation:
- ✅ Integrated Google Natural Language API as primary client
- ✅ Enhanced with Google APIs Gemini client for AI-powered insights
- ✅ Maintained fallback to original Gemini NLP client
- ✅ Added comprehensive error handling and graceful degradation
- ✅ Enhanced content quality assessment with Google's advanced NLP
- ✅ Added AI-readiness analysis for modern SEO features
"""

import logging
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from utils.browser_content_scraper import BrowserContentScraper
from utils.google_apis.natural_language_client import NaturalLanguageClient
from utils.google_apis.gemini_client import GeminiClient
from utils.gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAnalyzerEnhancedReal:
    """
    Enhanced content analyzer with Google Natural Language API integration.
    
    This class provides methods for analyzing content from URLs using:
    1. Google Natural Language API (primary) - for advanced NLP analysis
    2. Google APIs Gemini client (secondary) - for AI-powered insights
    3. Original Gemini NLP client (fallback) - for basic analysis
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the enhanced content analyzer.
        
        Args:
            gemini_api_key: Gemini API key (for fallback client)
        """
        # Initialize clients in order of preference
        self.natural_language_client = NaturalLanguageClient()
        self.gemini_client = GeminiClient()
        self.gemini_nlp_client = GeminiNLPClient(api_key=gemini_api_key)
        
        # Check client availability
        self.nl_available = self.natural_language_client.health_check()
        self.gemini_available = self.gemini_client.health_check()
        self.gemini_nlp_available = gemini_api_key is not None
        
        logger.info(f"Content Analyzer initialized - NL API: {self.nl_available}, Gemini API: {self.gemini_available}, Gemini NLP: {self.gemini_nlp_available}")
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze content from a URL using Google Natural Language API.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary containing enhanced analysis results
        """
        logger.info(f"Analyzing content from URL: {url}")
        
        # Scrape content from URL
        with BrowserContentScraper() as scraper:
            scraped_content = scraper.scrape_content(url)
        
        # Extract main content for NLP analysis
        main_content = scraped_content["main_content"]
        
        # Perform NLP analysis using the best available client
        nlp_analysis = self._perform_nlp_analysis(main_content)
        
        # Perform AI-powered analysis if available
        ai_analysis = self._perform_ai_analysis(main_content)
        
        # Compile comprehensive results
        result = {
            "url": url,
            "title": scraped_content["title"],
            "description": scraped_content["description"],
            "word_count": scraped_content["word_count"],
            "readability": self._calculate_readability(scraped_content),
            "content_structure": {
                "headings": len(scraped_content["headings"]),
                "paragraphs": scraped_content["content_metrics"]["paragraph_count"] if "paragraph_count" in scraped_content["content_metrics"] else 0,
                "images": len(scraped_content["images"]),
                "links": {
                    "internal": len(scraped_content["links"]["internal"]),
                    "external": len(scraped_content["links"]["external"]),
                    "total": scraped_content["links"]["total"]
                }
            },
            "content_analysis": {
                "entities": nlp_analysis.get("entities", []),
                "sentiment": nlp_analysis.get("sentiment", {}),
                "categories": nlp_analysis.get("categories", []),
                "language": nlp_analysis.get("language", "en"),
                "analysis_source": nlp_analysis.get("analysis_source", "fallback")
            },
            "ai_analysis": ai_analysis,
            "content_quality": self._assess_content_quality_enhanced(scraped_content, nlp_analysis),
            "seo_analysis": self._analyze_seo_enhanced(scraped_content, nlp_analysis),
            "recommendations": self._generate_recommendations_enhanced(scraped_content, nlp_analysis, ai_analysis)
        }
        
        return result
    
    def _perform_nlp_analysis(self, content: str) -> Dict[str, Any]:
        """
        Perform NLP analysis using the best available client.
        
        Args:
            content: Content to analyze
            
        Returns:
            NLP analysis results
        """
        # Try Google Natural Language API first
        if self.nl_available:
            try:
                logger.info("Using Google Natural Language API for content analysis")
                analysis = self.natural_language_client.analyze_content(
                    content,
                    analyze_entities=True,
                    analyze_sentiment=True,
                    analyze_syntax=False
                )
                analysis["analysis_source"] = "google_natural_language"
                return analysis
            except Exception as e:
                logger.warning(f"Google Natural Language API failed: {e}")
                self.nl_available = False
        
        # Fallback to Gemini NLP client
        if self.gemini_nlp_available:
            try:
                logger.info("Using Gemini NLP client for content analysis")
                analysis = self.gemini_nlp_client.analyze_content(content)
                analysis["analysis_source"] = "gemini_nlp"
                return analysis
            except Exception as e:
                logger.warning(f"Gemini NLP client failed: {e}")
                self.gemini_nlp_available = False
        
        # Final fallback to basic analysis
        logger.warning("Using basic fallback analysis")
        return self._basic_content_analysis(content)
    
    def _perform_ai_analysis(self, content: str) -> Dict[str, Any]:
        """
        Perform AI-powered analysis using Google APIs Gemini client.
        
        Args:
            content: Content to analyze
            
        Returns:
            AI analysis results
        """
        ai_analysis = {
            "ai_readiness_score": 0.0,
            "ai_overview_optimization": {},
            "featured_snippet_potential": {},
            "schema_suggestions": {},
            "entity_optimization": {},
            "analysis_source": "none"
        }
        
        if self.gemini_available:
            try:
                logger.info("Performing AI analysis with Google APIs Gemini client")
                
                # AI readiness analysis
                ai_readiness = self.gemini_client.analyze_ai_readiness(content)
                ai_analysis["ai_readiness_score"] = ai_readiness.get("overall_ai_readiness", 0.0)
                ai_analysis["ai_readiness_details"] = ai_readiness
                
                # AI Overview optimization
                ai_overview = self.gemini_client.optimize_for_ai_overview(content, "general query")
                ai_analysis["ai_overview_optimization"] = ai_overview
                
                # Schema markup suggestions
                schema_suggestions = self.gemini_client.generate_schema_markup_suggestions(content, "article")
                ai_analysis["schema_suggestions"] = schema_suggestions
                
                ai_analysis["analysis_source"] = "google_gemini"
                
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                self.gemini_available = False
        
        return ai_analysis
    
    def _basic_content_analysis(self, content: str) -> Dict[str, Any]:
        """
        Basic content analysis fallback when APIs are not available.
        
        Args:
            content: Content to analyze
            
        Returns:
            Basic analysis results
        """
        # Simple entity extraction
        entities = []
        # Find potential entities (capitalized words)
        potential_entities = re.findall(r'\\b[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*\\b', content)
        for entity in potential_entities[:10]:  # Limit to top 10
            entities.append({
                "name": entity,
                "type": "UNKNOWN",
                "salience": 0.1,
                "mentions": [{"text": entity, "type": "PROPER"}]
            })
        
        # Simple sentiment analysis
        positive_words = {'good', 'great', 'excellent', 'best', 'amazing', 'wonderful', 'fantastic'}
        negative_words = {'bad', 'worst', 'terrible', 'awful', 'horrible', 'poor'}
        
        words = content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        sentiment_score = 0.0
        if len(words) > 0:
            sentiment_score = (positive_count - negative_count) / len(words)
        
        return {
            "entities": entities,
            "sentiment": {
                "score": sentiment_score,
                "magnitude": abs(sentiment_score),
                "interpretation": "positive" if sentiment_score > 0.1 else ("negative" if sentiment_score < -0.1 else "neutral")
            },
            "categories": [],
            "language": "en",
            "analysis_source": "basic_fallback"
        }
    
    def _calculate_readability(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate readability metrics for content.
        
        Args:
            content: Scraped content dictionary
            
        Returns:
            Dictionary containing readability metrics
        """
        # Extract metrics from content_metrics if available
        if "content_metrics" in content and "readability_score" in content["content_metrics"]:
            readability_score = content["content_metrics"]["readability_score"]
        else:
            # Calculate basic readability score (Flesch Reading Ease approximation)
            text = content["main_content"]
            word_count = content["word_count"]
            
            # Count sentences (approximation)
            sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
            sentence_count = len(sentences)
            
            # Count syllables (very rough approximation)
            syllable_count = sum(self._count_syllables(word) for word in text.split())
            
            # Calculate Flesch Reading Ease score
            if sentence_count > 0 and word_count > 0:
                avg_sentence_length = word_count / sentence_count
                avg_syllables_per_word = syllable_count / word_count
                readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
                readability_score = max(0, min(100, readability_score))  # Clamp to 0-100
            else:
                readability_score = 50  # Default middle value
        
        # Determine readability level
        if readability_score >= 90:
            level = "Very Easy"
        elif readability_score >= 80:
            level = "Easy"
        elif readability_score >= 70:
            level = "Fairly Easy"
        elif readability_score >= 60:
            level = "Standard"
        elif readability_score >= 50:
            level = "Fairly Difficult"
        elif readability_score >= 30:
            level = "Difficult"
        else:
            level = "Very Difficult"
        
        return {
            "score": round(readability_score, 2),
            "level": level,
            "description": f"Content is {level.lower()} to read and understand."
        }
    
    def _count_syllables(self, word: str) -> int:
        """
        Count syllables in a word (approximation).
        
        Args:
            word: Word to count syllables for
            
        Returns:
            Number of syllables
        """
        word = word.lower()
        
        # Remove non-alphanumeric characters
        word = re.sub(r'[^a-z]', '', word)
        
        if not word:
            return 0
        
        # Count vowel groups
        count = len(re.findall(r'[aeiouy]+', word))
        
        # Adjust for silent e at end
        if word.endswith('e') and len(word) > 2 and word[-2] not in 'aeiouy':
            count -= 1
        
        # Ensure at least one syllable
        return max(1, count)
    
    def _assess_content_quality_enhanced(self, scraped_content: Dict[str, Any], nlp_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced content quality assessment using Google Natural Language API insights.
        
        Args:
            scraped_content: Scraped content dictionary
            nlp_analysis: NLP analysis dictionary
            
        Returns:
            Dictionary containing enhanced content quality assessment
        """
        # Extract metrics
        word_count = scraped_content["word_count"]
        
        # Get paragraph count from content_metrics or calculate
        if "content_metrics" in scraped_content and "paragraph_count" in scraped_content["content_metrics"]:
            paragraph_count = scraped_content["content_metrics"]["paragraph_count"]
        else:
            # Approximate paragraph count
            paragraphs = [p for p in scraped_content["main_content"].split('\
') if p.strip()]
            paragraph_count = len(paragraphs)
        
        # Get counts
        heading_count = len(scraped_content["headings"])
        image_count = len(scraped_content["images"])
        internal_link_count = len(scraped_content["links"]["internal"])
        external_link_count = len(scraped_content["links"]["external"])
        
        # Enhanced analysis with NLP insights
        entities = nlp_analysis.get("entities", [])
        sentiment = nlp_analysis.get("sentiment", {})
        entity_count = len(entities)
        
        # Calculate enhanced metrics
        content_density = word_count / max(1, paragraph_count)
        heading_ratio = word_count / max(1, heading_count)
        entity_density = entity_count / max(1, word_count / 100)  # Entities per 100 words
        
        # Enhanced scoring system
        quality_score = 0
        
        # Content length scoring (enhanced)
        if word_count >= 1500:
            length_score = 5
            length_assessment = "Comprehensive"
        elif word_count >= 1000:
            length_score = 4
            length_assessment = "Long"
        elif word_count >= 600:
            length_score = 3
            length_assessment = "Medium"
        elif word_count >= 300:
            length_score = 2
            length_assessment = "Short"
        else:
            length_score = 1
            length_assessment = "Very Short"
        
        quality_score += length_score * 15
        
        # Structure scoring (enhanced)
        structure_score = 0
        
        # Heading frequency (ideal: 1 heading per 150-300 words)
        if heading_count > 0 and 150 <= heading_ratio <= 300:
            structure_score += 3
        elif heading_count > 0:
            structure_score += 2
        
        # Paragraph length (ideal: 40-100 words per paragraph)
        if 40 <= content_density <= 100:
            structure_score += 2
        elif content_density < 150:
            structure_score += 1
        
        # Entity distribution (enhanced with NLP)
        if entity_density >= 3:  # Good entity density
            structure_score += 2
        elif entity_density >= 1:
            structure_score += 1
        
        structure_score = min(5, structure_score)
        quality_score += structure_score * 15
        
        # Sentiment scoring (enhanced)
        sentiment_score = sentiment.get("score", 0)
        sentiment_magnitude = sentiment.get("magnitude", 0)
        
        if -0.2 <= sentiment_score <= 0.3:  # Neutral to slightly positive
            sentiment_contribution = 15
        elif -0.5 <= sentiment_score <= 0.5:
            sentiment_contribution = 10
        else:
            sentiment_contribution = 5
        
        quality_score += sentiment_contribution
        
        # Entity quality scoring (new)
        entity_quality = 0
        if entities:
            # Check for diverse entity types
            entity_types = set(entity.get("type", "UNKNOWN") for entity in entities)
            if len(entity_types) >= 3:
                entity_quality += 15
            elif len(entity_types) >= 2:
                entity_quality += 10
            else:
                entity_quality += 5
            
            # Check entity salience
            avg_salience = sum(entity.get("salience", 0) for entity in entities) / len(entities)
            if avg_salience >= 0.1:
                entity_quality += 10
            elif avg_salience >= 0.05:
                entity_quality += 5
        
        quality_score += entity_quality
        
        # Media and links scoring
        if image_count > 0:
            quality_score += 5
        if external_link_count > 0:
            quality_score += 5
        if internal_link_count > 0:
            quality_score += 5
        
        # Ensure score is within 1-100 range
        quality_score = min(100, max(1, quality_score))
        
        return {
            "overall_score": quality_score,
            "length": {
                "assessment": length_assessment,
                "word_count": word_count,
                "score": length_score
            },
            "structure": {
                "score": structure_score,
                "paragraph_density": round(content_density, 2),
                "heading_frequency": round(heading_ratio, 2) if heading_count > 0 else 0
            },
            "sentiment": {
                "assessment": sentiment.get("interpretation", "neutral"),
                "score": round(sentiment_score, 2),
                "magnitude": round(sentiment_magnitude, 2)
            },
            "entity_analysis": {
                "count": entity_count,
                "density": round(entity_density, 2),
                "types": len(set(entity.get("type", "UNKNOWN") for entity in entities)),
                "avg_salience": round(sum(entity.get("salience", 0) for entity in entities) / max(1, len(entities)), 3)
            },
            "nlp_source": nlp_analysis.get("analysis_source", "unknown")
        }
    
    def _analyze_seo_enhanced(self, content: Dict[str, Any], nlp_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced SEO analysis incorporating NLP insights.
        
        Args:
            content: Scraped content dictionary
            nlp_analysis: NLP analysis dictionary
            
        Returns:
            Dictionary containing enhanced SEO analysis
        """
        # Get basic SEO analysis
        basic_seo = self._analyze_seo_basic(content)
        
        # Enhance with NLP insights
        entities = nlp_analysis.get("entities", [])
        sentiment = nlp_analysis.get("sentiment", {})
        
        # Entity-based SEO scoring
        entity_seo_score = 0
        if entities:
            # Check for location entities (good for local SEO)
            location_entities = [e for e in entities if e.get("type") == "LOCATION"]
            if location_entities:
                entity_seo_score += 10
            
            # Check for organization entities (good for authority)
            org_entities = [e for e in entities if e.get("type") == "ORGANIZATION"]
            if org_entities:
                entity_seo_score += 10
            
            # Check for person entities (good for E-A-T)
            person_entities = [e for e in entities if e.get("type") == "PERSON"]
            if person_entities:
                entity_seo_score += 10
        
        # Sentiment-based SEO scoring
        sentiment_seo_score = 0
        sentiment_score = sentiment.get("score", 0)
        if -0.1 <= sentiment_score <= 0.4:  # Neutral to positive is good for most content
            sentiment_seo_score = 10
        elif -0.3 <= sentiment_score <= 0.6:
            sentiment_seo_score = 5
        
        # Calculate enhanced SEO score
        enhanced_score = basic_seo["overall_score"] + entity_seo_score + sentiment_seo_score
        enhanced_score = min(100, enhanced_score)
        
        # Add NLP-based recommendations
        nlp_recommendations = []
        if len(entities) < 3:
            nlp_recommendations.append("Add more relevant entities (people, places, organizations)")
        
        if sentiment_score < -0.3:
            nlp_recommendations.append("Consider adjusting tone to be more neutral or positive")
        
        if not any(e.get("type") == "PERSON" for e in entities):
            nlp_recommendations.append("Consider mentioning relevant experts or authors for E-A-T")
        
        return {
            **basic_seo,
            "overall_score": enhanced_score,
            "entity_analysis": {
                "total_entities": len(entities),
                "location_entities": len([e for e in entities if e.get("type") == "LOCATION"]),
                "organization_entities": len([e for e in entities if e.get("type") == "ORGANIZATION"]),
                "person_entities": len([e for e in entities if e.get("type") == "PERSON"]),
                "entity_score": entity_seo_score
            },
            "sentiment_analysis": {
                "score": sentiment_score,
                "interpretation": sentiment.get("interpretation", "neutral"),
                "seo_impact": sentiment_seo_score
            },
            "nlp_recommendations": nlp_recommendations,
            "analysis_source": nlp_analysis.get("analysis_source", "unknown")
        }
    
    def _analyze_seo_basic(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic SEO analysis (maintained for compatibility).
        
        Args:
            content: Scraped content dictionary
            
        Returns:
            Dictionary containing basic SEO analysis
        """
        # Extract relevant data
        title = content["title"]
        description = content["description"]
        headings = content["headings"]
        url = content["url"]
        
        # Analyze title
        title_length = len(title)
        title_score = 0
        title_issues = []
        
        if 40 <= title_length <= 60:
            title_score = 5
        elif 30 <= title_length < 40 or 60 < title_length <= 70:
            title_score = 4
        elif 20 <= title_length < 30 or 70 < title_length <= 80:
            title_score = 3
        elif 10 <= title_length < 20 or 80 < title_length <= 100:
            title_score = 2
            title_issues.append(f"Title length ({title_length} characters) is not optimal")
        else:
            title_score = 1
            title_issues.append(f"Title length ({title_length} characters) is problematic")
        
        # Analyze meta description
        description_length = len(description)
        description_score = 0
        description_issues = []
        
        if 120 <= description_length <= 160:
            description_score = 5
        elif 100 <= description_length < 120 or 160 < description_length <= 180:
            description_score = 4
        elif 80 <= description_length < 100 or 180 < description_length <= 200:
            description_score = 3
        elif 50 <= description_length < 80 or 200 < description_length <= 250:
            description_score = 2
            description_issues.append(f"Description length ({description_length} characters) is not optimal")
        else:
            description_score = 1
            if description_length == 0:
                description_issues.append("Meta description is missing")
            else:
                description_issues.append(f"Description length ({description_length} characters) is problematic")
        
        # Analyze headings
        heading_score = 0
        heading_issues = []
        
        has_h1 = any(h["level"] == "h1" for h in headings)
        
        if has_h1:
            heading_score += 2
        else:
            heading_issues.append("No H1 heading found")
        
        if len(headings) >= 3:
            heading_score += 3
        elif len(headings) >= 2:
            heading_score += 2
        elif len(headings) == 1:
            heading_score += 1
        
        heading_score = min(5, heading_score)
        
        # Analyze URL
        url_score = 0
        url_issues = []
        
        path = urlparse(url).path
        path_length = len(path)
        
        if 20 <= path_length <= 60:
            url_score += 2
        elif path_length < 100:
            url_score += 1
        else:
            url_issues.append(f"URL path is too long ({path_length} characters)")
        
        if not re.search(r'[A-Z]', path):
            url_score += 1
        else:
            url_issues.append("URL contains uppercase letters")
        
        url_score = min(5, url_score)
        
        # Calculate basic SEO score
        seo_score = (title_score * 3) + (description_score * 3) + (heading_score * 2) + (url_score * 2)
        seo_score = min(100, max(1, seo_score * 10))
        
        return {
            "overall_score": seo_score,
            "title": {
                "score": title_score,
                "length": title_length,
                "issues": title_issues
            },
            "description": {
                "score": description_score,
                "length": description_length,
                "issues": description_issues
            },
            "headings": {
                "score": heading_score,
                "count": len(headings),
                "has_h1": has_h1,
                "issues": heading_issues
            },
            "url": {
                "score": url_score,
                "length": path_length,
                "issues": url_issues
            }
        }
    
    def _generate_recommendations_enhanced(self, content: Dict[str, Any], nlp_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate enhanced content improvement recommendations using NLP and AI insights.
        
        Args:
            content: Scraped content dictionary
            nlp_analysis: NLP analysis dictionary
            ai_analysis: AI analysis dictionary
            
        Returns:
            List of enhanced recommendation dictionaries
        """
        recommendations = []
        
        # Basic content recommendations
        word_count = content["word_count"]
        if word_count < 600:
            recommendations.append({
                "type": "content_length",
                "priority": "high",
                "recommendation": f"Increase content length to at least 600 words (current: {word_count}). Longer content tends to perform better in search results."
            })
        
        # Entity-based recommendations
        entities = nlp_analysis.get("entities", [])
        if len(entities) < 5:
            recommendations.append({
                "type": "entity_optimization",
                "priority": "medium",
                "recommendation": f"Add more relevant entities (current: {len(entities)}). Include people, places, organizations, and concepts related to your topic."
            })
        
        # Entity type diversity recommendations
        entity_types = set(entity.get("type", "UNKNOWN") for entity in entities)
        if "PERSON" not in entity_types:
            recommendations.append({
                "type": "entity_diversity",
                "priority": "medium",
                "recommendation": "Consider mentioning relevant experts, authors, or industry leaders to improve E-A-T signals."
            })
        
        if "ORGANIZATION" not in entity_types:
            recommendations.append({
                "type": "entity_diversity",
                "priority": "medium",
                "recommendation": "Reference relevant organizations, companies, or institutions to add authority."
            })
        
        # Sentiment-based recommendations
        sentiment = nlp_analysis.get("sentiment", {})
        sentiment_score = sentiment.get("score", 0)
        if sentiment_score < -0.2:
            recommendations.append({
                "type": "sentiment_optimization",
                "priority": "medium",
                "recommendation": "Consider adjusting the tone to be more neutral or positive, as negative sentiment may impact user engagement."
            })
        
        # AI-powered recommendations
        ai_readiness = ai_analysis.get("ai_readiness_score", 0)
        if ai_readiness < 0.7:
            recommendations.append({
                "type": "ai_optimization",
                "priority": "high",
                "recommendation": f"Improve AI readiness (current score: {ai_readiness:.2f}). Structure content for better AI understanding and featured snippet potential."
            })
        
        # Schema markup recommendations
        schema_suggestions = ai_analysis.get("schema_suggestions", {})
        if schema_suggestions and not schema_suggestions.get("note"):  # Real suggestions available
            recommendations.append({
                "type": "schema_markup",
                "priority": "medium",
                "recommendation": "Implement structured data markup to improve search appearance and enable rich results."
            })
        
        # Structure recommendations
        headings = content["headings"]
        if not headings:
            recommendations.append({
                "type": "structure",
                "priority": "high",
                "recommendation": "Add clear headings (H1, H2, H3) to improve content structure and readability."
            })
        elif len(headings) < 3 and word_count > 800:
            recommendations.append({
                "type": "structure",
                "priority": "medium",
                "recommendation": "Add more subheadings to break up long content sections and improve scannability."
            })
        
        # Media recommendations
        images = content["images"]
        if not images and word_count > 500:
            recommendations.append({
                "type": "media",
                "priority": "medium",
                "recommendation": "Add relevant images to enhance user engagement and visual appeal."
            })
        
        # Link recommendations
        external_links = content["links"]["external"]
        internal_links = content["links"]["internal"]
        
        if len(external_links) == 0:
            recommendations.append({
                "type": "external_links",
                "priority": "medium",
                "recommendation": "Add external links to authoritative sources to improve credibility and provide additional value to readers."
            })
        
        if len(internal_links) == 0:
            recommendations.append({
                "type": "internal_links",
                "priority": "medium",
                "recommendation": "Add internal links to related content on your site to improve navigation and SEO."
            })
        
        # Advanced AI-powered recommendations
        ai_overview_optimization = ai_analysis.get("ai_overview_optimization", {})
        if ai_overview_optimization and not ai_overview_optimization.get("note"):
            recommendations.append({
                "type": "ai_overview",
                "priority": "high",
                "recommendation": "Optimize content structure for Google AI Overviews to increase visibility in AI-powered search results."
            })
        
        # Content quality recommendations based on NLP analysis
        if nlp_analysis.get("analysis_source") == "google_natural_language":
            # Advanced recommendations only available with Google Natural Language API
            if len(entities) > 0:
                avg_salience = sum(entity.get("salience", 0) for entity in entities) / len(entities)
                if avg_salience < 0.1:
                    recommendations.append({
                        "type": "entity_prominence",
                        "priority": "medium",
                        "recommendation": "Increase the prominence of key entities in your content to improve topical relevance."
                    })
        
        return recommendations
    
    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze content quality using Google Natural Language API.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Content quality analysis
        """
        if self.nl_available:
            try:
                return self.natural_language_client.analyze_content_quality(content)
            except Exception as e:
                logger.warning(f"Google Natural Language API content quality analysis failed: {e}")
        
        # Fallback to basic analysis
        return self._basic_content_quality_analysis(content)
    
    def suggest_content_improvements(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Suggest content improvements using Google Natural Language API.
        
        Args:
            content: Text content to analyze
            target_keywords: Keywords to optimize for
            
        Returns:
            Content improvement suggestions
        """
        if self.nl_available:
            try:
                return self.natural_language_client.suggest_content_improvements(content, target_keywords)
            except Exception as e:
                logger.warning(f"Google Natural Language API content improvement suggestions failed: {e}")
        
        # Fallback to basic suggestions
        return self._basic_content_improvements(content, target_keywords)
    
    def analyze_ai_readiness(self, content: str) -> Dict[str, Any]:
        """
        Analyze content readiness for AI-powered search features.
        
        Args:
            content: Text content to analyze
            
        Returns:
            AI readiness analysis
        """
        if self.gemini_available:
            try:
                return self.gemini_client.analyze_ai_readiness(content)
            except Exception as e:
                logger.warning(f"Gemini AI readiness analysis failed: {e}")
        
        # Fallback to basic AI readiness assessment
        return self._basic_ai_readiness_analysis(content)
    
    def _basic_content_quality_analysis(self, content: str) -> Dict[str, Any]:
        """
        Basic content quality analysis fallback.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Basic content quality analysis
        """
        word_count = len(content.split())
        
        # Basic quality scoring
        quality_score = 0.5  # Base score
        
        if word_count >= 300:
            quality_score += 0.2
        if word_count >= 600:
            quality_score += 0.1
        if word_count >= 1000:
            quality_score += 0.1
        
        # Check for basic structure indicators
        if content.count('\n') >= 3:  # Some paragraph breaks
            quality_score += 0.1
        
        return {
            "quality_score": quality_score,
            "quality_level": "good" if quality_score >= 0.7 else "fair" if quality_score >= 0.5 else "needs_improvement",
            "content_metrics": {
                "word_count": word_count,
                "estimated_reading_time": round(word_count / 200, 1)  # Assuming 200 words per minute
            },
            "recommendations": ["Configure Google Natural Language API for detailed content quality analysis"],
            "note": "Basic analysis - Configure Google Natural Language API for comprehensive insights"
        }
    
    def _basic_content_improvements(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Basic content improvement suggestions fallback.
        
        Args:
            content: Text content to analyze
            target_keywords: Keywords to optimize for
            
        Returns:
            Basic improvement suggestions
        """
        word_count = len(content.split())
        
        suggestions = {
            "content_optimization": [],
            "keyword_optimization": [],
            "structure_improvements": []
        }
        
        # Basic content suggestions
        if word_count < 300:
            suggestions["content_optimization"].append({
                "type": "length",
                "suggestion": "Expand content to at least 300 words",
                "priority": "high"
            })
        
        # Keyword suggestions
        if target_keywords:
            content_lower = content.lower()
            for keyword in target_keywords:
                if keyword.lower() not in content_lower:
                    suggestions["keyword_optimization"].append({
                        "type": "missing_keyword",
                        "suggestion": f"Consider including the keyword '{keyword}' in the content",
                        "keyword": keyword,
                        "priority": "medium"
                    })
        
        # Basic structure suggestions
        if content.count('\n') < 3:
            suggestions["structure_improvements"].append({
                "type": "paragraphs",
                "suggestion": "Break content into more paragraphs for better readability",
                "priority": "medium"
            })
        
        return {
            "overall_quality": "fair",
            "quality_score": 0.6,
            "suggestions": suggestions,
            "total_suggestions": sum(len(cat) for cat in suggestions.values()),
            "note": "Basic analysis - Configure Google Natural Language API for comprehensive insights"
        }
    
    def _basic_ai_readiness_analysis(self, content: str) -> Dict[str, Any]:
        """
        Basic AI readiness analysis fallback.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Basic AI readiness analysis
        """
        word_count = len(content.split())
        
        # Basic scoring based on content length and structure
        ai_readiness = 0.5  # Base score
        
        if word_count >= 300:
            ai_readiness += 0.1
        if word_count >= 600:
            ai_readiness += 0.1
        
        # Check for question-like patterns (good for AI)
        if '?' in content:
            ai_readiness += 0.05
        
        # Check for structured content indicators
        if content.count('\n') >= 3:
            ai_readiness += 0.05
        
        return {
            "overall_ai_readiness": ai_readiness,
            "category_scores": {
                "ai_overviews": ai_readiness + 0.1,
                "featured_snippets": ai_readiness + 0.05,
                "voice_search": ai_readiness,
                "knowledge_panels": ai_readiness - 0.1
            },
            "analysis": "Basic AI readiness assessment based on content structure and length.",
            "improvement_areas": ["Content structure", "Entity optimization", "Answer formatting"],
            "note": "Basic analysis - Configure Gemini API for comprehensive AI readiness analysis"
        }
    
    def get_client_status(self) -> Dict[str, Any]:
        """
        Get the status of all clients.
        
        Returns:
            Dictionary containing client status information
        """
        return {
            "natural_language_api": {
                "available": self.nl_available,
                "status": "active" if self.nl_available else "unavailable",
                "description": "Google Natural Language API for advanced NLP analysis"
            },
            "gemini_api": {
                "available": self.gemini_available,
                "status": "active" if self.gemini_available else "unavailable",
                "description": "Google Gemini API for AI-powered content insights"
            },
            "gemini_nlp": {
                "available": self.gemini_nlp_available,
                "status": "active" if self.gemini_nlp_available else "unavailable",
                "description": "Gemini NLP client for basic content analysis"
            },
            "phase_completion": {
                "phase_2_2": "completed",
                "description": "Content Analyzer successfully updated with Google Natural Language API integration",
                "features": [
                    "Google Natural Language API integration",
                    "Enhanced entity analysis",
                    "Advanced sentiment analysis",
                    "AI-powered content optimization",
                    "Intelligent fallback mechanisms",
                    "Content quality assessment",
                    "SEO optimization recommendations"
                ]
            }
        }