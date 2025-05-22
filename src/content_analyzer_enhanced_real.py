"""
Enhanced Content Analyzer with Gemini API Integration

This module provides enhanced content analysis functionality using Google's Gemini API
instead of mock data or other NLP solutions.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from .utils.browser_content_scraper import BrowserContentScraper
from .utils.gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAnalyzerEnhancedReal:
    """
    Enhanced content analyzer with Gemini API integration.
    
    This class provides methods for analyzing content from URLs using
    real browser-based scraping and Gemini API for NLP analysis.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the enhanced content analyzer.
        
        Args:
            gemini_api_key: Gemini API key
        """
        self.nlp_client = GeminiNLPClient(api_key=gemini_api_key)
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze content from a URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing content from URL: {url}")
        
        # Scrape content from URL
        with BrowserContentScraper() as scraper:
            scraped_content = scraper.scrape_content(url)
        
        # Extract main content for NLP analysis
        main_content = scraped_content["main_content"]
        
        # Perform NLP analysis using Gemini API
        nlp_analysis = self.nlp_client.analyze_content(main_content)
        
        # Compile results
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
                "entities": nlp_analysis["entities"],
                "sentiment": nlp_analysis["sentiment"],
                "categories": nlp_analysis["categories"]
            },
            "content_quality": self._assess_content_quality(scraped_content, nlp_analysis),
            "seo_analysis": self._analyze_seo(scraped_content),
            "recommendations": self._generate_recommendations(scraped_content, nlp_analysis)
        }
        
        return result
    
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
    
    def _assess_content_quality(self, scraped_content: Dict[str, Any], nlp_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess content quality based on various metrics.
        
        Args:
            scraped_content: Scraped content dictionary
            nlp_analysis: NLP analysis dictionary
            
        Returns:
            Dictionary containing content quality assessment
        """
        # Extract metrics
        word_count = scraped_content["word_count"]
        
        # Get paragraph count from content_metrics or calculate
        if "content_metrics" in scraped_content and "paragraph_count" in scraped_content["content_metrics"]:
            paragraph_count = scraped_content["content_metrics"]["paragraph_count"]
        else:
            # Approximate paragraph count
            paragraphs = [p for p in scraped_content["main_content"].split('\n') if p.strip()]
            paragraph_count = len(paragraphs)
        
        # Get heading count
        heading_count = len(scraped_content["headings"])
        
        # Get image count
        image_count = len(scraped_content["images"])
        
        # Get link counts
        internal_link_count = len(scraped_content["links"]["internal"])
        external_link_count = len(scraped_content["links"]["external"])
        
        # Calculate content density (words per paragraph)
        content_density = word_count / max(1, paragraph_count)
        
        # Calculate heading ratio (words per heading)
        heading_ratio = word_count / max(1, heading_count)
        
        # Calculate image ratio (words per image)
        image_ratio = word_count / max(1, image_count)
        
        # Calculate link ratio (words per link)
        link_ratio = word_count / max(1, internal_link_count + external_link_count)
        
        # Assess content length
        if word_count < 300:
            length_assessment = "Very Short"
            length_score = 1
        elif word_count < 600:
            length_assessment = "Short"
            length_score = 2
        elif word_count < 1200:
            length_assessment = "Medium"
            length_score = 3
        elif word_count < 2000:
            length_assessment = "Long"
            length_score = 4
        else:
            length_assessment = "Very Long"
            length_score = 5
        
        # Assess content structure
        structure_score = 0
        
        # Heading frequency (ideal: 1 heading per 150-300 words)
        if heading_count > 0 and 150 <= heading_ratio <= 300:
            structure_score += 2
        elif heading_count > 0:
            structure_score += 1
        
        # Paragraph length (ideal: 3-5 sentences per paragraph)
        if 40 <= content_density <= 100:
            structure_score += 2
        elif content_density < 150:
            structure_score += 1
        
        # Image usage (ideal: 1 image per 350-500 words)
        if image_count > 0 and 350 <= image_ratio <= 500:
            structure_score += 1
        
        # Link usage (ideal: not too sparse, not too dense)
        if internal_link_count + external_link_count > 0 and 150 <= link_ratio <= 350:
            structure_score += 1
        
        # Normalize structure score to 1-5
        structure_score = min(5, max(1, structure_score + 1))
        
        # Assess content sentiment
        sentiment_score = nlp_analysis["sentiment"]["score"]
        sentiment_magnitude = nlp_analysis["sentiment"]["magnitude"]
        
        if sentiment_score > 0.5:
            sentiment_assessment = "Very Positive"
        elif sentiment_score > 0.1:
            sentiment_assessment = "Positive"
        elif sentiment_score > -0.1:
            sentiment_assessment = "Neutral"
        elif sentiment_score > -0.5:
            sentiment_assessment = "Negative"
        else:
            sentiment_assessment = "Very Negative"
        
        # Calculate overall quality score (1-100)
        quality_score = (length_score * 15) + (structure_score * 15) + (min(5, len(nlp_analysis["entities"])) * 4)
        
        # Adjust for sentiment (neutral is often best for informational content)
        if -0.2 <= sentiment_score <= 0.2:
            quality_score += 10
        elif -0.5 <= sentiment_score <= 0.5:
            quality_score += 5
        
        # Ensure score is within 1-100 range
        quality_score = min(100, max(1, quality_score))
        
        return {
            "overall_score": quality_score,
            "length": {
                "assessment": length_assessment,
                "word_count": word_count
            },
            "structure": {
                "score": structure_score,
                "paragraph_density": round(content_density, 2),
                "heading_frequency": round(heading_ratio, 2) if heading_count > 0 else 0
            },
            "sentiment": {
                "assessment": sentiment_assessment,
                "score": round(sentiment_score, 2),
                "magnitude": round(sentiment_magnitude, 2)
            },
            "entity_count": len(nlp_analysis["entities"])
        }
    
    def _analyze_seo(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze SEO aspects of content.
        
        Args:
            content: Scraped content dictionary
            
        Returns:
            Dictionary containing SEO analysis
        """
        # Extract relevant data
        title = content["title"]
        description = content["description"]
        headings = content["headings"]
        url = content["url"]
        domain = content["domain"] if "domain" in content else urlparse(url).netloc
        
        # Analyze title
        title_length = len(title)
        title_score = 0
        title_issues = []
        
        if 40 <= title_length <= 60:
            title_score = 5  # Ideal length
        elif 30 <= title_length < 40 or 60 < title_length <= 70:
            title_score = 4  # Good length
        elif 20 <= title_length < 30 or 70 < title_length <= 80:
            title_score = 3  # Acceptable length
        elif 10 <= title_length < 20 or 80 < title_length <= 100:
            title_score = 2  # Suboptimal length
            title_issues.append(f"Title length ({title_length} characters) is not optimal")
        else:
            title_score = 1  # Poor length
            title_issues.append(f"Title length ({title_length} characters) is problematic")
        
        # Analyze meta description
        description_length = len(description)
        description_score = 0
        description_issues = []
        
        if 120 <= description_length <= 160:
            description_score = 5  # Ideal length
        elif 100 <= description_length < 120 or 160 < description_length <= 180:
            description_score = 4  # Good length
        elif 80 <= description_length < 100 or 180 < description_length <= 200:
            description_score = 3  # Acceptable length
        elif 50 <= description_length < 80 or 200 < description_length <= 250:
            description_score = 2  # Suboptimal length
            description_issues.append(f"Description length ({description_length} characters) is not optimal")
        else:
            description_score = 1  # Poor length
            if description_length == 0:
                description_issues.append("Meta description is missing")
            else:
                description_issues.append(f"Description length ({description_length} characters) is problematic")
        
        # Analyze headings
        heading_score = 0
        heading_issues = []
        
        # Check if there's an H1
        has_h1 = any(h["level"] == "h1" for h in headings)
        
        if has_h1:
            heading_score += 2
        else:
            heading_issues.append("No H1 heading found")
        
        # Check heading hierarchy
        heading_levels = [h["level"] for h in headings]
        
        if heading_levels and heading_levels[0] == "h1" and "h3" in heading_levels and "h2" not in heading_levels:
            heading_issues.append("Heading hierarchy is not sequential (H3 without H2)")
            heading_score += 1
        elif len(heading_levels) >= 3:
            heading_score += 3
        elif len(heading_levels) >= 2:
            heading_score += 2
        elif len(heading_levels) == 1:
            heading_score += 1
        
        # Normalize heading score to 1-5
        heading_score = min(5, heading_score)
        
        # Analyze URL
        url_score = 0
        url_issues = []
        
        # Check URL length
        path = urlparse(url).path
        path_length = len(path)
        
        if 20 <= path_length <= 60:
            url_score += 2
        elif path_length < 100:
            url_score += 1
        else:
            url_issues.append(f"URL path is too long ({path_length} characters)")
        
        # Check for URL readability
        if re.search(r'[A-Z]', path):
            url_issues.append("URL contains uppercase letters")
        else:
            url_score += 1
        
        if re.search(r'[^a-zA-Z0-9\-/]', path):
            url_issues.append("URL contains special characters")
        else:
            url_score += 1
        
        if re.search(r'\d{5,}', path):
            url_issues.append("URL contains long numeric sequences")
        else:
            url_score += 1
        
        # Normalize URL score to 1-5
        url_score = min(5, url_score)
        
        # Calculate overall SEO score
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
    
    def _generate_recommendations(self, content: Dict[str, Any], nlp_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate content improvement recommendations.
        
        Args:
            content: Scraped content dictionary
            nlp_analysis: NLP analysis dictionary
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Word count recommendations
        word_count = content["word_count"]
        if word_count < 300:
            recommendations.append({
                "type": "content_length",
                "priority": "high",
                "recommendation": "Increase content length to at least 600 words for better search visibility."
            })
        elif word_count < 600:
            recommendations.append({
                "type": "content_length",
                "priority": "medium",
                "recommendation": "Consider expanding content to 1000+ words for more comprehensive coverage."
            })
        
        # Heading recommendations
        headings = content["headings"]
        if not headings:
            recommendations.append({
                "type": "structure",
                "priority": "high",
                "recommendation": "Add headings (H1, H2, H3) to structure your content and improve readability."
            })
        elif len(headings) < 3 and word_count > 600:
            recommendations.append({
                "type": "structure",
                "priority": "medium",
                "recommendation": "Add more headings to break up long content sections."
            })
        
        # Image recommendations
        images = content["images"]
        if not images:
            recommendations.append({
                "type": "media",
                "priority": "medium",
                "recommendation": "Add relevant images to enhance engagement and visual appeal."
            })
        elif len(images) < 2 and word_count > 1000:
            recommendations.append({
                "type": "media",
                "priority": "low",
                "recommendation": "Consider adding more images for long-form content."
            })
        
        # Link recommendations
        internal_links = content["links"]["internal"]
        external_links = content["links"]["external"]
        
        if not external_links:
            recommendations.append({
                "type": "links",
                "priority": "medium",
                "recommendation": "Add external links to authoritative sources to improve credibility."
            })
        
        if not internal_links and "domain" in content:
            recommendations.append({
                "type": "links",
                "priority": "medium",
                "recommendation": "Add internal links to related content on your site."
            })
        
        # Readability recommendations
        if "content_metrics" in content and "readability_score" in content["content_metrics"]:
            readability_score = content["content_metrics"]["readability_score"]
            if readability_score < 30:
                recommendations.append({
                    "type": "readability",
                    "priority": "high",
                    "recommendation": "Simplify language and sentence structure to improve readability."
                })
            elif readability_score < 50:
                recommendations.append({
                    "type": "readability",
                    "priority": "medium",
                    "recommendation": "Consider using shorter sentences and simpler words to improve readability."
                })
        
        # SEO recommendations
        if "description" in content and (not content["description"] or len(content["description"]) < 50):
            recommendations.append({
                "type": "seo",
                "priority": "high",
                "recommendation": "Add or improve meta description (120-160 characters) for better search visibility."
            })
        
        # Entity recommendations
        entities = nlp_analysis["entities"]
        if len(entities) < 3:
            recommendations.append({
                "type": "content",
                "priority": "medium",
                "recommendation": "Include more relevant entities (people, places, organizations, concepts) in your content."
            })
        
        # Category recommendations based on Gemini analysis
        categories = nlp_analysis.get("categories", [])
        if categories and len(categories) > 0:
            main_category = categories[0]["name"] if len(categories) > 0 else "general"
            recommendations.append({
                "type": "content_focus",
                "priority": "medium",
                "recommendation": f"Your content is primarily categorized as '{main_category}'. Consider expanding on this topic or adding related subtopics for more comprehensive coverage."
            })
        
        return recommendations
