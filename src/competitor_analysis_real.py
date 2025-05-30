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
        Analyze a single competitor.
        
        Args:
            competitor: Competitor data
            keyword: Target keyword
            
        Returns:
            Dictionary containing competitor analysis
        """
        url = competitor.get("url", "")
        logger.info(f"Analyzing competitor: {url}")
        
        # Scrape content
        content = self.content_scraper.scrape_content(url)
        
        # Analyze content with NLP
        content_analysis = self.nlp_client.analyze_content(content.get("content", ""))
        
        # Calculate keyword usage
        keyword_usage = self._calculate_keyword_usage(content, keyword)
        
        # Analyze content structure
        content_structure = self._analyze_structure(content)
        
        # Analyze readability
        readability = self._calculate_readability(content.get("content", ""))
        
        # Compile analysis
        analysis = {
            "url": url,
            "title": competitor.get("title", ""),
            "position": competitor.get("position", 0),
            "domain": competitor.get("domain", ""),
            "content_length": len(content.get("content", "")),
            "keyword_usage": keyword_usage,
            "content_structure": content_structure,
            "readability": readability,
            "sentiment": content_analysis.get("sentiment", {}),
            "entities": content_analysis.get("entities", []),
            "meta": {
                "description": content.get("meta_description", ""),
                "title": content.get("title", ""),
                "h1": content.get("h1", "")
            }
        }
        
        return analysis
    
    def _calculate_keyword_usage(self, content: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Calculate keyword usage in content.
        
        Args:
            content: Content data
            keyword: Target keyword
            
        Returns:
            Dictionary containing keyword usage metrics
        """
        text = content.get("content", "")
        title = content.get("title", "")
        meta_description = content.get("meta_description", "")
        h1 = content.get("h1", "")
        
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
        word_count = len(text.split())
        density = text_count / max(1, word_count) * 100
        
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
        Analyze content structure.
        
        Args:
            content: Content data
            
        Returns:
            Dictionary containing structure analysis
        """
        # Extract headings
        headings = content.get("headings", [])
        
        # Count headings by level
        heading_counts = {}
        for heading in headings:
            level = heading.get("level", "")
            if level:
                heading_counts[level] = heading_counts.get(level, 0) + 1
        
        # Extract paragraphs
        paragraphs = content.get("paragraphs", [])
        paragraph_count = len(paragraphs)
        
        # Calculate average paragraph length
        total_paragraph_length = sum(len(p) for p in paragraphs)
        avg_paragraph_length = total_paragraph_length / max(1, paragraph_count)
        
        # Extract lists
        lists = content.get("lists", [])
        list_count = len(lists)
        
        # Extract images
        images = content.get("images", [])
        image_count = len(images)
        
        # Extract links
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
        
        for competitor in competitor_analysis:
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
        Generate content blueprint based on competitor analysis.
        
        Args:
            keyword: Target keyword
            num_competitors: Number of competitors to analyze
            
        Returns:
            Dictionary containing content blueprint
        """
        logger.info(f"Generating content blueprint for keyword: {keyword}")
        
        # Analyze competitors
        competitor_analysis = self.analyze_competitors(keyword, num_competitors=num_competitors)
        
        # Extract insights
        insights = competitor_analysis.get("insights", {})
        common_entities = insights.get("common_entities", []) # This will be an empty list if not found
        content_structure = insights.get("content_structure", {})
        
        # Generate content outline with Gemini
        common_topics_string = ", ".join(common_entities[:8])  # common_entities is now a list of strings
        if not common_topics_string:
            common_topics_string = "general best practices and common knowledge for this topic"

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
        
        # Generate recommendations with Gemini
        avg_length = insights.get('content_length', {}).get('average', 0)
        # Note: content_structure is not available in insights from _generate_insights anymore
        sentiment_trend = insights.get('sentiment_trend', 'Neutral')  # This is now a string, not dict

        recommendations_prompt_considerations = []
        if avg_length > 0:
            recommendations_prompt_considerations.append(f"- Average content length: {avg_length} words")
        else:
            recommendations_prompt_considerations.append("- Competitor content length data is unavailable. Focus on creating comprehensive content.")
        
        recommendations_prompt_considerations.append(f"- Sentiment trend: {sentiment_trend}")

        recommendations_prompt = f"""
        Based on competitor analysis for the keyword "{keyword}", provide 5-7 specific content recommendations.
        
        Consider:
        {chr(10).join(recommendations_prompt_considerations)}
        
        Format the response as a list of specific, actionable recommendations.
        If specific competitor data is limited, provide general best practice recommendations.
        """
        
        recommendations_response = self.nlp_client.generate_content(recommendations_prompt)
        
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
            }
        }
        
        return result
