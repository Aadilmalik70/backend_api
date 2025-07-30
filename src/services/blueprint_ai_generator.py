"""
Blueprint AI Generator - AI-powered content generation methods.

This module handles AI-powered generation of heading structures, topic clusters,
and content recommendations using Gemini API.
"""

import logging
from typing import Dict, Any, List
from utils.gemini_nlp_client import GeminiNLPClient
from .blueprint_utils import (
    parse_json_response, 
    generate_fallback_heading_structure,
    generate_fallback_topic_clusters,
    extract_paa_questions
)

logger = logging.getLogger(__name__)

class BlueprintAIGenerator:
    """
    AI-powered generator for content blueprints using Gemini API.
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the AI generator with Gemini API.
        
        Args:
            gemini_api_key: Google Gemini API key for AI processing
        """
        self.gemini_client = GeminiNLPClient(api_key=gemini_api_key)
        logger.info("Blueprint AI generator initialized successfully")
    
    def generate_heading_structure(self, keyword: str, competitors: Dict[str, Any], 
                                 content_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommended heading structure using AI."""
        
        try:
            # Prepare context for AI
            competitor_info = ""
            if 'top_competitors' in competitors and competitors['top_competitors']:
                for i, comp in enumerate(competitors['top_competitors'][:3], 1):
                    competitor_info += f"\n{i}. {comp.get('title', 'N/A')}"
            
            common_sections = content_insights.get('common_sections', [])
            
            prompt = f"""
            Create a content heading structure for the keyword "{keyword}".
            
            Top competitor titles:
            {competitor_info}
            
            Common sections found in competitors:
            {', '.join(common_sections[:5]) if common_sections else 'None found'}
            
            Generate a comprehensive heading structure with:
            1. One H1 title
            2. 4-6 H2 main sections
            3. 2-3 H3 subsections under each H2
            
            Return ONLY a JSON object with this structure:
            {{
                "h1": "Main title here",
                "h2_sections": [
                    {{
                        "title": "H2 title",
                        "h3_subsections": ["H3 title 1", "H3 title 2"]
                    }}
                ]
            }}
            """
            
            ai_response = self.gemini_client.generate_content(prompt)
            heading_data = parse_json_response(ai_response)
            
            if heading_data and 'h1' in heading_data:
                logger.info("AI heading structure generated successfully")
                return heading_data
            else:
                logger.warning("AI response parsing failed, using fallback")
                return generate_fallback_heading_structure(keyword, common_sections)
                
        except Exception as e:
            logger.warning(f"AI heading generation failed: {str(e)}, using fallback")
            return generate_fallback_heading_structure(keyword, common_sections)
    
    def generate_topic_clusters(self, keyword: str, competitors: Dict[str, Any], 
                              serp_features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate topic clusters based on competitor analysis and SERP features."""
        
        try:
            # Extract People Also Ask questions
            paa_questions = extract_paa_questions(serp_features)
            
            # Extract competitor titles
            competitor_titles = []
            if 'top_competitors' in competitors and competitors['top_competitors']:
                competitor_titles = [comp.get('title', '') for comp in competitors['top_competitors'][:5]]
            
            prompt = f"""
            Based on the keyword "{keyword}", create topic clusters for content planning.
            
            People Also Ask questions:
            {chr(10).join(paa_questions[:5]) if paa_questions else 'None found'}
            
            Competitor titles:
            {chr(10).join(competitor_titles[:5]) if competitor_titles else 'None found'}
            
            Generate topic clusters with:
            1. Primary cluster (main topics)
            2. Secondary clusters (supporting topics)
            3. Related keywords for each cluster
            
            Return ONLY a JSON object:
            {{
                "primary_cluster": ["topic1", "topic2", "topic3"],
                "secondary_clusters": {{
                    "cluster_name_1": ["subtopic1", "subtopic2"],
                    "cluster_name_2": ["subtopic1", "subtopic2"]
                }},
                "related_keywords": ["keyword1", "keyword2", "keyword3"]
            }}
            """
            
            ai_response = self.gemini_client.generate_content(prompt)
            topic_data = parse_json_response(ai_response)
            
            if topic_data and 'primary_cluster' in topic_data:
                logger.info("AI topic clustering generated successfully")
                return topic_data
            else:
                logger.warning("AI topic clustering parsing failed, using fallback")
                return generate_fallback_topic_clusters(keyword, paa_questions)
                
        except Exception as e:
            logger.warning(f"AI topic clustering failed: {str(e)}, using fallback")
            return generate_fallback_topic_clusters(keyword, [])
    
    def generate_content_outline(self, keyword: str, heading_structure: Dict[str, Any], 
                               topic_clusters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed content outline using AI."""
        
        try:
            # Prepare heading information
            h1_title = heading_structure.get('h1', '')
            h2_sections = heading_structure.get('h2_sections', [])
            
            # Prepare topic information
            primary_topics = topic_clusters.get('primary_cluster', [])
            secondary_clusters = topic_clusters.get('secondary_clusters', {})
            
            prompt = f"""
            Create a detailed content outline for the keyword "{keyword}".
            
            Main Title: {h1_title}
            
            Section Structure:
            {chr(10).join([f"- {section.get('title', '')}" for section in h2_sections[:5]])}
            
            Primary Topics: {', '.join(primary_topics[:5])}
            
            Generate a detailed outline with:
            1. Introduction paragraph
            2. Main content points for each section
            3. Key takeaways
            4. Call-to-action suggestions
            
            Return ONLY a JSON object:
            {{
                "introduction": "Introduction paragraph here",
                "section_outlines": [
                    {{
                        "section_title": "Section title",
                        "content_points": ["Point 1", "Point 2", "Point 3"],
                        "word_count_estimate": 300
                    }}
                ],
                "key_takeaways": ["Takeaway 1", "Takeaway 2"],
                "cta_suggestions": ["CTA 1", "CTA 2"]
            }}
            """
            
            ai_response = self.gemini_client.generate_content(prompt)
            outline_data = parse_json_response(ai_response)
            
            if outline_data and 'introduction' in outline_data:
                logger.info("AI content outline generated successfully")
                return outline_data
            else:
                logger.warning("AI outline generation failed, using fallback")
                return self._generate_fallback_outline(keyword, h1_title, h2_sections)
                
        except Exception as e:
            logger.warning(f"AI outline generation failed: {str(e)}, using fallback")
            return self._generate_fallback_outline(keyword, h1_title if 'h1_title' in locals() else keyword, 
                                                 h2_sections if 'h2_sections' in locals() else [])
    
    def generate_seo_recommendations(self, keyword: str, competitors: Dict[str, Any], 
                                   serp_features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO optimization recommendations using AI."""
        
        try:
            # Extract competitor insights
            competitor_insights = competitors.get('insights', {})
            avg_content_length = competitor_insights.get('content_length', {}).get('average', 0)
            
            # Extract SERP feature data
            serp_data = serp_features.get('serp_features', {})
            
            # Handle serp_data being a list or dict
            serp_features_text = 'None detected'
            if isinstance(serp_data, dict) and serp_data:
                serp_features_text = ', '.join(serp_data.keys())
            elif isinstance(serp_data, list) and serp_data:
                serp_features_text = ', '.join([str(item) for item in serp_data])
            
            prompt = f"""
            Generate SEO optimization recommendations for the keyword "{keyword}".
            
            Competitor Analysis:
            - Average content length: {avg_content_length} words
            - Number of competitors analyzed: {len(competitors.get('competitors', []))}
            
            SERP Features Present:
            {serp_features_text}
            
            Generate specific SEO recommendations including:
            1. Target content length
            2. Technical SEO elements
            3. Content optimization strategies
            4. SERP feature optimization
            
            Return ONLY a JSON object:
            {{
                "content_optimization": {{
                    "target_word_count": 2500,
                    "readability_level": "intermediate",
                    "content_structure": ["Use subheadings", "Include lists"]
                }},
                "technical_seo": {{
                    "title_tag": "Optimized title",
                    "meta_description": "Meta description",
                    "schema_markup": ["Article", "FAQPage"]
                }},
                "serp_optimization": ["Feature 1", "Feature 2"],
                "ranking_factors": ["Factor 1", "Factor 2"]
            }}
            """
            
            ai_response = self.gemini_client.generate_content(prompt)
            seo_data = parse_json_response(ai_response)
            
            if seo_data and 'content_optimization' in seo_data:
                logger.info("AI SEO recommendations generated successfully")
                return seo_data
            else:
                logger.warning("AI SEO generation failed, using fallback")
                return self._generate_fallback_seo_recommendations(keyword, avg_content_length)
                
        except Exception as e:
            logger.warning(f"AI SEO generation failed: {str(e)}, using fallback")
            return self._generate_fallback_seo_recommendations(keyword, 0)
    
    def _generate_fallback_outline(self, keyword: str, title: str, sections: List[Dict]) -> Dict[str, Any]:
        """Generate fallback content outline when AI fails."""
        return {
            "introduction": f"This comprehensive guide covers everything you need to know about {keyword}, including strategies, best practices, and implementation tips.",
            "section_outlines": [
                {
                    "section_title": section.get('title', f"Section about {keyword}"),
                    "content_points": [
                        f"Key concepts related to {keyword}",
                        f"Best practices for {keyword}",
                        f"Common challenges and solutions"
                    ],
                    "word_count_estimate": 400
                } for section in sections[:4]
            ],
            "key_takeaways": [
                f"Understanding {keyword} is crucial for success",
                f"Implementation requires careful planning",
                f"Regular monitoring and optimization are essential"
            ],
            "cta_suggestions": [
                f"Start implementing {keyword} strategies today",
                f"Get expert help with {keyword} optimization"
            ]
        }
    
    def _generate_fallback_seo_recommendations(self, keyword: str, avg_content_length: int) -> Dict[str, Any]:
        """Generate fallback SEO recommendations when AI fails."""
        target_length = max(avg_content_length + 500, 2000) if avg_content_length > 0 else 2500
        
        return {
            "content_optimization": {
                "target_word_count": target_length,
                "readability_level": "intermediate",
                "content_structure": [
                    "Use clear H2 and H3 headings",
                    "Include bullet points and numbered lists",
                    "Add relevant images and diagrams",
                    "Include internal and external links"
                ]
            },
            "technical_seo": {
                "title_tag": f"{keyword.title()} - Complete Guide and Best Practices",
                "meta_description": f"Learn everything about {keyword} with our comprehensive guide. Discover strategies, tips, and best practices for {keyword} optimization.",
                "schema_markup": ["Article", "HowTo", "FAQPage"]
            },
            "serp_optimization": [
                "Target featured snippets with clear answers",
                "Create FAQ sections for People Also Ask",
                "Optimize for local search if applicable",
                "Include relevant images with alt text"
            ],
            "ranking_factors": [
                "High-quality, comprehensive content",
                "Strong topic authority and expertise",
                "Good user experience and page speed",
                "Relevant internal linking structure"
            ]
        }
