"""
Blueprint Generator Service - Core orchestrator for content blueprint generation.

This service combines competitor analysis, content analysis, and AI-powered
content structuring to generate comprehensive content blueprints.
"""

import logging
import time
import json
import re
import signal
import concurrent.futures
from typing import Dict, Any, List, Optional
from datetime import datetime
from functools import wraps

# Import existing analysis modules
from ..competitor_analysis_real import CompetitorAnalysisReal
from ..content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
from ..serp_feature_optimizer_real import SerpFeatureOptimizerReal
from ..utils.gemini_nlp_client import GeminiNLPClient
from ..utils.quick_competitor_analyzer import QuickCompetitorAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timeout_handler(signum, frame):
    raise TimeoutError("Blueprint generation timed out")

def with_timeout(timeout_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            except TimeoutError:
                logger.warning(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                raise
            finally:
                # Clear the alarm
                signal.alarm(0)
        return wrapper
    return decorator

class BlueprintGeneratorService:
    """
    Core service that orchestrates blueprint generation by combining
    competitor analysis, content analysis, and AI-powered content structuring.
    """
    
    def __init__(self, serpapi_key: str, gemini_api_key: str):
        """
        Initialize the blueprint generator with API credentials.
        
        Args:
            serpapi_key: SerpAPI key for search data
            gemini_api_key: Google Gemini API key for AI processing
        """
        self.serpapi_key = serpapi_key
        self.gemini_api_key = gemini_api_key
        
        # Initialize analysis services
        try:
            # Use quick analyzer to avoid hanging
            self.quick_analyzer = QuickCompetitorAnalyzer(
                serpapi_key=serpapi_key,
                gemini_key=gemini_api_key
            )
            
            self.competitor_analyzer = CompetitorAnalysisReal(
                gemini_api_key=gemini_api_key,
                serpapi_key=serpapi_key
            )
            self.content_analyzer = ContentAnalyzerEnhancedReal(
                gemini_api_key=gemini_api_key
            )
            self.serp_optimizer = SerpFeatureOptimizerReal(
                serpapi_key=serpapi_key
            )
            self.gemini_client = GeminiNLPClient(api_key=gemini_api_key)
            
            logger.info("Blueprint generator services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize blueprint generator: {str(e)}")
            raise Exception(f"Blueprint generator initialization failed: {str(e)}")
    
    @with_timeout(120)  # 2 minute timeout
    def generate_blueprint(self, keyword: str, user_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a complete content blueprint for the given keyword.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            project_id: Optional project ID to associate the blueprint with
            
        Returns:
            Dictionary containing the complete blueprint data
        """
        start_time = time.time()
        logger.info(f"Starting blueprint generation for keyword: '{keyword}' (user: {user_id})")
        
        try:
            # Step 1: Analyze competitors and SERP features
            logger.info("Step 1: Analyzing competitors and SERP features")
            competitors = self._analyze_competitors(keyword)
            serp_features = self._analyze_serp_features(keyword)
            
            # Step 2: Analyze competitor content structure
            logger.info("Step 2: Analyzing competitor content structure")
            content_insights = self._analyze_competitor_content(competitors)
            
            # Step 3: Generate heading structure using AI
            logger.info("Step 3: Generating AI-powered heading structure")
            heading_structure = self._generate_heading_structure(keyword, competitors, content_insights)
            
            # Step 4: Generate topic clusters
            logger.info("Step 4: Generating topic clusters")
            topic_clusters = self._generate_topic_clusters(keyword, competitors, serp_features)
            
            # Step 5: Compile final blueprint
            generation_time = int(time.time() - start_time)
            
            blueprint_data = {
                'keyword': keyword,
                'competitor_analysis': competitors,
                'heading_structure': heading_structure,
                'topic_clusters': topic_clusters,
                'serp_features': serp_features,
                'content_insights': content_insights,
                'generation_metadata': {
                    'created_at': datetime.utcnow().isoformat(),
                    'generation_time': generation_time,
                    'version': '1.0',
                    'components_used': ['competitor_analysis', 'content_analysis', 'serp_optimization', 'ai_generation']
                }
            }
            
            logger.info(f"Blueprint generation completed for keyword: '{keyword}' in {generation_time}s")
            return blueprint_data
            
        except Exception as e:
            logger.error(f"Error generating blueprint for keyword '{keyword}': {str(e)}")
            raise Exception(f"Blueprint generation failed: {str(e)}")
    
    def _analyze_competitors(self, keyword: str) -> Dict[str, Any]:
        """Analyze competitors for the given keyword with timeout protection."""
        try:
            # Use quick analyzer first to avoid hanging
            logger.info(f"Using quick competitor analysis for: {keyword}")
            competitors = self.quick_analyzer.analyze_competitors_quick(keyword, max_competitors=3)
            logger.info(f"Successfully analyzed competitors for keyword: {keyword}")
            return competitors
        except Exception as e:
            logger.warning(f"Quick competitor analysis failed for '{keyword}': {str(e)}")
            return self._get_fallback_competitors(keyword)
    
    def _get_fallback_competitors(self, keyword: str) -> Dict[str, Any]:
        """Get fallback competitor data when analysis fails."""
        return {
            'keyword': keyword,
            'competitors': [],
            'insights': {
                'common_topics': keyword.split() + ['guide', 'tips', 'strategy'],
                'content_length': {
                    'average': 2500,
                    'count': 0,
                    'max': 0,
                    'min': 0
                },
                'sentiment_trend': 'Positive',
                'data_quality': {
                    'competitors_analyzed': 0,
                    'content_samples': 0,
                    'entities_extracted': 0,
                    'failed_competitors': 0,
                    'sentiment_samples': 0,
                    'success_rate': 0,
                    'successful_competitors': 0
                }
            },
            'analysis_status': 'fallback'
        }
    
    def _analyze_serp_features(self, keyword: str) -> Dict[str, Any]:
        """Analyze SERP features for the given keyword."""
        try:
            serp_features = self.serp_optimizer.generate_recommendations(keyword)
            logger.info(f"Successfully analyzed SERP features for keyword: {keyword}")
            return serp_features
        except Exception as e:
            logger.warning(f"SERP feature analysis failed for '{keyword}': {str(e)}")
            return {
                'serp_features': {},
                'recommendations': [],
                'analysis_status': 'fallback',
                'error': str(e)
            }
    
    def _analyze_competitor_content(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the content structure of top competitors."""
        content_insights = {
            'avg_word_count': 0,
            'common_sections': [],
            'content_gaps': [],
            'structural_patterns': {},
            'analysis_status': 'completed'
        }
        
        if 'top_competitors' not in competitors or not competitors['top_competitors']:
            content_insights['analysis_status'] = 'no_competitors'
            return content_insights
        
        try:
            word_counts = []
            all_sections = []
            
            for competitor in competitors['top_competitors'][:3]:  # Analyze top 3
                try:
                    url = competitor.get('url', '')
                    if url:
                        analysis = self.content_analyzer.analyze_url(url)
                        
                        # Extract word count and sections
                        if 'content_analysis' in analysis:
                            content_data = analysis['content_analysis']
                            word_counts.append(content_data.get('word_count', 0))
                            
                            # Extract headings/sections
                            headings = content_data.get('headings', [])
                            all_sections.extend(headings)
                
                except Exception as e:
                    logger.warning(f"Failed to analyze competitor URL {url}: {str(e)}")
                    continue
            
            # Calculate insights
            if word_counts:
                content_insights['avg_word_count'] = sum(word_counts) // len(word_counts)
            
            # Find common sections
            if all_sections:
                section_counts = {}
                for section in all_sections:
                    section_lower = section.lower().strip()
                    section_counts[section_lower] = section_counts.get(section_lower, 0) + 1
                
                # Get sections mentioned by multiple competitors
                content_insights['common_sections'] = [
                    section for section, count in section_counts.items() 
                    if count >= 2
                ][:10]  # Top 10 common sections
            
            logger.info("Competitor content analysis completed successfully")
            
        except Exception as e:
            logger.warning(f"Content insights analysis failed: {str(e)}")
            content_insights['analysis_status'] = 'failed'
            content_insights['error'] = str(e)
        
        return content_insights
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from AI response with multiple fallback strategies."""
        if not response:
            return None
        
        try:
            # Try direct JSON parsing first
            return json.loads(response)
        except:
            pass
        
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1).strip())
        except:
            pass
        
        try:
            # Try to find JSON object between first { and last }
            first_brace = response.find('{')
            last_brace = response.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = response[first_brace:last_brace + 1]
                return json.loads(json_str)
        except:
            pass
        
        return None
    
    def _extract_paa_questions(self, serp_features: Dict[str, Any]) -> List[str]:
        """Extract People Also Ask questions from SERP features."""
        paa_questions = []
        
        try:
            if 'serp_features' in serp_features:
                serp_data = serp_features['serp_features']
                if 'people_also_ask' in serp_data:
                    paa_data = serp_data['people_also_ask']
                    if isinstance(paa_data, dict) and 'data' in paa_data:
                        paa_questions = [q.get('question', '') for q in paa_data['data'][:5]]
        except Exception as e:
            logger.warning(f"Failed to extract PAA questions: {str(e)}")
        
        return [q for q in paa_questions if q.strip()]
    
    def _generate_heading_structure(self, keyword: str, competitors: Dict[str, Any], content_insights: Dict[str, Any]) -> Dict[str, Any]:
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
            heading_data = self._parse_json_response(ai_response)
            
            if heading_data and 'h1' in heading_data:
                logger.info("AI heading structure generated successfully")
                return heading_data
            else:
                logger.warning("AI response parsing failed, using fallback")
                return self._generate_fallback_heading_structure(keyword, common_sections)
                
        except Exception as e:
            logger.warning(f"AI heading generation failed: {str(e)}, using fallback")
            return self._generate_fallback_heading_structure(keyword, common_sections)
    
    def _generate_topic_clusters(self, keyword: str, competitors: Dict[str, Any], serp_features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate topic clusters based on competitor analysis and SERP features."""
        
        try:
            # Extract People Also Ask questions
            paa_questions = self._extract_paa_questions(serp_features)
            
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
            topic_data = self._parse_json_response(ai_response)
            
            if topic_data and 'primary_cluster' in topic_data:
                logger.info("AI topic clustering generated successfully")
                return topic_data
            else:
                logger.warning("AI topic clustering parsing failed, using fallback")
                return self._generate_fallback_topic_clusters(keyword, paa_questions)
                
        except Exception as e:
            logger.warning(f"AI topic clustering failed: {str(e)}, using fallback")
            return self._generate_fallback_topic_clusters(keyword, [])
    
    def _generate_fallback_heading_structure(self, keyword: str, common_sections: List[str]) -> Dict[str, Any]:
        """Generate a basic heading structure when AI fails."""
        keyword_title = keyword.title()
        
        h2_sections = [
            {
                "title": f"What is {keyword_title}?",
                "h3_subsections": ["Definition and Overview", "Key Benefits and Importance"]
            },
            {
                "title": f"How to Implement {keyword_title}",
                "h3_subsections": ["Step-by-Step Process", "Best Practices and Tips"]
            },
            {
                "title": f"{keyword_title} Strategies and Techniques",
                "h3_subsections": ["Advanced Methods", "Common Mistakes to Avoid"]
            },
            {
                "title": f"Measuring {keyword_title} Success",
                "h3_subsections": ["Key Performance Indicators", "Tools and Analytics"]
            }
        ]
        
        # Include common sections if available
        if common_sections:
            for section in common_sections[:2]:  # Add up to 2 common sections
                h2_sections.append({
                    "title": section.title(),
                    "h3_subsections": ["Key Concepts", "Implementation Guide"]
                })
        
        return {
            "h1": f"Complete Guide to {keyword_title}: Strategies, Tips, and Best Practices",
            "h2_sections": h2_sections[:6]  # Limit to 6 sections
        }
    
    def _generate_fallback_topic_clusters(self, keyword: str, paa_questions: List[str]) -> Dict[str, Any]:
        """Generate basic topic clusters when AI fails."""
        primary_cluster = [keyword, f"{keyword} guide", f"{keyword} tips", f"best {keyword} practices"]
        
        secondary_clusters = {
            "fundamentals": [f"{keyword} basics", f"{keyword} definition", f"introduction to {keyword}"],
            "implementation": [f"how to {keyword}", f"{keyword} process", f"{keyword} steps"],
            "advanced": [f"{keyword} strategies", f"advanced {keyword}", f"{keyword} optimization"],
            "tools": [f"{keyword} tools", f"best {keyword} software", f"{keyword} resources"]
        }
        
        # Add PAA-based clusters if available
        if paa_questions:
            secondary_clusters["common_questions"] = paa_questions[:3]
        
        related_keywords = [
            f"{keyword} guide", f"best {keyword}", f"{keyword} tips",
            f"{keyword} strategies", f"how to {keyword}", f"{keyword} best practices"
        ]
        
        return {
            "primary_cluster": primary_cluster,
            "secondary_clusters": secondary_clusters,
            "related_keywords": related_keywords
        }
    
    def validate_blueprint_data(self, blueprint_data: Dict[str, Any]) -> bool:
        """
        Validate that the generated blueprint contains required components.
        
        Args:
            blueprint_data: Generated blueprint data
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['keyword', 'competitor_analysis', 'heading_structure', 'topic_clusters']
        
        for field in required_fields:
            if field not in blueprint_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate heading structure
        heading_structure = blueprint_data['heading_structure']
        if not isinstance(heading_structure, dict) or 'h1' not in heading_structure:
            logger.error("Invalid heading structure format")
            return False
        
        # Validate topic clusters
        topic_clusters = blueprint_data['topic_clusters']
        if not isinstance(topic_clusters, dict) or 'primary_cluster' not in topic_clusters:
            logger.error("Invalid topic clusters format")
            return False
        
        return True
