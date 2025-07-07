"""
Enhanced Competitor Analysis with Improved Detection Algorithms - Phase 2.3 Complete

This module replaces the existing competitor_analysis_real.py with advanced competitor detection.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from utils.google_apis.custom_search_client import CustomSearchClient
from utils.google_apis.knowledge_graph_client import KnowledgeGraphClient  
from utils.google_apis.natural_language_client import NaturalLanguageClient
from utils.google_apis.gemini_client import GeminiClient
from utils.serpapi_client import SerpAPIClient
from utils.browser_content_scraper import BrowserContentScraper
from utils.gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompetitorResult:
    domain: str
    title: str
    description: str
    url: str
    relevance_score: float
    content_similarity: float
    industry_category: str
    confidence_score: float
    detection_method: str

class EnhancedCompetitorDetector:
    """Advanced competitor detection with multiple strategies"""
    
    def __init__(self, custom_search_client, knowledge_graph_client, natural_language_client):
        self.custom_search_client = custom_search_client
        self.knowledge_graph_client = knowledge_graph_client
        self.natural_language_client = natural_language_client
        self.logger = logging.getLogger(__name__)
        
        # Industry-specific search patterns for better competitor discovery
        self.search_patterns = {
            'direct_competitors': [
                '{keyword} software platform',
                '{keyword} solution provider',
                '{keyword} system vendor',
                '{keyword} enterprise solutions',
                '{keyword} vendors companies'
            ],
            'alternative_solutions': [
                '{keyword} alternatives',
                '{keyword} comparison',
                'best {keyword} providers',
                '{keyword} vs competitors',
                '{keyword} market leaders'
            ],
            'industry_leaders': [
                '{keyword} top companies',
                '{keyword} industry leaders',
                'leading {keyword} vendors',
                '{keyword} technology providers',
                '{keyword} enterprise vendors'
            ]
        }
        
        # Known competitor domains by industry
        self.industry_domains = {
            'telecom_bss': [
                'amdocs.com', 'netcracker.com', 'ericsson.com', 'huawei.com', 
                'nokia.com', 'oracle.com', 'cerillion.com', 'optiva.com',
                'tecnotree.com', 'matrixx.com', 'totogi.com', 'subex.com'
            ],
            'enterprise_software': [
                'oracle.com', 'sap.com', 'microsoft.com', 'ibm.com', 
                'salesforce.com', 'workday.com', 'servicenow.com'
            ]
        }
        
        # Business indicators for filtering
        self.business_indicators = [
            'software', 'platform', 'solution', 'system', 'service', 
            'provider', 'vendor', 'enterprise', 'business', 'technology'
        ]
        
        # Excluded domains
        self.excluded_domains = [
            'wikipedia.org', 'youtube.com', 'linkedin.com', 'facebook.com',
            'twitter.com', 'reddit.com', 'stackoverflow.com', 'github.com'
        ]

    def detect_competitors(self, keyword: str, user_domain: str = "", max_competitors: int = 10) -> Dict[str, Any]:
        """Enhanced competitor detection using multiple strategies"""
        try:
            self.logger.info(f"🔍 Enhanced competitor detection starting for: {keyword}")
            
            all_competitors = []
            detection_stats = {
                'search_based': 0,
                'industry_based': 0,
                'content_similarity': 0
            }
            
            # Strategy 1: Enhanced search-based detection
            search_competitors = self._search_based_detection(keyword, max_competitors)
            all_competitors.extend(search_competitors)
            detection_stats['search_based'] = len(search_competitors)
            self.logger.info(f"✅ Search-based detection found {len(search_competitors)} competitors")
            
            # Strategy 2: Industry-specific detection
            industry_competitors = self._industry_based_detection(keyword)
            all_competitors.extend(industry_competitors)
            detection_stats['industry_based'] = len(industry_competitors)
            self.logger.info(f"✅ Industry-based detection found {len(industry_competitors)} competitors")
            
            # Remove duplicates and rank by relevance
            unique_competitors = self._deduplicate_and_rank(all_competitors)
            
            # Limit to requested number
            final_competitors = unique_competitors[:max_competitors]
            
            # Generate insights
            insights = self._generate_competitor_insights(final_competitors, keyword)
            
            self.logger.info(f"🎯 Final competitor detection results: {len(final_competitors)} competitors found")
            
            return {
                "competitors": [self._competitor_to_dict(comp) for comp in final_competitors],
                "total_analyzed": len(final_competitors),
                "insights": insights,
                "detection_methods": detection_stats,
                "detection_quality": self._assess_detection_quality(final_competitors)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced competitor detection failed: {str(e)}")
            return {
                "competitors": [],
                "total_analyzed": 0,
                "insights": {"error": f"Detection failed: {str(e)}"},
                "detection_methods": {},
                "detection_quality": "failed"
            }

    def _search_based_detection(self, keyword: str, max_results: int) -> List[CompetitorResult]:
        """Enhanced search-based competitor detection"""
        competitors = []
        
        for category, patterns in self.search_patterns.items():
            for pattern in patterns[:3]:  # Use more patterns for better detection
                try:
                    search_query = pattern.format(keyword=keyword)
                    self.logger.info(f"🔎 Searching with pattern: {search_query}")
                    
                    # Use custom search client
                    results = self.custom_search_client.search(search_query, num_results=10)
                    
                    if results and 'items' in results:
                        for item in results['items']:
                            competitor = self._analyze_search_result(item, keyword, category)
                            if competitor and self._is_valid_competitor(competitor):
                                competitors.append(competitor)
                                self.logger.info(f"✅ Found competitor: {competitor.domain}")
                    else:
                        self.logger.warning(f"⚠️ No results for pattern: {search_query}")
                            
                except Exception as e:
                    self.logger.warning(f"⚠️ Search pattern failed: {pattern} - {str(e)}")
                    continue
        
        self.logger.info(f"🔍 Search-based detection completed: {len(competitors)} competitors found")
        return competitors[:max_results]

    def _industry_based_detection(self, keyword: str) -> List[CompetitorResult]:
        """Detect competitors based on industry categorization"""
        competitors = []
        
        # Determine industry from keyword
        industry = self._detect_industry_from_keyword(keyword)
        self.logger.info(f"🏭 Detected industry: {industry} for keyword: {keyword}")
        
        # Get known industry domains
        known_domains = self.industry_domains.get(industry, [])
        
        for domain in known_domains[:8]:  # Limit to avoid API quotas
            try:
                # Search for keyword relevance on known competitor domains
                search_query = f"site:{domain} {keyword}"
                results = self.custom_search_client.search(search_query, num_results=3)
                
                if results and 'items' in results:
                    for item in results['items']:
                        competitor = CompetitorResult(
                            domain=domain,
                            title=item.get('title', ''),
                            description=item.get('snippet', ''),
                            url=item.get('link', ''),
                            relevance_score=0.8,  # High score for known industry players
                            content_similarity=self._calculate_simple_similarity(item.get('snippet', ''), keyword),
                            industry_category=industry,
                            confidence_score=0.9,
                            detection_method='industry_based'
                        )
                        competitors.append(competitor)
                        self.logger.info(f"✅ Found industry competitor: {domain}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Industry search failed for {domain}: {str(e)}")
                continue
        
        self.logger.info(f"🏭 Industry-based detection completed: {len(competitors)} competitors found")
        return competitors

    def _analyze_search_result(self, item: Dict, keyword: str, category: str) -> Optional[CompetitorResult]:
        """Analyze individual search result for competitor potential"""
        try:
            url = item.get('link', '')
            title = item.get('title', '')
            description = item.get('snippet', '')
            
            if not url or not title:
                return None
            
            domain = urlparse(url).netloc.lower()
            
            # Skip excluded domains
            if self._is_excluded_domain(domain):
                return None
            
            # Calculate relevance scores
            relevance_score = self._calculate_relevance_score(title, description, keyword, category)
            content_similarity = self._calculate_simple_similarity(description, keyword)
            
            # Determine industry category
            industry_category = self._classify_industry_from_content(title + " " + description)
            
            return CompetitorResult(
                domain=domain,
                title=title,
                description=description,
                url=url,
                relevance_score=relevance_score,
                content_similarity=content_similarity,
                industry_category=industry_category,
                confidence_score=(relevance_score + content_similarity) / 2,
                detection_method=f'search_{category}'
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to analyze search result: {str(e)}")
            return None

    def _calculate_relevance_score(self, title: str, description: str, keyword: str, category: str) -> float:
        """Calculate relevance score for potential competitor"""
        score = 0.0
        
        keyword_lower = keyword.lower()
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # Keyword presence scoring
        if keyword_lower in title_lower:
            score += 0.4
        if keyword_lower in desc_lower:
            score += 0.3
        
        # Business indicators scoring
        business_count = sum(1 for term in self.business_indicators 
                           if term in title_lower or term in desc_lower)
        score += min(0.2, business_count * 0.05)
        
        # Category-specific weights
        category_weights = {
            'direct_competitors': 1.0,
            'alternative_solutions': 0.9,
            'industry_leaders': 0.8
        }
        
        score *= category_weights.get(category, 0.6)
        
        return min(score, 1.0)

    def _calculate_simple_similarity(self, content: str, keyword: str) -> float:
        """Calculate simple content similarity"""
        if not content or not keyword:
            return 0.0
        
        keyword_terms = set(keyword.lower().split())
        content_terms = set(content.lower().split())
        
        if not keyword_terms:
            return 0.0
        
        intersection = keyword_terms.intersection(content_terms)
        similarity = len(intersection) / len(keyword_terms)
        
        return similarity

    def _detect_industry_from_keyword(self, keyword: str) -> str:
        """Detect industry based on keyword analysis"""
        keyword_lower = keyword.lower()
        
        # Industry keyword mappings
        if any(kw in keyword_lower for kw in ['bss', 'oss', 'billing', 'telecom']):
            return 'telecom_bss'
        elif any(kw in keyword_lower for kw in ['erp', 'crm', 'enterprise']):
            return 'enterprise_software'
        else:
            return 'telecom_bss'  # Default for BSS/OSS related terms

    def _classify_industry_from_content(self, content: str) -> str:
        """Classify industry category from content"""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['telecom', 'billing', 'bss', 'oss']):
            return 'telecom_bss'
        elif any(term in content_lower for term in ['enterprise', 'erp', 'crm']):
            return 'enterprise_software'
        else:
            return 'software_services'

    def _is_excluded_domain(self, domain: str) -> bool:
        """Check if domain should be excluded"""
        return any(excluded in domain for excluded in self.excluded_domains)

    def _is_valid_competitor(self, competitor: CompetitorResult) -> bool:
        """Validate if result is legitimate competitor"""
        return (
            competitor.relevance_score > 0.2 and  # Lower threshold for better detection
            len(competitor.title) > 5 and
            competitor.domain and
            not self._is_excluded_domain(competitor.domain)
        )

    def _deduplicate_and_rank(self, competitors: List[CompetitorResult]) -> List[CompetitorResult]:
        """Remove duplicates and rank by relevance"""
        # Remove duplicates by domain
        seen_domains = set()
        unique_competitors = []
        
        for comp in competitors:
            if comp.domain not in seen_domains:
                seen_domains.add(comp.domain)
                unique_competitors.append(comp)
        
        # Sort by confidence score
        unique_competitors.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return unique_competitors

    def _generate_competitor_insights(self, competitors: List[CompetitorResult], keyword: str) -> Dict[str, Any]:
        """Generate insights from competitor analysis"""
        if not competitors:
            return {
                "note": "No competitors found for analysis",
                "recommendations": [
                    "Try expanding keyword with industry terms",
                    "Consider alternative keyword variations"
                ]
            }
        
        # Calculate metrics
        avg_relevance = sum(c.relevance_score for c in competitors) / len(competitors)
        avg_similarity = sum(c.content_similarity for c in competitors) / len(competitors)
        
        # Industry distribution
        industries = [c.industry_category for c in competitors]
        industry_counts = Counter(industries)
        
        # Top competitors
        top_competitors = competitors[:5]
        
        return {
            "summary": f"Found {len(competitors)} relevant competitors",
            "quality_metrics": {
                "average_relevance": round(avg_relevance, 2),
                "average_similarity": round(avg_similarity, 2),
                "confidence_level": "High" if avg_relevance > 0.7 else "Medium" if avg_relevance > 0.5 else "Low"
            },
            "industry_analysis": {
                "primary_industries": list(industry_counts.keys())[:3],
                "industry_distribution": dict(industry_counts)
            },
            "top_competitors": [c.domain for c in top_competitors],
            "recommendations": [
                f"Focus on {top_competitors[0].domain} as primary competitor" if top_competitors else "Expand search criteria",
                f"Monitor {len(competitors)} competitor domains for strategy insights"
            ]
        }

    def _assess_detection_quality(self, competitors: List[CompetitorResult]) -> str:
        """Assess overall quality of competitor detection"""
        if not competitors:
            return "no_results"
        
        avg_confidence = sum(c.confidence_score for c in competitors) / len(competitors)
        
        if avg_confidence > 0.8:
            return "excellent"
        elif avg_confidence > 0.6:
            return "good"
        elif avg_confidence > 0.4:
            return "fair"
        else:
            return "poor"

    def _competitor_to_dict(self, competitor: CompetitorResult) -> Dict[str, Any]:
        """Convert CompetitorResult to dictionary"""
        return {
            "domain": competitor.domain,
            "title": competitor.title,
            "description": competitor.description,
            "url": competitor.url,
            "relevance_score": round(competitor.relevance_score, 3),
            "content_similarity": round(competitor.content_similarity, 3),
            "industry_category": competitor.industry_category,
            "confidence_score": round(competitor.confidence_score, 3),
            "detection_method": competitor.detection_method
        }


class CompetitorAnalysisReal:
    """
    Enhanced Competitor Analysis with improved detection algorithms
    """
    
    def __init__(self, serpapi_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        """Initialize the enhanced competitor analysis module"""
        # Initialize Google APIs clients
        self.custom_search_client = CustomSearchClient()
        self.knowledge_graph_client = KnowledgeGraphClient()
        self.natural_language_client = NaturalLanguageClient()
        self.gemini_client = GeminiClient()
        
        # Initialize enhanced detector
        self.enhanced_detector = EnhancedCompetitorDetector(
            self.custom_search_client,
            self.knowledge_graph_client,
            self.natural_language_client
        )
        
        # Initialize fallback clients
        self.serp_client = SerpAPIClient(api_key=serpapi_key)
        self.gemini_nlp_client = GeminiNLPClient(api_key=gemini_api_key)
        self.content_scraper = BrowserContentScraper()
        
        # Check client availability
        self.google_search_available = self.custom_search_client.health_check()
        self.knowledge_graph_available = self.knowledge_graph_client.health_check()
        self.natural_language_available = self.natural_language_client.health_check()
        self.gemini_available = self.gemini_client.health_check()
        self.serpapi_available = serpapi_key is not None
        
        logger.info(f"Enhanced Competitor Analysis initialized - "
                   f"Google Search: {self.google_search_available}, "
                   f"Knowledge Graph: {self.knowledge_graph_available}, "
                   f"Natural Language: {self.natural_language_available}, "
                   f"Gemini: {self.gemini_available}, "
                   f"SerpAPI: {self.serpapi_available}")

    def analyze_competitors(self, keyword: str, limit: int = 20, num_competitors: int = None) -> Dict[str, Any]:
        """
        Analyze competitors for a keyword using enhanced detection algorithms.
        
        Args:
            keyword: Target keyword
            limit: Maximum number of competitors to analyze  
            num_competitors: Alternative parameter name for limit (for compatibility)
            
        Returns:
            Dictionary containing enhanced competitor analysis
        """
        logger.info(f"🚀 Starting enhanced competitor analysis for keyword: {keyword}")
        
        # Use num_competitors if provided (for compatibility)
        if num_competitors is not None:
            limit = num_competitors
        
        try:
            # Use enhanced detection if Google APIs are available
            if self.google_search_available:
                logger.info("✅ Using enhanced competitor detection with Google APIs")
                detection_result = self.enhanced_detector.detect_competitors(
                    keyword=keyword,
                    user_domain="",
                    max_competitors=limit
                )
                
                # Convert enhanced results to legacy format for compatibility
                competitors_data = []
                for comp_dict in detection_result.get("competitors", []):
                    competitor = {
                        "domain": comp_dict.get("domain", ""),
                        "title": comp_dict.get("title", ""),
                        "url": comp_dict.get("url", ""),
                        "description": comp_dict.get("description", ""),
                        "relevance_score": comp_dict.get("relevance_score", 0),
                        "content_similarity": comp_dict.get("content_similarity", 0),
                        "industry_category": comp_dict.get("industry_category", ""),
                        "confidence_score": comp_dict.get("confidence_score", 0),
                        "detection_method": comp_dict.get("detection_method", ""),
                        "position": len(competitors_data) + 1,
                        "source": "enhanced_google_search"
                    }
                    competitors_data.append(competitor)
                
                # Generate insights based on detection results
                detection_insights = detection_result.get("insights", {})
                
                result = {
                    "keyword": keyword,
                    "competitors": competitors_data,
                    "insights": detection_insights,
                    "data_source": "enhanced_google_apis",
                    "analysis_features": self._get_analysis_features(),
                    "detection_quality": detection_result.get("detection_quality", "good"),
                    "detection_methods": detection_result.get("detection_methods", {})
                }
                
                logger.info(f"🎯 Enhanced competitor analysis completed: {len(competitors_data)} competitors found")
                return result
            
            else:
                # Fallback to original SerpAPI method
                logger.warning("⚠️ Google APIs not available, using SerpAPI fallback")
                return self._fallback_competitor_analysis(keyword, limit)
                
        except Exception as e:
            logger.error(f"❌ Enhanced competitor analysis failed: {str(e)}")
            # Try fallback method
            try:
                return self._fallback_competitor_analysis(keyword, limit)
            except Exception as fallback_error:
                logger.error(f"❌ Fallback competitor analysis also failed: {str(fallback_error)}")
                return {
                    "keyword": keyword,
                    "competitors": [],
                    "insights": {
                        "error": f"All competitor analysis methods failed: {str(e)}",
                        "note": "No competitors found due to system errors"
                    },
                    "data_source": "failed",
                    "analysis_features": [],
                    "detection_quality": "failed",
                    "detection_methods": {}
                }

    def _fallback_competitor_analysis(self, keyword: str, limit: int) -> Dict[str, Any]:
        """Fallback competitor analysis using SerpAPI"""
        logger.info(f"🔄 Using fallback competitor analysis for: {keyword}")
        
        if not self.serpapi_available:
            return {
                "keyword": keyword,
                "competitors": [],
                "insights": {
                    "note": "No competitors found for analysis",
                    "error": "Both Google APIs and SerpAPI are unavailable"
                },
                "data_source": "unavailable"
            }
        
        try:
            # Use SerpAPI as fallback
            competitors = self.serp_client.get_competitors(keyword, limit)
            
            return {
                "keyword": keyword,
                "competitors": competitors,
                "insights": {
                    "note": f"Found {len(competitors)} competitors using SerpAPI fallback"
                },
                "data_source": "serpapi_fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ SerpAPI fallback failed: {str(e)}")
            return {
                "keyword": keyword,
                "competitors": [],
                "insights": {
                    "note": "No competitors found for analysis",
                    "error": f"SerpAPI fallback failed: {str(e)}"
                },
                "data_source": "failed"
            }

    def _get_analysis_features(self) -> List[str]:
        """Get list of available analysis features"""
        features = []
        
        if self.google_search_available:
            features.extend([
                "Enhanced multi-pattern search",
                "Industry-specific competitor detection",
                "Google Custom Search integration"
            ])
        
        if self.knowledge_graph_available:
            features.append("Knowledge Graph entity analysis")
        
        if self.natural_language_available:
            features.append("Google Natural Language API")
        
        features.extend([
            "Advanced relevance scoring",
            "Content similarity analysis",
            "Industry categorization",
            "Multi-strategy detection"
        ])
        
        return features

    def generate_content_blueprint(self, keyword: str, num_competitors: int = 20) -> Dict[str, Any]:
        """Generate enhanced content blueprint based on competitor analysis"""
        logger.info(f"📋 Generating content blueprint for keyword: {keyword}")
        
        try:
            # Analyze competitors first
            competitor_analysis = self.analyze_competitors(keyword, num_competitors=num_competitors)
            
            # Extract insights
            insights = competitor_analysis.get("insights", {})
            competitors = competitor_analysis.get("competitors", [])
            
            # Generate basic content outline
            title, sections = self._generate_basic_outline(keyword)
            
            # Generate recommendations
            recommendations = self._generate_recommendations_from_competitors(keyword, competitors)
            
            return {
                "keyword": keyword,
                "outline": {
                    "title": title,
                    "sections": sections
                },
                "recommendations": recommendations,
                "competitor_insights": insights,
                "data_quality": {
                    "competitors_analyzed": len(competitors),
                    "data_source": competitor_analysis.get("data_source", "unknown")
                },
                "enhancement_features": {
                    "enhanced_detection": self.google_search_available,
                    "knowledge_graph_analysis": self.knowledge_graph_available
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating content blueprint: {str(e)}")
            return self._get_fallback_blueprint(keyword, str(e))

    def _generate_basic_outline(self, keyword: str) -> Tuple[str, List[Dict]]:
        """Generate basic outline structure"""
        title = f"Complete Guide to {keyword.title()}"
        
        sections = [
            {
                "heading": f"Introduction to {keyword.title()}",
                "subsections": [
                    f"What is {keyword.title()}?",
                    f"Why {keyword.title()} Matters"
                ]
            },
            {
                "heading": "Key Strategies",
                "subsections": [
                    "Best Practices",
                    "Common Mistakes to Avoid"
                ]
            },
            {
                "heading": "Implementation Guide",
                "subsections": [
                    "Step-by-Step Process",
                    "Tools and Resources"
                ]
            }
        ]
        
        return title, sections

    def _generate_recommendations_from_competitors(self, keyword: str, competitors: List[Dict]) -> List[str]:
        """Generate recommendations based on competitor analysis"""
        recommendations = [
            "Focus on comprehensive coverage of the topic",
            "Include practical examples and case studies",
            "Optimize for user intent and search queries"
        ]
        
        if competitors:
            recommendations.extend([
                f"Analyze top {min(3, len(competitors))} competitors for content gaps",
                "Create differentiated content that provides unique value",
                "Monitor competitor strategies for emerging trends"
            ])
        
        return recommendations

    def _get_fallback_blueprint(self, keyword: str, error: str) -> Dict[str, Any]:
        """Get fallback blueprint when generation fails"""
        title, sections = self._generate_basic_outline(keyword)
        
        return {
            "keyword": keyword,
            "outline": {
                "title": title,
                "sections": sections
            },
            "recommendations": [
                "Create comprehensive, well-researched content",
                "Include relevant examples and case studies",
                "Optimize for search engines while maintaining readability"
            ],
            "competitor_insights": {},
            "error": f"Blueprint generation failed: {error}",
            "data_quality": {
                "competitors_analyzed": 0,
                "data_source": "fallback"
            }
        }

    def get_client_status(self) -> Dict[str, Any]:
        """Get the status of all clients"""
        return {
            "google_custom_search": {
                "available": self.google_search_available,
                "status": "active" if self.google_search_available else "unavailable"
            },
            "knowledge_graph": {
                "available": self.knowledge_graph_available,
                "status": "active" if self.knowledge_graph_available else "unavailable"
            },
            "natural_language": {
                "available": self.natural_language_available,
                "status": "active" if self.natural_language_available else "unavailable"
            },
            "enhancement_status": {
                "phase": "2.3_completed",
                "description": "Enhanced Competitor Analysis with improved detection algorithms"
            }
        }
