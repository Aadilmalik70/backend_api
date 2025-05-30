"""
Real Search Intent Analyzer with Gemini Integration

This module provides search intent classification using real SERP features
and Gemini API for classification, following production-quality requirements.
"""

import logging
import json
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchIntentAnalyzer:
    """
    Real search intent analyzer using SERP features and Gemini API.
    
    This class provides methods for classifying search intent using real data sources
    instead of mock data, with Gemini API integration for classification.
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the search intent analyzer.
        
        Args:
            gemini_api_key: Gemini API key for content analysis
        """
        self.gemini_client = GeminiNLPClient(api_key=gemini_api_key)
    
    def classify_intent(self, keyword: str, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        REAL IMPLEMENTATION REQUIRED:
        - Analyze actual SERP features from real SerpAPI data
        - Use Gemini API for real intent classification
        - Calculate confidence based on real signal strength
        """
        
        # MUST: Extract real SERP signals
        real_signals = self._extract_real_serp_signals(serp_data)
        
        # MUST: Use real Gemini API call for classification
        intent_prompt = f"""
        Classify the search intent for: "{keyword}"
        
        Real SERP Analysis:
        - Ads present: {real_signals['ads_count']} ads found
        - Featured snippet: {'Yes' if real_signals['has_featured_snippet'] else 'No'}
        - People Also Ask: {real_signals['paa_count']} questions
        - Shopping results: {'Yes' if real_signals['has_shopping'] else 'No'}
        - Local pack: {'Yes' if real_signals['has_local'] else 'No'}
        - Top domains: {real_signals['top_domains']}
        
        Based on these REAL SERP features, classify intent percentages (must sum to 100):
        {{
            "informational": percentage,
            "commercial": percentage, 
            "transactional": percentage,
            "navigational": percentage,
            "primary_intent": "dominant_category",
            "confidence_score": score_0_to_100
        }}
        
        Return only valid JSON.
        """
        
        # MUST: Make real API call to Gemini
        try:
            response = self.gemini_client.generate_content(intent_prompt)
            classification = self._parse_real_intent_response(response)
            
            # MUST: Validate response is not mock data
            if self._is_valid_real_classification(classification):
                return {
                    **classification,
                    "serp_signals": real_signals,
                    "analysis_method": "real_gemini_api",
                    "data_source": "real_serp_features"
                }
            else:
                logger.error("Invalid classification response from Gemini")
                raise ValueError("Classification failed validation")
                
        except Exception as e:
            logger.error(f"Real intent classification failed: {str(e)}")
            # MUST: Return error, not mock data
            return {
                "error": f"Intent classification failed: {str(e)}",
                "serp_signals": real_signals,  
                "fallback_used": False  # No fallback mock data
            }
    
    def _extract_real_serp_signals(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract real signals from actual SERP data"""
        
        return {
            "ads_count": len(serp_data.get("ads", [])),
            "has_featured_snippet": bool(serp_data.get("featured_snippet")),
            "paa_count": len(serp_data.get("people_also_ask", [])),
            "has_shopping": bool(serp_data.get("shopping", [])),
            "has_local": bool(serp_data.get("local_results")),
            "organic_count": len(serp_data.get("organic_results", [])),
            "top_domains": [
                self._extract_domain(result.get("link", ""))
                for result in serp_data.get("organic_results", [])[:5]
            ],
            "total_results": serp_data.get("search_information", {}).get("total_results", 0)
        }
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name
        """
        try:
            return urlparse(url).netloc
        except:
            # Simple fallback
            if url.startswith("http"):
                parts = url.split("/")
                if len(parts) > 2:
                    return parts[2]
            return ""
    
    def _parse_real_intent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse real intent classification response from Gemini.
        
        Args:
            response: Raw response from Gemini API
            
        Returns:
            Parsed classification data
        """
        try:
            # Try to extract JSON from response
            response_clean = response.strip()
            
            # Handle cases where response is wrapped in code blocks
            if "```json" in response_clean:
                start_idx = response_clean.find("```json") + 7
                end_idx = response_clean.find("```", start_idx)
                response_clean = response_clean[start_idx:end_idx].strip()
            elif "```" in response_clean:
                start_idx = response_clean.find("```") + 3
                end_idx = response_clean.find("```", start_idx)
                response_clean = response_clean[start_idx:end_idx].strip()
            
            # Parse JSON
            classification = json.loads(response_clean)
            
            # Validate structure
            required_keys = ["informational", "commercial", "transactional", "navigational", "primary_intent", "confidence_score"]
            if all(key in classification for key in required_keys):
                return classification
            else:
                logger.error(f"Missing required keys in classification response: {classification}")
                raise ValueError("Incomplete classification response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            logger.error(f"Response was: {response}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing intent classification: {str(e)}")
            raise ValueError(f"Failed to parse classification: {str(e)}")
    
    def _is_valid_real_classification(self, classification: Dict[str, Any]) -> bool:
        """
        Validate that classification contains real data, not mock.
        
        Args:
            classification: Classification response to validate
            
        Returns:
            True if classification appears to be real data
        """
        try:
            # Check that percentages sum to approximately 100
            intent_sum = (
                classification.get("informational", 0) +
                classification.get("commercial", 0) +
                classification.get("transactional", 0) +
                classification.get("navigational", 0)
            )
            
            if not (95 <= intent_sum <= 105):  # Allow small rounding errors
                logger.error(f"Intent percentages don't sum to 100: {intent_sum}")
                return False
            
            # Check confidence score is reasonable
            confidence = classification.get("confidence_score", 0)
            if not (0 <= confidence <= 100):
                logger.error(f"Invalid confidence score: {confidence}")
                return False
            
            # Check primary intent is valid
            valid_intents = ["informational", "commercial", "transactional", "navigational"]
            primary_intent = classification.get("primary_intent", "")
            if primary_intent not in valid_intents:
                logger.error(f"Invalid primary intent: {primary_intent}")
                return False
            
            # Check that percentages are realistic (not all zeros or all 100)
            percentages = [
                classification.get("informational", 0),
                classification.get("commercial", 0),
                classification.get("transactional", 0),
                classification.get("navigational", 0)
            ]
            
            non_zero_count = sum(1 for p in percentages if p > 0)
            if non_zero_count == 0:
                logger.error("All intent percentages are zero")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating classification: {str(e)}")
            return False
    
    def analyze_intent_signals(self, keyword: str, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze search intent signals from SERP features.
        
        Args:
            keyword: Target keyword
            serp_data: Real SERP data from SerpAPI
            
        Returns:
            Dictionary containing intent signal analysis
        """
        signals = self._extract_real_serp_signals(serp_data)
        
        # Analyze commercial signals
        commercial_signals = {
            "high_ad_count": signals["ads_count"] >= 4,
            "has_shopping_results": signals["has_shopping"],
            "commercial_domains": self._count_commercial_domains(signals["top_domains"])
        }
        
        # Analyze informational signals
        informational_signals = {
            "has_featured_snippet": signals["has_featured_snippet"],
            "high_paa_count": signals["paa_count"] >= 3,
            "educational_domains": self._count_educational_domains(signals["top_domains"])
        }
        
        # Analyze transactional signals
        transactional_signals = {
            "has_shopping_results": signals["has_shopping"],
            "ecommerce_domains": self._count_ecommerce_domains(signals["top_domains"]),
            "high_commercial_intent": commercial_signals["high_ad_count"] and commercial_signals["has_shopping_results"]
        }
        
        # Analyze navigational signals
        navigational_signals = {
            "brand_domains": self._count_brand_domains(signals["top_domains"], keyword),
            "official_results": self._count_official_domains(signals["top_domains"])
        }
        
        return {
            "serp_signals": signals,
            "commercial_signals": commercial_signals,
            "informational_signals": informational_signals,
            "transactional_signals": transactional_signals,
            "navigational_signals": navigational_signals,
            "signal_strength": {
                "commercial": sum(commercial_signals.values()),
                "informational": sum(informational_signals.values()),
                "transactional": sum(transactional_signals.values()),
                "navigational": sum(navigational_signals.values())
            }
        }
    
    def _count_commercial_domains(self, domains: list) -> int:
        """Count domains that indicate commercial intent"""
        commercial_indicators = [
            "shop", "store", "buy", "price", "deal", "sale", "discount",
            "amazon", "ebay", "walmart", "target", "bestbuy"
        ]
        
        count = 0
        for domain in domains:
            if any(indicator in domain.lower() for indicator in commercial_indicators):
                count += 1
        return count
    
    def _count_educational_domains(self, domains: list) -> int:
        """Count domains that indicate informational intent"""
        educational_tlds = [".edu", ".org", ".gov"]
        educational_domains = [
            "wikipedia", "wikihow", "britannica", "khan", "coursera",
            "udemy", "edx", "mit", "stanford", "harvard"
        ]
        
        count = 0
        for domain in domains:
            domain_lower = domain.lower()
            if (any(tld in domain_lower for tld in educational_tlds) or
                any(edu_domain in domain_lower for edu_domain in educational_domains)):
                count += 1
        return count
    
    def _count_ecommerce_domains(self, domains: list) -> int:
        """Count domains that indicate transactional intent"""
        ecommerce_domains = [
            "amazon", "ebay", "etsy", "shopify", "woocommerce",
            "bigcommerce", "magento", "stripe", "paypal"
        ]
        
        count = 0
        for domain in domains:
            if any(ecom in domain.lower() for ecom in ecommerce_domains):
                count += 1
        return count
    
    def _count_brand_domains(self, domains: list, keyword: str) -> int:
        """Count domains that match the keyword (navigational intent)"""
        keyword_parts = keyword.lower().split()
        count = 0
        
        for domain in domains:
            domain_lower = domain.lower()
            if any(part in domain_lower for part in keyword_parts if len(part) > 2):
                count += 1
        return count
    
    def _count_official_domains(self, domains: list) -> int:
        """Count official/authoritative domains"""
        official_tlds = [".gov", ".edu", ".org"]
        official_indicators = ["official", "www", "support", "help", "docs"]
        
        count = 0
        for domain in domains:
            domain_lower = domain.lower()
            if (any(tld in domain_lower for tld in official_tlds) or
                any(indicator in domain_lower for indicator in official_indicators)):
                count += 1
        return count
    
    def get_intent_recommendations(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Get content recommendations based on intent classification"""
        
        if "error" in classification:
            return {
                "error": "Cannot provide recommendations due to classification error",
                "fallback_recommendations": [
                    "Create comprehensive, informational content as fallback",
                    "Include clear value propositions for commercial elements",
                    "Ensure content addresses user questions and concerns"
                ]
            }
        
        primary_intent = classification.get("primary_intent", "informational")
        confidence = classification.get("confidence_score", 0)
        
        recommendations = {
            "primary_strategy": self._get_primary_strategy(primary_intent),
            "content_focus": self._get_content_focus(classification),
            "optimization_tactics": self._get_optimization_tactics(classification),
            "confidence_level": "high" if confidence >= 80 else ("medium" if confidence >= 60 else "low")
        }
        
        return recommendations
    
    def _get_primary_strategy(self, primary_intent: str) -> Dict[str, Any]:
        """Get primary strategy based on intent"""
        strategies = {
            "informational": {
                "focus": "Educational and comprehensive content",
                "content_type": "Guides, tutorials, explanations",
                "cta_type": "Learn more, subscribe, share"
            },
            "commercial": {
                "focus": "Comparison and evaluation content",
                "content_type": "Reviews, comparisons, buyer guides",
                "cta_type": "Compare options, get quotes, contact sales"
            },
            "transactional": {
                "focus": "Purchase-oriented content",
                "content_type": "Product pages, pricing, offers",
                "cta_type": "Buy now, add to cart, get discount"
            },
            "navigational": {
                "focus": "Brand-specific information",
                "content_type": "Brand pages, contact info, support",
                "cta_type": "Visit site, contact us, get support"
            }
        }
        
        return strategies.get(primary_intent, strategies["informational"])
    
    def _get_content_focus(self, classification: Dict[str, Any]) -> list:
        """Get content focus areas based on intent mix"""
        focus_areas = []
        
        informational = classification.get("informational", 0)
        commercial = classification.get("commercial", 0)
        transactional = classification.get("transactional", 0)
        navigational = classification.get("navigational", 0)
        
        if informational >= 30:
            focus_areas.append("Educational content and how-to guides")
        if commercial >= 30:
            focus_areas.append("Product comparisons and reviews")
        if transactional >= 30:
            focus_areas.append("Clear purchase pathways and offers")
        if navigational >= 30:
            focus_areas.append("Brand-specific information and support")
        
        return focus_areas if focus_areas else ["Comprehensive informational content"]
    
    def _get_optimization_tactics(self, classification: Dict[str, Any]) -> list:
        """Get specific optimization tactics based on intent"""
        tactics = []
        
        informational = classification.get("informational", 0)
        commercial = classification.get("commercial", 0)
        transactional = classification.get("transactional", 0)
        
        if informational >= 40:
            tactics.extend([
                "Optimize for featured snippets with clear answers",
                "Create comprehensive FAQ sections",
                "Use structured data for how-to content"
            ])
        
        if commercial >= 30:
            tactics.extend([
                "Include comparison tables and review sections",
                "Add pricing and feature comparisons",
                "Implement review schema markup"
            ])
        
        if transactional >= 30:
            tactics.extend([
                "Optimize product schema and pricing markup",
                "Include clear purchase CTAs",
                "Add trust signals and testimonials"
            ])
        
        return tactics if tactics else ["Focus on comprehensive, helpful content"]
