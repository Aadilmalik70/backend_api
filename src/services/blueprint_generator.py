"""
Blueprint Generator Service - Core orchestrator for content blueprint generation.

This service combines competitor analysis, content analysis, and AI-powered
content structuring to generate comprehensive content blueprints.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

# Import refactored modules
from .blueprint_analyzer import BlueprintAnalyzer
from .blueprint_ai_generator import BlueprintAIGenerator
from .blueprint_utils import validate_blueprint_data, is_google_apis_enabled
from utils.google_apis.migration_manager import MigrationManager as get_migration_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Initialize components
        try:
            self.analyzer = BlueprintAnalyzer(
                serpapi_key=serpapi_key,
                gemini_api_key=gemini_api_key
            )
            
            self.ai_generator = BlueprintAIGenerator(
                gemini_api_key=gemini_api_key
            )
            
            logger.info("Blueprint generator services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize blueprint generator: {str(e)}")
            raise Exception(f"Blueprint generator initialization failed: {str(e)}")
    
    def generate_blueprint(self, keyword: str, user_id: str,
                          project_id: Optional[str] = None,
                          competitors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a complete content blueprint for the given keyword.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            project_id: Optional project ID to associate the blueprint with
            competitors: (Optional) Precomputed competitor analysis data
            
        Returns:
            Dictionary containing the complete blueprint data
        """
        start_time = time.time()
        logger.info(f"Starting blueprint generation for keyword: '{keyword}' (user: {user_id})")
        
        try:
            # Step 1: Comprehensive analysis
            logger.info("Step 1: Performing comprehensive analysis")
            if competitors is not None:
                # Use provided competitors, avoid redundant analysis
                analysis_data = self.analyzer.get_comprehensive_analysis(keyword, competitors=competitors)
            else:
                analysis_data = self.analyzer.get_comprehensive_analysis(keyword)
            
            # Extract components from analysis
            competitors_data = analysis_data.get('competitors', {})
            serp_features = analysis_data.get('serp_features', {})
            content_insights = analysis_data.get('content_insights', {})
            content_gaps = analysis_data.get('content_gaps', {})
            
            # Step 2: Generate AI-powered content structure
            logger.info("Step 2: Generating AI-powered content structure")
            heading_structure = self.ai_generator.generate_heading_structure(
                keyword, competitors_data, content_insights
            )
            
            # Step 3: Generate topic clusters
            logger.info("Step 3: Generating topic clusters")
            topic_clusters = self.ai_generator.generate_topic_clusters(
                keyword, competitors_data, serp_features
            )
            
            # Step 4: Generate detailed content outline
            logger.info("Step 4: Generating detailed content outline")
            content_outline = self.ai_generator.generate_content_outline(
                keyword, heading_structure, topic_clusters
            )
            
            # Step 5: Generate SEO recommendations
            logger.info("Step 5: Generating SEO recommendations")
            seo_recommendations = self.ai_generator.generate_seo_recommendations(
                keyword, competitors_data, serp_features
            )
            
            # Step 6: Compile final blueprint with Google APIs status
            generation_time = int(time.time() - start_time)
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            blueprint_data = {
                'keyword': keyword,
                'competitor_analysis': competitors,
                'heading_structure': heading_structure,
                'topic_clusters': topic_clusters,
                'content_outline': content_outline,
                'seo_recommendations': seo_recommendations,
                'content_insights': content_insights,
                'content_gaps': content_gaps,
                'serp_features': serp_features,
                'generation_metadata': {
                    'created_at': datetime.utcnow().isoformat(),
                    'generation_time': generation_time,
                    'user_id': user_id,
                    'project_id': project_id,
                    'version': '2.0',
                    'components_used': [
                        'competitor_analysis', 'content_analysis', 'serp_optimization',
                        'ai_generation', 'gap_analysis', 'seo_recommendations'
                    ],
                    'analysis_quality': analysis_data.get('analysis_metadata', {}).get('analysis_quality', 'medium')
                },
                'google_apis_status': {
                    'enabled': google_apis_enabled,
                    'migration_manager_available': bool(migration_manager),
                    'apis_used': [
                        'Custom Search API' if google_apis_enabled else 'SerpAPI',
                        'Knowledge Graph API' if google_apis_enabled else 'Fallback Analysis',
                        'Natural Language API' if google_apis_enabled else 'Gemini API',
                        'Gemini API'  # Always used for AI generation
                    ],
                    'fallback_available': bool(self.serpapi_key),
                    'processing_method': 'google_apis' if google_apis_enabled and migration_manager else 'fallback_apis'
                }
            }
            
            # Validate the blueprint
            if self.validate_blueprint_data(blueprint_data):
                logger.info(f"Blueprint generation completed for keyword: '{keyword}' in {generation_time}s")
                return blueprint_data
            else:
                raise Exception("Generated blueprint failed validation")
            
        except Exception as e:
            logger.error(f"Error generating blueprint for keyword '{keyword}': {str(e)}")
            raise Exception(f"Blueprint generation failed: {str(e)}")
    
    def generate_quick_blueprint(self, keyword: str, user_id: str) -> Dict[str, Any]:
        """
        Generate a quick blueprint with essential components only.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            
        Returns:
            Dictionary containing the quick blueprint data
        """
        start_time = time.time()
        logger.info(f"Starting quick blueprint generation for keyword: '{keyword}' (user: {user_id})")
        
        try:
            # Quick competitor analysis
            competitors = self.analyzer.analyze_competitors(keyword)
            
            # Quick SERP analysis
            serp_features = self.analyzer.analyze_serp_features(keyword)
            
            # Basic content insights
            content_insights = self.analyzer.analyze_competitor_content(competitors)
            
            # Generate basic heading structure
            heading_structure = self.ai_generator.generate_heading_structure(
                keyword, competitors, content_insights
            )
            
            # Generate basic topic clusters
            topic_clusters = self.ai_generator.generate_topic_clusters(
                keyword, competitors, serp_features
            )
            
            generation_time = int(time.time() - start_time)
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            quick_blueprint = {
                'keyword': keyword,
                'competitor_analysis': competitors,
                'heading_structure': heading_structure,
                'topic_clusters': topic_clusters,
                'content_insights': content_insights,
                'serp_features': serp_features,
                'generation_metadata': {
                    'created_at': datetime.utcnow().isoformat(),
                    'generation_time': generation_time,
                    'user_id': user_id,
                    'version': '2.0-quick',
                    'components_used': [
                        'competitor_analysis', 'content_analysis', 'serp_optimization', 'ai_generation'
                    ],
                    'blueprint_type': 'quick'
                },
                'google_apis_status': {
                    'enabled': google_apis_enabled,
                    'migration_manager_available': bool(migration_manager),
                    'processing_method': 'google_apis' if google_apis_enabled and migration_manager else 'fallback_apis',
                    'blueprint_type': 'quick'
                }
            }
            
            logger.info(f"Quick blueprint generation completed for keyword: '{keyword}' in {generation_time}s")
            return quick_blueprint
            
        except Exception as e:
            logger.error(f"Error generating quick blueprint for keyword '{keyword}': {str(e)}")
            raise Exception(f"Quick blueprint generation failed: {str(e)}")
    
    def validate_blueprint_data(self, blueprint_data: Dict[str, Any]) -> bool:
        """
        Validate that the generated blueprint contains required components.
        
        Args:
            blueprint_data: Generated blueprint data
            
        Returns:
            True if valid, False otherwise
        """
        return validate_blueprint_data(blueprint_data)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the current status of the blueprint generator service.
        
        Returns:
            Service status information
        """
        try:
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            status = {
                'service_name': 'BlueprintGeneratorService',
                'version': '2.0',
                'status': 'operational',
                'components': {
                    'analyzer': 'initialized' if hasattr(self, 'analyzer') else 'not_initialized',
                    'ai_generator': 'initialized' if hasattr(self, 'ai_generator') else 'not_initialized'
                },
                'api_keys': {
                    'serpapi_configured': bool(self.serpapi_key),
                    'gemini_configured': bool(self.gemini_api_key)
                },
                'google_apis': {
                    'enabled': google_apis_enabled,
                    'migration_manager_available': bool(migration_manager),
                    'processing_method': 'google_apis' if google_apis_enabled and migration_manager else 'fallback_apis'
                },
                'capabilities': [
                    'competitor_analysis',
                    'content_analysis', 
                    'serp_optimization',
                    'ai_content_generation',
                    'blueprint_validation'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Check if all components are ready
            if (status['components']['analyzer'] == 'initialized' and 
                status['components']['ai_generator'] == 'initialized' and
                (google_apis_enabled or (status['api_keys']['serpapi_configured'] and 
                status['api_keys']['gemini_configured']))):
                status['overall_status'] = 'fully_operational'
            else:
                status['overall_status'] = 'limited_functionality'
                status['status'] = 'degraded'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")
            return {
                'service_name': 'BlueprintGeneratorService',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
