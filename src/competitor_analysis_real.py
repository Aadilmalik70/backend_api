"""
Real Competitor Analysis with Gemini Integration

This module provides competitor analysis functionality using real data sources
instead of mock data, with Gemini API integration for content analysis.
"""

import logging
import re
from typing import Dict, Any, List, Optional

from utils.serpapi_client import SerpAPIClient
from utils.browser_content_scraper import BrowserContentScraper
from utils.gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitorAnalysisReal:
    """
    Real competitor analysis with Gemini integration.
    
    This class provides methods for analyzing competitors using real data sources
    instead of mock data, with Gemini API integration for content analysis.
    """
    
    def __init__(self, serpapi_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        """
        Initialize the competitor analysis module.
        
        Args:
            serpapi_key: SerpAPI key for real data integration
            gemini_api_key: Gemini API key for content analysis
        """
        self.serp_client = SerpAPIClient(api_key=serpapi_key)
        self.content_scraper = BrowserContentScraper()
        self.nlp_client = GeminiNLPClient(api_key=gemini_api_key)
    
    def analyze_competitors(self, keyword: str, limit: int = 20, num_competitors: int = None) -> Dict[str, Any]:
        """
        Analyze competitors for a keyword.
        
        Args:
            keyword: Target keyword
            limit: Maximum number of competitors to analyze
            num_competitors: Alternative parameter name for limit (for compatibility)
            
        Returns:
            Dictionary containing competitor analysis
        """
        logger.info(f"Analyzing competitors for keyword: {keyword}")
        
        # Use num_competitors if provided (for compatibility with test suite)
        if num_competitors is not None:
            limit = num_competitors
        
        # Get competitors from SERP
        competitors = self.serp_client.get_competitors(keyword, limit)
        logger.info(f"Found {len(competitors)} competitors for keyword: {keyword}")
        
        # Analyze each competitor
        competitor_analysis = []
        for competitor in competitors:
            analysis = self._analyze_competitor(competitor, keyword)
            competitor_analysis.append(analysis)
        
        # Generate insights
        insights = self._generate_insights(competitor_analysis, keyword)
        
        # Compile result
        result = {
            "keyword": keyword,
            "competitors": competitor_analysis,
            "insights": insights
        }
        
        return result
    
    def _analyze_competitor(self, competitor: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Analyze a single competitor with robust error handling.
        
        Args:
            competitor: Competitor data
            keyword: Target keyword
            
        Returns:
            Dictionary containing competitor analysis
        """
        url = competitor.get("url", "")
        logger.info(f"Analyzing competitor: {url}")
        
        try:
            # Scrape content with error handling
            content = self.content_scraper.scrape_content(url)
            
            # Check if scraping failed
            if content.get("failed", False) or content.get("error"):
                logger.warning(f"Failed to scrape {url}: {content.get('error', 'Unknown error')}")
                return self._get_failed_competitor_analysis(competitor, content.get('error', 'Scraping failed'))
            
            # Extract main content text for analysis
            main_content = content.get("main_content", "")
            if not main_content or len(main_content.strip()) < 100:
                logger.warning(f"Insufficient content from {url}: {len(main_content)} characters")
                return self._get_failed_competitor_analysis(competitor, "Insufficient content extracted")
            
            # Analyze content with NLP (with error handling)
            try:
                content_analysis = self.nlp_client.analyze_content(main_content)
            except Exception as nlp_error:
                logger.warning(f"NLP analysis failed for {url}: {str(nlp_error)}")
                content_analysis = {"sentiment": {"score": 0}, "entities": []}
            
            # Calculate keyword usage
            keyword_usage = self._calculate_keyword_usage(content, keyword)
            
            # Analyze content structure
            content_structure = self._analyze_structure(content)
            
            # Analyze readability
            readability = self._calculate_readability(main_content)
            
            # Compile successful analysis
            analysis = {
                "url": url,
                "title": competitor.get("title", ""),
                "position": competitor.get("position", 0),
                "domain": competitor.get("domain", ""),
                "content_length": len(main_content),
                "keyword_usage": keyword_usage,
                "content_structure": content_structure,
                "readability": readability,
                "sentiment": content_analysis.get("sentiment", {"score": 0}),
                "entities": content_analysis.get("entities", []),
                "meta": {
                    "description": content.get("meta_description", ""),
                    "title": content.get("title", ""),
                    "h1": self._extract_h1(content.get("headings", []))
                },
                "status": "success",
                "scraped_at": content.get("scraped_at", "")
            }
            
            logger.info(f"Successfully analyzed competitor: {url}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competitor {url}: {str(e)}")
            return self._get_failed_competitor_analysis(competitor, f"Analysis error: {str(e)}")
    
    def _get_failed_competitor_analysis(self, competitor: Dict[str, Any], error_reason: str) -> Dict[str, Any]:
        """
        Generate a failed competitor analysis with consistent structure.
        
        Args:
            competitor: Original competitor data
            error_reason: Reason for failure
            
        Returns:
            Dictionary containing failed analysis with default values
        """
        return {
            "url": competitor.get("url", ""),
            "title": competitor.get("title", ""),
            "position": competitor.get("position", 0),
            "domain": competitor.get("domain", ""),
            "content_length": 0,
            "keyword_usage": {
                "count": 0,
                "density": 0.0,
                "in_title": False,
                "in_meta": False,
                "in_h1": False,
                "title_count": 0,
                "meta_count": 0,
                "h1_count": 0
            },
            "content_structure": {
                "heading_structure": {},
                "paragraph_count": 0,
                "avg_paragraph_length": 0.0,
                "list_count": 0,
                "image_count": 0,
                "internal_link_count": 0,
                "external_link_count": 0
            },
            "readability": {
                "flesch_score": 0.0,
                "reading_level": "Unknown",
                "avg_sentence_length": 0.0,
                "avg_word_length": 0.0,
                "sentence_count": 0,
                "word_count": 0
            },
            "sentiment": {"score": 0},
            "entities": [],
            "meta": {
                "description": "",
                "title": "",
                "h1": ""
            },
            "status": "failed",
            "error": error_reason,
            "scraped_at": ""
        }
    
    def _extract_h1(self, headings: List[Dict[str, str]]) -> str:
        """
        Extract the first H1 heading from headings list.
        
        Args:
            headings: List of heading dictionaries
            
        Returns:
            First H1 text or empty string if not found
        """
        for heading in headings:
            if heading.get("level") == "h1":
                return heading.get("text", "")
        return ""
    
    def _calculate_keyword_usage(self, content: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Calculate keyword usage in content.
        
        Args:
            content: Content data
            keyword: Target keyword
            
        Returns:
            Dictionary containing keyword usage metrics
        """
        # Extract text from the new content structure
        text = content.get("main_content", "")
        title = content.get("title", "")
        meta_description = content.get("meta_description", "") or content.get("description", "")
        
        # Extract H1 from headings
        headings = content.get("headings", [])
        h1 = self._extract_h1(headings)
        
        # Normalize keyword and text
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        title_lower = title.lower()
        meta_lower = meta_description.lower()
        h1_lower = h1.lower()
        
        # Count occurrences
        text_count = text_lower.count(keyword_lower)
        title_count = title_lower.count(keyword_lower)
        meta_count = meta_lower.count(keyword_lower)
        h1_count = h1_lower.count(keyword_lower)
        
        # Calculate density
        word_count = len(text.split()) if text else 0
        density = (text_count / max(1, word_count)) * 100
        
        return {
            "count": text_count,
            "density": round(density, 2),
            "in_title": title_count > 0,
            "in_meta": meta_count > 0,
            "in_h1": h1_count > 0,
            "title_count": title_count,
            "meta_count": meta_count,
            "h1_count": h1_count
        }
    
    def _analyze_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content structure using the new content format.
        
        Args:
            content: Content data
            
        Returns:
            Dictionary containing structure analysis
        """
        # Extract headings from the new format
        headings = content.get("headings", [])
        
        # Count headings by level
        heading_counts = {}
        for heading in headings:
            level = heading.get("level", "")
            if level:
                heading_counts[level] = heading_counts.get(level, 0) + 1
        
        # Extract paragraphs from main content
        main_content = content.get("main_content", "")
        paragraphs = [p.strip() for p in main_content.split('\n') if p.strip() and len(p.strip()) > 10]
        paragraph_count = len(paragraphs)
        
        # Calculate average paragraph length
        total_paragraph_length = sum(len(p) for p in paragraphs)
        avg_paragraph_length = total_paragraph_length / max(1, paragraph_count)
        
        # Extract lists (estimate from content - look for bullet points and numbered lists)
        list_indicators = ['•', '●', '◦', '-', '*']
        list_count = 0
        for paragraph in paragraphs:
            if any(paragraph.strip().startswith(indicator) for indicator in list_indicators):
                list_count += 1
            # Check for numbered lists
            if paragraph.strip() and paragraph.strip()[0].isdigit() and '.' in paragraph[:10]:
                list_count += 1
        
        # Extract images from the new format
        images = content.get("images", [])
        image_count = len(images)
        
        # Extract links from the new format
        links = content.get("links", {})
        internal_links = links.get("internal", [])
        external_links = links.get("external", [])
        internal_link_count = len(internal_links)
        external_link_count = len(external_links)
        
        return {
            "heading_structure": heading_counts,
            "paragraph_count": paragraph_count,
            "avg_paragraph_length": round(avg_paragraph_length, 2),
            "list_count": list_count,
            "image_count": image_count,
            "internal_link_count": internal_link_count,
            "external_link_count": external_link_count
        }
    
    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculate readability metrics for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing readability metrics
        """
        # Split text into sentences and words
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = [w for w in text.split() if w.strip()]
        
        # Count sentences, words, and characters
        sentence_count = len(sentences)
        word_count = len(words)
        char_count = len(text)
        
        # Calculate average sentence length
        avg_sentence_length = word_count / max(1, sentence_count)
        
        # Calculate average word length
        avg_word_length = char_count / max(1, word_count)
        
        # Calculate Flesch Reading Ease score (simplified)
        # 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        # We'll estimate syllables as characters / 3
        syllables = char_count / 3
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * (syllables / max(1, word_count))
        flesch_score = max(0, min(100, flesch_score))
        
        # Determine reading level
        if flesch_score >= 90:
            reading_level = "Very Easy"
        elif flesch_score >= 80:
            reading_level = "Easy"
        elif flesch_score >= 70:
            reading_level = "Fairly Easy"
        elif flesch_score >= 60:
            reading_level = "Standard"
        elif flesch_score >= 50:
            reading_level = "Fairly Difficult"
        elif flesch_score >= 30:
            reading_level = "Difficult"
        else:
            reading_level = "Very Difficult"
        
        return {
            "flesch_score": round(flesch_score, 2),
            "reading_level": reading_level,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2),
            "sentence_count": sentence_count,
            "word_count": word_count
        }
    
    def _generate_insights(self, competitor_analysis: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """
        REAL IMPLEMENTATION REQUIRED:
        - Use actual scraped content lengths from competitor_analysis
        - Extract real entities from actual competitor content
        - Calculate real sentiment scores from actual text
        - Identify genuine content gaps, not assumptions
        """
        
        # MUST: Validate that competitor_analysis contains real scraped data
        if not competitor_analysis:
            logger.error("No real competitor data available for analysis")
            return self._get_empty_insights_with_reason("No competitor data scraped")
        
        # MUST: Extract real content metrics from scraped data
        real_content_lengths = []
        real_entities = []
        real_sentiment_scores = []
        successful_competitors = 0
        failed_competitors = 0
        
        for competitor in competitor_analysis:
            # Track success/failure rates
            if competitor.get("status") == "failed":
                failed_competitors += 1
                logger.warning(f"Skipping failed competitor: {competitor.get('url', 'unknown')} - {competitor.get('error', 'unknown error')}")
                continue
            
            successful_competitors += 1
            
            # Validate this is real scraped data, not mock
            content_length = competitor.get("content_length", 0)
            if content_length > 0:  # Only count real content
                real_content_lengths.append(content_length)
            
            # Extract real entities from actual scraped content
            entities = competitor.get("entities", [])
            if entities and isinstance(entities, list):
                real_entities.extend([e.get("name", "") for e in entities if e.get("name")])
            
            # Extract real sentiment from actual analysis
            sentiment = competitor.get("sentiment", {})
            if sentiment and isinstance(sentiment, dict):
                score = sentiment.get("score", 0)
                if isinstance(score, (int, float)):
                    real_sentiment_scores.append(score)
        
        # MUST: Use real data for calculations
        if real_content_lengths:
            content_insights = {
                "average": sum(real_content_lengths) / len(real_content_lengths),
                "min": min(real_content_lengths),
                "max": max(real_content_lengths),
                "count": len(real_content_lengths)
            }
        else:
            content_insights = {"error": "No real content data available"}
        
        # MUST: Extract real common topics from actual entities
        from collections import Counter
        if real_entities:
            entity_counter = Counter([entity.lower().strip() for entity in real_entities if entity.strip()])
            # Only include entities mentioned by multiple competitors (real commonality)
            common_topics = [entity for entity, count in entity_counter.most_common(20) if count >= 2]
        else:
            common_topics = []
        
        # MUST: Calculate real sentiment trend
        if real_sentiment_scores:
            avg_sentiment = sum(real_sentiment_scores) / len(real_sentiment_scores)
            sentiment_trend = "Positive" if avg_sentiment > 0.1 else ("Negative" if avg_sentiment < -0.1 else "Neutral")
        else:
            sentiment_trend = "Unknown - No sentiment data"
        
        return {
            "content_length": content_insights,
            "common_topics": common_topics,
            "sentiment_trend": sentiment_trend,
            "data_quality": {
                "competitors_analyzed": len(competitor_analysis),
                "successful_competitors": successful_competitors,
                "failed_competitors": failed_competitors,
                "success_rate": round(successful_competitors / max(1, len(competitor_analysis)) * 100, 1),
                "content_samples": len(real_content_lengths),
                "entities_extracted": len(real_entities),
                "sentiment_samples": len(real_sentiment_scores)
            }
        }
    
    def _get_empty_insights_with_reason(self, reason: str) -> Dict[str, Any]:
        """
        Return empty insights structure with error reason.
        
        Args:
            reason: Reason why insights are empty
            
        Returns:
            Dictionary with empty insights and error reason
        """
        return {
            "content_length": {"error": reason},
            "common_topics": [],
            "sentiment_trend": "Unknown - " + reason,
            "data_quality": {
                "competitors_analyzed": 0,
                "content_samples": 0,
                "entities_extracted": 0,
                "sentiment_samples": 0,
                "error": reason
            }
        }
    
    def generate_content_blueprint(self, keyword: str, num_competitors: int = 20) -> Dict[str, Any]:
        """
        Generate content blueprint based on competitor analysis with robust error handling.
        
        Args:
            keyword: Target keyword
            num_competitors: Number of competitors to analyze
            
        Returns:
            Dictionary containing content blueprint
        """
        logger.info(f"Generating content blueprint for keyword: {keyword}")
        
        try:
            # Analyze competitors with error handling
            try:
                competitor_analysis = self.analyze_competitors(keyword, num_competitors=num_competitors)
            except Exception as competitor_error:
                logger.error(f"Error during competitor analysis: {str(competitor_error)}")
                # Continue with empty competitor analysis rather than failing completely
                competitor_analysis = {
                    "keyword": keyword,
                    "competitors": [],
                    "insights": self._get_empty_insights_with_reason(f"Competitor analysis failed: {str(competitor_error)}")
                }
            
            # Extract insights
            insights = competitor_analysis.get("insights", {})
            common_entities = insights.get("common_topics", [])  # This will be an empty list if not found
            
            # Generate content outline with Gemini
            common_topics_string = ", ".join(common_entities[:8])  # common_entities is now a list of strings
            if not common_topics_string:
                common_topics_string = "general best practices and common knowledge for this topic"

            try:
                outline_prompt = f"""
                Create a comprehensive content outline for an article about "{keyword}".
                
                Consider these common topics from competitor analysis (or general best practices if specific topics are unavailable):
                {common_topics_string}
                
                The outline should include:
                1. A compelling title
                2. 5-7 main sections with descriptive headings
                3. 2-4 subsections under each main section
                4. Key points to cover in each section
                
                Format the response as a structured outline with clear hierarchy.
                """
                
                outline_response = self.nlp_client.generate_content(outline_prompt)
            except Exception as outline_error:
                logger.warning(f"Error generating outline with Gemini: {str(outline_error)}")
                outline_response = f"Default outline for {keyword} (Gemini unavailable)"
            
            # Generate recommendations with Gemini
            avg_length = insights.get('content_length', {}).get('average', 0)
            sentiment_trend = insights.get('sentiment_trend', 'Neutral')  # This is now a string, not dict

            recommendations_prompt_considerations = []
            if avg_length > 0:
                recommendations_prompt_considerations.append(f"- Average content length: {avg_length} words")
            else:
                recommendations_prompt_considerations.append("- Competitor content length data is unavailable. Focus on creating comprehensive content.")
            
            recommendations_prompt_considerations.append(f"- Sentiment trend: {sentiment_trend}")

            try:
                recommendations_prompt = f"""
                Based on competitor analysis for the keyword "{keyword}", provide 5-7 specific content recommendations.
                
                Consider:
                {chr(10).join(recommendations_prompt_considerations)}
                
                Format the response as a list of specific, actionable recommendations.
                If specific competitor data is limited, provide general best practice recommendations.
                """
                
                recommendations_response = self.nlp_client.generate_content(recommendations_prompt)
            except Exception as rec_error:
                logger.warning(f"Error generating recommendations with Gemini: {str(rec_error)}")
                recommendations_response = "Default recommendations (Gemini unavailable)"
            
            # Parse recommendations into a list
            recommendations = []
            if recommendations_response and "fallback content" not in recommendations_response.lower() and "error" not in recommendations_response.lower():
                for line in recommendations_response.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('*') or (len(line) > 2 and line[0].isdigit() and line[1] == '.')):
                        recommendations.append(line.lstrip('- *0123456789.').strip())
            
            # If parsing failed or response indicates an issue, create a default list
            if not recommendations:
                default_length_target = "1500-2000 words" if avg_length == 0 else f"{int(avg_length)} words"
                recommendations = [
                    "Due to limited specific competitor data, these are general SEO and content best practices:",
                    "Include at least 3-5 high-quality images relevant to the topic.",
                    f"Aim for a comprehensive content length (e.g., {default_length_target}).",
                    "Use bulleted lists, numbered lists, and clear formatting (bolding, short paragraphs) to improve readability.",
                    "Include relevant internal links to related content on your site and external links to authoritative sources.",
                    "Structure content logically with clear headings (H2, H3) and subheadings. Ensure the main keyword is used naturally within headings and content.",
                    "Craft a compelling meta description and title tag that includes the target keyword."
                ]
            
            # Parse outline into structured format
            title = ""
            sections = []
            
            lines = outline_response.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    if not title and not line.startswith('#') and not line.startswith('-'):
                        title = line
                    elif line.startswith('# ') or line.startswith('## '):
                        sections.append({
                            "heading": line.lstrip('#').strip(),
                            "subsections": []
                        })
                    elif line.startswith('### ') and sections:
                        sections[-1]["subsections"].append(line.lstrip('#').strip())
            
            # If parsing failed, create a default outline
            if not title:
                title = f"Complete Guide to {keyword.title()}"
            
            if not sections:
                sections = [
                    {"heading": "Introduction to " + keyword.title(), "subsections": ["What is " + keyword.title(), "Why " + keyword.title() + " Matters"]},
                    {"heading": "Key Strategies", "subsections": ["Best Practices", "Common Mistakes to Avoid"]},
                    {"heading": "Implementation Guide", "subsections": ["Step-by-Step Process", "Tools and Resources"]},
                    {"heading": "Case Studies", "subsections": ["Success Stories", "Lessons Learned"]},
                    {"heading": "Future Trends", "subsections": ["Emerging Technologies", "Industry Predictions"]}
                ]
            
            # Compile result
            result = {
                "keyword": keyword,
                "outline": {
                    "title": title,
                    "sections": sections
                },
                "recommendations": recommendations,
                "competitor_insights": {
                    "content_length": insights.get("content_length", {"average": 0, "min": 0, "max": 0}), # Ensure default structure
                    "common_topics": common_entities[:5],  # common_entities is already a list of strings
                    "sentiment_trend": insights.get("sentiment_trend", "Neutral")  # Fixed: sentiment_trend is now a string, not dict
                },
                "data_quality": insights.get("data_quality", {
                    "competitors_analyzed": 0,
                    "successful_competitors": 0,
                    "failed_competitors": 0,
                    "success_rate": 0
                })
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating content blueprint: {str(e)}")
            # Return a minimal but functional blueprint instead of crashing
            return {
                "keyword": keyword,
                "outline": {
                    "title": f"Complete Guide to {keyword.title()}",
                    "sections": [
                        {"heading": "Introduction to " + keyword.title(), "subsections": ["What is " + keyword.title(), "Why " + keyword.title() + " Matters"]},
                        {"heading": "Key Strategies", "subsections": ["Best Practices", "Common Mistakes to Avoid"]},
                        {"heading": "Implementation Guide", "subsections": ["Step-by-Step Process", "Tools and Resources"]},
                        {"heading": "Case Studies", "subsections": ["Success Stories", "Lessons Learned"]},
                        {"heading": "Future Trends", "subsections": ["Emerging Technologies", "Industry Predictions"]}
                    ]
                },
                "recommendations": [
                    "Create comprehensive, well-researched content covering all aspects of the topic",
                    "Include relevant examples and case studies to support your points",
                    "Optimize for search engines while maintaining readability",
                    "Add visual elements like images, charts, or infographics",
                    "Structure content with clear headings and subheadings",
                    "Include actionable takeaways for readers"
                ],
                "competitor_insights": {
                    "content_length": {"average": 0, "min": 0, "max": 0},
                    "common_topics": [],
                    "sentiment_trend": "Neutral"
                },
                "error": f"Content blueprint generation failed: {str(e)}",
                "data_quality": {
                    "competitors_analyzed": 0,
                    "successful_competitors": 0,
                    "failed_competitors": 0,
                    "success_rate": 0,
                    "error": str(e)
                }
            }
