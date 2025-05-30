import logging
from typing import Dict, Any, List, Optional
from collections import Counter
import statistics

from .gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentPerformanceAnalyzer:
  
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the content performance analyzer.
        
        Args:
            gemini_api_key: Gemini API key for content analysis
        """
        self.gemini_client = GeminiNLPClient(api_key=gemini_api_key)
    
    def analyze_real_content_patterns(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        REAL IMPLEMENTATION REQUIRED:
        - Analyze actual scraped competitor content
        - Identify real content type patterns
        - Calculate real performance indicators
        """
        
        if not competitor_data:
            return {"error": "No real competitor data available"}
        
        # MUST: Analyze real content from scraped data
        real_patterns = {
            "content_types": self._analyze_real_content_types(competitor_data),
            "length_distribution": self._analyze_real_length_patterns(competitor_data),
            "structure_patterns": self._analyze_real_structure_patterns(competitor_data),
            "topic_coverage": self._analyze_real_topic_coverage(competitor_data),
            "content_freshness": self._analyze_real_freshness_signals(competitor_data)
        }
        
        # MUST: Use real Gemini analysis for insights
        insights = self._generate_real_insights(real_patterns)
        
        return {
            "patterns": real_patterns,
            "insights": insights,
            "data_quality": {
                "competitors_analyzed": len(competitor_data),
                "real_content_samples": len([c for c in competitor_data if c.get("content_length", 0) > 0])
            }
        }
    
    def _analyze_real_content_types(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real content types from competitor titles and content"""
        
        content_types = {"guides": 0, "lists": 0, "comparisons": 0, "reviews": 0, "tutorials": 0, "news": 0, "other": 0}
        
        for competitor in competitor_data:
            title = competitor.get("title", "").lower()
            content = competitor.get("content", "").lower()[:500]  # First 500 chars for performance
            
            # Real pattern detection based on actual content analysis
            classified = False
            
            # Guide detection
            if any(word in title for word in ["guide", "complete", "ultimate", "comprehensive", "handbook", "manual"]):
                content_types["guides"] += 1
                classified = True
            # List detection
            elif (
                any(word in title for word in ["best", "top", "list", "ranking", "most", "least"])
                or any(pattern in title for pattern in ["10 ", "5 ", "15 ", "20 ", "7 "])
            ):
                content_types["lists"] += 1
                classified = True
            # Comparison detection
            elif any(word in title for word in ["vs", "versus", "compared", "comparison", "difference", "better"]):
                content_types["comparisons"] += 1
                classified = True
            # Review detection
            elif any(word in title for word in ["review", "reviews", "tested", "rating", "pros", "cons"]):
                content_types["reviews"] += 1
                classified = True
            # Tutorial detection
            elif any(word in title for word in ["how to", "tutorial", "step", "learn", "beginners", "start"]):
                content_types["tutorials"] += 1
                classified = True
            # News detection
            elif any(word in title for word in ["news", "breaking", "update", "announced", "launched", "new"]):
                content_types["news"] += 1
                classified = True
            
            if not classified:
                content_types["other"] += 1
        
        # Calculate real percentages
        total = len(competitor_data)
        percentages = {ctype: round((count/total)*100, 1) for ctype, count in content_types.items()}
        
        # Find dominant type
        dominant_type = max(content_types.items(), key=lambda x: x[1])[0] if total > 0 else None
        
        return {
            "type_counts": content_types,
            "type_percentages": percentages,
            "dominant_type": dominant_type,
            "classification_coverage": round((total - content_types["other"])/total * 100, 1) if total > 0 else 0
        }
    
    def _analyze_real_length_patterns(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real content length patterns from competitor data"""
        
        # Extract real content lengths
        content_lengths = [c.get("content_length", 0) for c in competitor_data if c.get("content_length", 0) > 0]
        
        if not content_lengths:
            return {"error": "No real content length data available"}
        
        # Calculate real statistics
        content_lengths.sort()
        
        return {
            "total_samples": len(content_lengths),
            "min_length": min(content_lengths),
            "max_length": max(content_lengths),
            "median_length": statistics.median(content_lengths),
            "average_length": round(statistics.mean(content_lengths), 0),
            "std_deviation": round(statistics.stdev(content_lengths) if len(content_lengths) > 1 else 0, 0),
            "quartiles": {
                "q1": statistics.quantiles(content_lengths, n=4)[0] if len(content_lengths) >= 4 else content_lengths[0],
                "q2": statistics.median(content_lengths),
                "q3": statistics.quantiles(content_lengths, n=4)[2] if len(content_lengths) >= 4 else content_lengths[-1]
            },
            "length_ranges": {
                "short_under_1000": len([l for l in content_lengths if l < 1000]),
                "medium_1000_3000": len([l for l in content_lengths if 1000 <= l < 3000]),
                "long_3000_plus": len([l for l in content_lengths if l >= 3000])
            }
        }
    
    def _analyze_real_structure_patterns(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real content structure patterns from competitor data"""
        
        structure_metrics = {
            "headings": [],
            "paragraphs": [],
            "images": [],
            "lists": [],
            "internal_links": [],
            "external_links": []
        }
        
        for competitor in competitor_data:
            content_structure = competitor.get("content_structure", {})
            
            # Extract real structural elements
            if content_structure:
                heading_counts = content_structure.get("heading_structure", {})
                total_headings = sum(heading_counts.values()) if heading_counts else 0
                structure_metrics["headings"].append(total_headings)
                
                structure_metrics["paragraphs"].append(content_structure.get("paragraph_count", 0))
                structure_metrics["images"].append(content_structure.get("image_count", 0))
                structure_metrics["lists"].append(content_structure.get("list_count", 0))
                structure_metrics["internal_links"].append(content_structure.get("internal_link_count", 0))
                structure_metrics["external_links"].append(content_structure.get("external_link_count", 0))
        
        # Calculate averages for each metric
        averages = {}
        for metric, values in structure_metrics.items():
            if values:
                averages[f"avg_{metric}"] = round(statistics.mean(values), 1)
                averages[f"median_{metric}"] = statistics.median(values)
            else:
                averages[f"avg_{metric}"] = 0
                averages[f"median_{metric}"] = 0
        
        return {
            "structure_averages": averages,
            "samples_analyzed": len([c for c in competitor_data if c.get("content_structure")]),
            "heading_usage": self._analyze_heading_patterns(competitor_data),
            "multimedia_usage": {
                "images_per_1000_words": self._calculate_images_per_1000_words(competitor_data),
                "common_image_placement": "distributed"  # Based on typical patterns
            }
        }
    
    def _analyze_heading_patterns(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real heading usage patterns"""
        
        heading_patterns = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}
        total_pages = 0
        
        for competitor in competitor_data:
            content_structure = competitor.get("content_structure", {})
            heading_structure = content_structure.get("heading_structure", {})
            
            if heading_structure:
                total_pages += 1
                for level, count in heading_structure.items():
                    if level in heading_patterns:
                        heading_patterns[level] += count
        
        # Calculate averages
        if total_pages > 0:
            avg_patterns = {level: round(count/total_pages, 1) for level, count in heading_patterns.items()}
        else:
            avg_patterns = heading_patterns
        
        return {
            "average_per_page": avg_patterns,
            "most_used_level": max(heading_patterns.items(), key=lambda x: x[1])[0] if any(heading_patterns.values()) else "h2",
            "pages_analyzed": total_pages
        }
        
        
    def _calculate_images_per_1000_words(self, competitor_data: List[Dict[str, Any]]) -> float:
        """Calculate average images per 1000 words across competitors"""
        
        ratios = []
        
        for competitor in competitor_data:
            content_length = competitor.get("content_length", 0)
            content_structure = competitor.get("content_structure", {})
            image_count = content_structure.get("image_count", 0)
            
            if content_length > 0:
                ratio = (image_count / content_length) * 1000
                ratios.append(ratio)
        
        return round(statistics.mean(ratios), 2) if ratios else 0
    
    def _analyze_real_topic_coverage(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real topic coverage from competitor entities and content"""
        
        all_entities = []
        topic_keywords = []
        
        for competitor in competitor_data:
            # Extract real entities from NLP analysis
            entities = competitor.get("entities", [])
            if entities:
                entity_names = [e.get("name", "").lower() for e in entities if e.get("name")]
                all_entities.extend(entity_names)
            
            # Extract keywords from titles and content
            title = competitor.get("title", "")
            if title:
                # Simple keyword extraction from titles
                title_words = [word.lower().strip() for word in title.split() 
                              if len(word) > 3 and word.isalpha()]
                topic_keywords.extend(title_words)
        
        # Count entity and keyword frequencies
        entity_counts = Counter(all_entities)
        keyword_counts = Counter(topic_keywords)
        
        # Get most common topics (entities mentioned by multiple competitors)
        common_entities = [entity for entity, count in entity_counts.most_common(20) if count >= 2]
        common_keywords = [keyword for keyword, count in keyword_counts.most_common(20) if count >= 2]
        
        return {
            "total_entities_found": len(all_entities),
            "unique_entities": len(entity_counts),
            "common_entities": common_entities[:10],
            "entity_frequency": dict(entity_counts.most_common(10)),
            "common_keywords": common_keywords[:10],
            "keyword_frequency": dict(keyword_counts.most_common(10)),
            "topic_diversity": len(set(all_entities + topic_keywords)),
            "coverage_depth": "high" if len(common_entities) > 5 else ("medium" if len(common_entities) > 2 else "low")
        }
    
    def _analyze_real_freshness_signals(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content freshness signals from real competitor data"""
        
        freshness_indicators = {
            "date_mentions": 0,
            "current_year_mentions": 0,
            "update_signals": 0,
            "recent_events": 0
        }
        
        current_year = "2025"
        recent_years = ["2024", "2025"]
        
        for competitor in competitor_data:
            title = competitor.get("title", "").lower()
            content = competitor.get("content", "").lower()[:1000]  # First 1000 chars
            
            # Check for date mentions
            if any(year in title + content for year in recent_years):
                freshness_indicators["date_mentions"] += 1
            
            # Check for current year specifically
            if current_year in title + content:
                freshness_indicators["current_year_mentions"] += 1
            
            # Check for update signals
            update_words = ["updated", "latest", "new", "recent", "current", "now"]
            if any(word in title for word in update_words):
                freshness_indicators["update_signals"] += 1
            
            # Check for recent event mentions (simplified)
            recent_terms = ["ai", "chatgpt", "covid", "pandemic", "remote work", "climate"]
            if any(term in content for term in recent_terms):
                freshness_indicators["recent_events"] += 1
        
        total_competitors = len(competitor_data)
        percentages = {k: round((v/total_competitors)*100, 1) if total_competitors > 0 else 0 
                      for k, v in freshness_indicators.items()}
        
        # Determine overall freshness score
        freshness_score = sum(percentages.values()) / 4
        freshness_level = "high" if freshness_score > 60 else ("medium" if freshness_score > 30 else "low")
        
        return {
            "freshness_indicators": freshness_indicators,
            "freshness_percentages": percentages,
            "overall_freshness_score": round(freshness_score, 1),
            "freshness_level": freshness_level,
            "recommendation": self._get_freshness_recommendation(freshness_level)
        }
    
    def _get_freshness_recommendation(self, freshness_level: str) -> str:
        """Get recommendation based on freshness analysis"""
        
        recommendations = {
            "high": "Competitors are focusing on current content - ensure your content includes recent developments and current year references",
            "medium": "Mixed freshness signals - consider updating content with recent information and current examples",
            "low": "Opportunity to stand out with fresh, current content that addresses recent developments"
        }
        
        return recommendations.get(freshness_level, "Focus on creating timely, relevant content")
    
    def _generate_real_insights(self, real_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real insights using Gemini API based on content patterns"""
        
        try:
            # Prepare data for Gemini analysis
            content_types = real_patterns.get("content_types", {})
            length_dist = real_patterns.get("length_distribution", {})
            structure = real_patterns.get("structure_patterns", {})
            topics = real_patterns.get("topic_coverage", {})
            freshness = real_patterns.get("content_freshness", {})
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following real competitor content patterns and provide strategic insights:
            
            Content Types Distribution:
            - Dominant type: {content_types.get('dominant_type', 'unknown')}
            - Guides: {content_types.get('type_percentages', {}).get('guides', 0)}%
            - Lists: {content_types.get('type_percentages', {}).get('lists', 0)}%
            - Tutorials: {content_types.get('type_percentages', {}).get('tutorials', 0)}%
            - Reviews: {content_types.get('type_percentages', {}).get('reviews', 0)}%
            
            Content Length Analysis:
            - Average length: {length_dist.get('average_length', 0)} words
            - Median length: {length_dist.get('median_length', 0)} words
            - Range: {length_dist.get('min_length', 0)} - {length_dist.get('max_length', 0)} words
            
            Structure Patterns:
            - Average headings: {structure.get('structure_averages', {}).get('avg_headings', 0)}
            - Average images: {structure.get('structure_averages', {}).get('avg_images', 0)}
            - Images per 1000 words: {structure.get('multimedia_usage', {}).get('images_per_1000_words', 0)}
            
            Topic Coverage:
            - Common entities: {', '.join(topics.get('common_entities', [])[:5])}
            - Topic diversity: {topics.get('coverage_depth', 'unknown')}
            
            Content Freshness:
            - Freshness level: {freshness.get('freshness_level', 'unknown')}
            - Current year mentions: {freshness.get('freshness_percentages', {}).get('current_year_mentions', 0)}%
            
            Provide 5 key strategic insights for content creation based on this real data analysis.
            Focus on actionable recommendations that leverage gaps or opportunities.
            """
            
            # Get insights from Gemini
            insights_response = self.gemini_client.generate_content(analysis_prompt)
            
            # Parse insights into structured format
            insights_list = self._parse_insights_response(insights_response)
            
            return {
                "strategic_insights": insights_list,
                "content_opportunities": self._identify_content_opportunities(real_patterns),
                "optimization_priorities": self._identify_optimization_priorities(real_patterns),
                "competitive_gaps": self._identify_competitive_gaps(real_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error generating insights with Gemini: {str(e)}")
            return {
                "error": f"Insights generation failed: {str(e)}",
                "fallback_insights": self._generate_fallback_insights(real_patterns)
            }
    
    def _parse_insights_response(self, response: str) -> List[str]:
        """Parse Gemini response into structured insights list"""
        
        insights = []
        
        # Split response into lines and extract insights
        lines = response.split('\
')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 
                        (len(line) > 2 and line[0].isdigit() and line[1] in ['.', ')'])):
                # Clean up the insight
                insight = line.lstrip('- *0123456789.)').strip()
                if len(insight) > 10:  # Only include substantial insights
                    insights.append(insight)
        
        # If parsing didn't work well, try to split by sentences
        if len(insights) < 3:
            sentences = response.split('. ')
            insights = [s.strip() + '.' for s in sentences if len(s.strip()) > 20][:5]
        
        return insights[:5]  # Return top 5 insights
    
    def _identify_content_opportunities(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify content opportunities based on real patterns"""
        
        opportunities = []
        
        content_types = patterns.get("content_types", {})
        length_dist = patterns.get("length_distribution", {})
        structure = patterns.get("structure_patterns", {})
        
        # Content type opportunities
        type_percentages = content_types.get("type_percentages", {})
        if type_percentages.get("guides", 0) < 20:
            opportunities.append("Low guide content representation - opportunity for comprehensive guides")
        if type_percentages.get("comparisons", 0) < 15:
            opportunities.append("Limited comparison content - opportunity for detailed comparisons")
        
        # Length opportunities
        avg_length = length_dist.get("average_length", 0)
        if avg_length < 1500:
            opportunities.append("Competitors use shorter content - opportunity for in-depth, comprehensive pieces")
        elif avg_length > 4000:
            opportunities.append("Very long competitor content - opportunity for concise, focused pieces")
        
        # Structure opportunities
        avg_images = structure.get("structure_averages", {}).get("avg_images", 0)
        if avg_images < 3:
            opportunities.append("Low image usage by competitors - opportunity for rich visual content")
        
        return opportunities[:4]  # Return top 4 opportunities
    
    def _identify_optimization_priorities(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify optimization priorities based on patterns"""
        
        priorities = []
        
        content_types = patterns.get("content_types", {})
        structure = patterns.get("structure_patterns", {})
        freshness = patterns.get("content_freshness", {})
        
        # Priority based on dominant content type
        dominant_type = content_types.get("dominant_type")
        if dominant_type == "guides":
            priorities.append("Focus on comprehensive, step-by-step guide format")
        elif dominant_type == "lists":
            priorities.append("Optimize for list-based content with clear rankings")
        elif dominant_type == "tutorials":
            priorities.append("Emphasize practical, actionable tutorial content")
        
        # Structure optimization
        avg_headings = structure.get("structure_averages", {}).get("avg_headings", 0)
        if avg_headings > 5:
            priorities.append("Use clear heading hierarchy with multiple section breaks")
        
        # Freshness optimization
        freshness_level = freshness.get("freshness_level", "low")
        if freshness_level in ["high", "medium"]:
            priorities.append("Include current year references and recent developments")
        
        return priorities[:3]  # Return top 3 priorities
    
    def _identify_competitive_gaps(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify competitive gaps based on analysis"""
        
        gaps = []
        
        topics = patterns.get("topic_coverage", {})
        content_types = patterns.get("content_types", {})
        structure = patterns.get("structure_patterns", {})
        
        # Topic gaps
        coverage_depth = topics.get("coverage_depth", "low")
        if coverage_depth == "low":
            gaps.append("Limited topic diversity - opportunity to cover broader range")
        
        # Content type gaps
        classification_coverage = content_types.get("classification_coverage", 0)
        if classification_coverage < 70:
            gaps.append("Many unclassified content types - opportunity for unique formats")
        
        # Structure gaps
        samples_analyzed = structure.get("samples_analyzed", 0)
        if samples_analyzed < len(patterns.get("length_distribution", {}).get("total_samples", 1)) * 0.5:
            gaps.append("Inconsistent content structure - opportunity for well-structured content")
        
        return gaps[:3]  # Return top 3 gaps
    
    def _generate_fallback_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate basic insights when Gemini analysis fails"""
        
        insights = [
            "Focus on creating content that matches or exceeds competitor length standards",
            "Ensure content structure includes appropriate heading hierarchy",
            "Consider the dominant content type in your niche for format decisions",
            "Include visual elements to enhance content engagement",
            "Keep content fresh with current examples and recent information"
        ]
        
        return insights
        
        
    def _get_freshness_recommendation(self, freshness_level: str) -> str:
        """Get recommendation based on freshness analysis"""
        
        recommendations = {
            "high": "Competitors are focusing on current content - ensure your content includes recent developments and current year references",
            "medium": "Mixed freshness signals - consider updating content with recent information and current examples",
            "low": "Opportunity to stand out with fresh, current content that addresses recent developments"
        }
        
        return recommendations.get(freshness_level, "Focus on creating timely, relevant content")
    
    def _generate_real_insights(self, real_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real insights using Gemini API based on content patterns"""
        
        try:
            # Prepare data for Gemini analysis
            content_types = real_patterns.get("content_types", {})
            length_dist = real_patterns.get("length_distribution", {})
            structure = real_patterns.get("structure_patterns", {})
            topics = real_patterns.get("topic_coverage", {})
            freshness = real_patterns.get("content_freshness", {})
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following real competitor content patterns and provide strategic insights:
            
            Content Types Distribution:
            - Dominant type: {content_types.get('dominant_type', 'unknown')}
            - Guides: {content_types.get('type_percentages', {}).get('guides', 0)}%
            - Lists: {content_types.get('type_percentages', {}).get('lists', 0)}%
            - Tutorials: {content_types.get('type_percentages', {}).get('tutorials', 0)}%
            - Reviews: {content_types.get('type_percentages', {}).get('reviews', 0)}%
            
            Content Length Analysis:
            - Average length: {length_dist.get('average_length', 0)} words
            - Median length: {length_dist.get('median_length', 0)} words
            - Range: {length_dist.get('min_length', 0)} - {length_dist.get('max_length', 0)} words
            
            Structure Patterns:
            - Average headings: {structure.get('structure_averages', {}).get('avg_headings', 0)}
            - Average images: {structure.get('structure_averages', {}).get('avg_images', 0)}
            - Images per 1000 words: {structure.get('multimedia_usage', {}).get('images_per_1000_words', 0)}
            
            Topic Coverage:
            - Common entities: {', '.join(topics.get('common_entities', [])[:5])}
            - Topic diversity: {topics.get('coverage_depth', 'unknown')}
            
            Content Freshness:
            - Freshness level: {freshness.get('freshness_level', 'unknown')}
            - Current year mentions: {freshness.get('freshness_percentages', {}).get('current_year_mentions', 0)}%
            
            Provide 5 key strategic insights for content creation based on this real data analysis.
            Focus on actionable recommendations that leverage gaps or opportunities.
            """
            
            # Get insights from Gemini
            insights_response = self.gemini_client.generate_content(analysis_prompt)
            
            # Parse insights into structured format
            insights_list = self._parse_insights_response(insights_response)
            
            return {
                "strategic_insights": insights_list,
                "content_opportunities": self._identify_content_opportunities(real_patterns),
                "optimization_priorities": self._identify_optimization_priorities(real_patterns),
                "competitive_gaps": self._identify_competitive_gaps(real_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error generating insights with Gemini: {str(e)}")
            return {
                "error": f"Insights generation failed: {str(e)}",
                "fallback_insights": self._generate_fallback_insights(real_patterns)
            }
    
    def _parse_insights_response(self, response: str) -> List[str]:
        """Parse Gemini response into structured insights list"""
        
        insights = []
        
        # Split response into lines and extract insights
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 
                        (len(line) > 2 and line[0].isdigit() and line[1] in ['.', ')'])):
                # Clean up the insight
                insight = line.lstrip('- *0123456789.)').strip()
                if len(insight) > 10:  # Only include substantial insights
                    insights.append(insight)
        
        # If parsing didn't work well, try to split by sentences
        if len(insights) < 3:
            sentences = response.split('. ')
            insights = [s.strip() + '.' for s in sentences if len(s.strip()) > 20][:5]
        
        return insights[:5]  # Return top 5 insights
    
    def _identify_content_opportunities(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify content opportunities based on real patterns"""
        
        opportunities = []
        
        content_types = patterns.get("content_types", {})
        length_dist = patterns.get("length_distribution", {})
        structure = patterns.get("structure_patterns", {})
        
        # Content type opportunities
        type_percentages = content_types.get("type_percentages", {})
        if type_percentages.get("guides", 0) < 20:
            opportunities.append("Low guide content representation - opportunity for comprehensive guides")
        if type_percentages.get("comparisons", 0) < 15:
            opportunities.append("Limited comparison content - opportunity for detailed comparisons")
        
        # Length opportunities
        avg_length = length_dist.get("average_length", 0)
        if avg_length < 1500:
            opportunities.append("Competitors use shorter content - opportunity for in-depth, comprehensive pieces")
        elif avg_length > 4000:
            opportunities.append("Very long competitor content - opportunity for concise, focused pieces")
        
        # Structure opportunities
        avg_images = structure.get("structure_averages", {}).get("avg_images", 0)
        if avg_images < 3:
            opportunities.append("Low image usage by competitors - opportunity for rich visual content")
        
        return opportunities[:4]  # Return top 4 opportunities
    
    def _identify_optimization_priorities(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify optimization priorities based on patterns"""
        
        priorities = []
        
        content_types = patterns.get("content_types", {})
        structure = patterns.get("structure_patterns", {})
        freshness = patterns.get("content_freshness", {})
        
        # Priority based on dominant content type
        dominant_type = content_types.get("dominant_type")
        if dominant_type == "guides":
            priorities.append("Focus on comprehensive, step-by-step guide format")
        elif dominant_type == "lists":
            priorities.append("Optimize for list-based content with clear rankings")
        elif dominant_type == "tutorials":
            priorities.append("Emphasize practical, actionable tutorial content")
        
        # Structure optimization
        avg_headings = structure.get("structure_averages", {}).get("avg_headings", 0)
        if avg_headings > 5:
            priorities.append("Use clear heading hierarchy with multiple section breaks")
        
        # Freshness optimization
        freshness_level = freshness.get("freshness_level", "low")
        if freshness_level in ["high", "medium"]:
            priorities.append("Include current year references and recent developments")
        
        return priorities[:3]  # Return top 3 priorities
    
    def _identify_competitive_gaps(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify competitive gaps based on analysis"""
        
        gaps = []
        
        topics = patterns.get("topic_coverage", {})
        content_types = patterns.get("content_types", {})
        structure = patterns.get("structure_patterns", {})
        
        # Topic gaps
        coverage_depth = topics.get("coverage_depth", "low")
        if coverage_depth == "low":
            gaps.append("Limited topic diversity - opportunity to cover broader range")
        
        # Content type gaps
        classification_coverage = content_types.get("classification_coverage", 0)
        if classification_coverage < 70:
            gaps.append("Many unclassified content types - opportunity for unique formats")
        
        # Structure gaps
        samples_analyzed = structure.get("samples_analyzed", 0)
        total_samples = patterns.get("length_distribution", {}).get("total_samples", 1)
        if samples_analyzed < total_samples * 0.5:
            gaps.append("Inconsistent content structure - opportunity for well-structured content")
        
        return gaps[:3]  # Return top 3 gaps
    
    def _generate_fallback_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate basic insights when Gemini analysis fails"""
        
        insights = [
            "Focus on creating content that matches or exceeds competitor length standards",
            "Ensure content structure includes appropriate heading hierarchy",
            "Consider the dominant content type in your niche for format decisions",
            "Include visual elements to enhance content engagement",
            "Keep content fresh with current examples and recent information"
        ]
        
        return insights