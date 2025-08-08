"""
Realtime Blueprint Generator Service - Blueprint generation with WebSocket progress updates.

This service extends the standard blueprint generator to provide real-time progress
updates through WebSocket connections during the generation process.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import the base blueprint generator and WebSocket service
from .blueprint_generator import BlueprintGeneratorService
from .websocket_service import get_websocket_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeBlueprintGenerator(BlueprintGeneratorService):
    """
    Enhanced blueprint generator with real-time WebSocket progress updates.
    
    This service provides the same functionality as the base BlueprintGeneratorService
    but adds real-time progress tracking and WebSocket communication capabilities.
    """
    
    def __init__(self, serpapi_key: str, gemini_api_key: str):
        """
        Initialize the realtime blueprint generator.
        
        Args:
            serpapi_key: SerpAPI key for search data
            gemini_api_key: Google Gemini API key for AI processing
        """
        super().__init__(serpapi_key, gemini_api_key)
        self.websocket_service = get_websocket_service()
        
        if self.websocket_service:
            logger.info("Realtime blueprint generator initialized with WebSocket support")
        else:
            logger.warning("WebSocket service not available - running without real-time updates")
    
    def generate_blueprint_realtime(self, keyword: str, user_id: str,
                                   project_id: Optional[str] = None,
                                   competitors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a complete content blueprint with real-time progress updates.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            project_id: Optional project ID to associate the blueprint with
            competitors: (Optional) Precomputed competitor analysis data
            
        Returns:
            Dictionary containing the complete blueprint data
        """
        # Generate a unique blueprint ID for this session
        blueprint_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Starting realtime blueprint generation for keyword: '{keyword}' "
                   f"(user: {user_id}, blueprint_id: {blueprint_id})")
        
        # Start WebSocket session if available
        if self.websocket_service:
            self.websocket_service.start_blueprint_session(blueprint_id, user_id, total_steps=6)
        
        try:
            # Step 1: Comprehensive analysis
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 1, "comprehensive_analysis",
                    "Analyzing competitors and SERP features..."
                )
            
            logger.info("Step 1: Performing comprehensive analysis")
            if competitors is not None:
                analysis_data = self.analyzer.get_comprehensive_analysis(keyword, competitors=competitors)
            else:
                analysis_data = self.analyzer.get_comprehensive_analysis(keyword)
            
            # Extract components from analysis
            competitors_data = analysis_data.get('competitors', {})
            serp_features = analysis_data.get('serp_features', {})
            content_insights = analysis_data.get('content_insights', {})
            content_gaps = analysis_data.get('content_gaps', {})
            
            if self.websocket_service:
                self.websocket_service.complete_step(
                    blueprint_id, 1, "comprehensive_analysis",
                    {"competitors_found": len(competitors_data.get('competitors', []))}
                )
            
            # Step 2: Generate AI-powered content structure
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 2, "heading_structure",
                    "Generating AI-powered heading structure..."
                )
            
            logger.info("Step 2: Generating AI-powered content structure")
            heading_structure = self.ai_generator.generate_heading_structure(
                keyword, competitors_data, content_insights
            )
            
            if self.websocket_service:
                self.websocket_service.complete_step(
                    blueprint_id, 2, "heading_structure",
                    {"headings_generated": len(heading_structure.get('h2_sections', []))}
                )
            
            # Step 3: Generate topic clusters
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 3, "topic_clusters",
                    "Creating topic clusters and keyword groups..."
                )
            
            logger.info("Step 3: Generating topic clusters")
            topic_clusters = self.ai_generator.generate_topic_clusters(
                keyword, competitors_data, serp_features
            )
            
            if self.websocket_service:
                self.websocket_service.complete_step(
                    blueprint_id, 3, "topic_clusters",
                    {"clusters_created": len(topic_clusters.get('secondary_clusters', {}))}
                )
            
            # Step 4: Generate detailed content outline
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 4, "content_outline",
                    "Building detailed content outline..."
                )
            
            logger.info("Step 4: Generating detailed content outline")
            content_outline = self.ai_generator.generate_content_outline(
                keyword, heading_structure, topic_clusters
            )
            
            if self.websocket_service:
                self.websocket_service.complete_step(
                    blueprint_id, 4, "content_outline",
                    {"outline_sections": len(content_outline) if isinstance(content_outline, list) else 1}
                )
            
            # Step 5: Generate SEO recommendations
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 5, "seo_recommendations",
                    "Generating SEO recommendations and optimization tips..."
                )
            
            logger.info("Step 5: Generating SEO recommendations")
            seo_recommendations = self.ai_generator.generate_seo_recommendations(
                keyword, competitors_data, serp_features
            )
            
            if self.websocket_service:
                self.websocket_service.complete_step(
                    blueprint_id, 5, "seo_recommendations",
                    {"recommendations_count": len(seo_recommendations) if isinstance(seo_recommendations, list) else 1}
                )
            
            # Step 6: Compile final blueprint
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 6, "final_compilation",
                    "Compiling final blueprint and validating results..."
                )
            
            # Import required utilities
            from .blueprint_utils import validate_blueprint_data, is_google_apis_enabled
            from utils.google_apis.migration_manager import MigrationManager as get_migration_manager
            
            generation_time = int(time.time() - start_time)
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            blueprint_data = {
                'id': blueprint_id,  # Include the blueprint ID
                'keyword': keyword,
                'competitor_analysis': competitors_data,
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
                    'version': '2.0-realtime',
                    'blueprint_id': blueprint_id,
                    'components_used': [
                        'competitor_analysis', 'content_analysis', 'serp_optimization',
                        'ai_generation', 'gap_analysis', 'seo_recommendations', 'realtime_updates'
                    ],
                    'analysis_quality': analysis_data.get('analysis_metadata', {}).get('analysis_quality', 'medium'),
                    'realtime_enabled': True
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
            if validate_blueprint_data(blueprint_data):
                if self.websocket_service:
                    self.websocket_service.complete_step(
                        blueprint_id, 6, "final_compilation",
                        {"validation_passed": True, "blueprint_size": len(str(blueprint_data))}
                    )
                    
                    # Send completion notification
                    self.websocket_service.complete_generation(
                        blueprint_id, blueprint_data, generation_time
                    )
                
                logger.info(f"Realtime blueprint generation completed for keyword: '{keyword}' "
                           f"(blueprint_id: {blueprint_id}) in {generation_time}s")
                return blueprint_data
            else:
                raise Exception("Generated blueprint failed validation")
        
        except Exception as e:
            error_message = f"Blueprint generation failed: {str(e)}"
            logger.error(f"Error in realtime blueprint generation for keyword '{keyword}': {error_message}")
            
            # Notify WebSocket clients of failure
            if self.websocket_service:
                self.websocket_service.fail_generation(
                    blueprint_id, error_message,
                    {"keyword": keyword, "user_id": user_id, "error_type": type(e).__name__}
                )
            
            raise Exception(error_message)
    
    def generate_quick_blueprint_realtime(self, keyword: str, user_id: str) -> Dict[str, Any]:
        """
        Generate a quick blueprint with real-time updates.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            
        Returns:
            Dictionary containing the quick blueprint data
        """
        # Generate a unique blueprint ID for this session
        blueprint_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Starting realtime quick blueprint generation for keyword: '{keyword}' "
                   f"(user: {user_id}, blueprint_id: {blueprint_id})")
        
        # Start WebSocket session with fewer steps for quick generation
        if self.websocket_service:
            self.websocket_service.start_blueprint_session(blueprint_id, user_id, total_steps=4)
        
        try:
            # Step 1: Quick competitor analysis
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 1, "competitor_analysis",
                    "Analyzing top competitors..."
                )
            
            competitors = self.analyzer.analyze_competitors(keyword)
            
            if self.websocket_service:
                self.websocket_service.complete_step(blueprint_id, 1, "competitor_analysis")
            
            # Step 2: Quick SERP analysis
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 2, "serp_analysis",
                    "Analyzing SERP features..."
                )
            
            serp_features = self.analyzer.analyze_serp_features(keyword)
            
            if self.websocket_service:
                self.websocket_service.complete_step(blueprint_id, 2, "serp_analysis")
            
            # Step 3: Basic content insights
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 3, "content_insights",
                    "Extracting content insights..."
                )
            
            content_insights = self.analyzer.analyze_competitor_content(competitors)
            
            # Generate basic structures
            heading_structure = self.ai_generator.generate_heading_structure(
                keyword, competitors, content_insights
            )
            topic_clusters = self.ai_generator.generate_topic_clusters(
                keyword, competitors, serp_features
            )
            
            if self.websocket_service:
                self.websocket_service.complete_step(blueprint_id, 3, "content_insights")
            
            # Step 4: Final compilation
            if self.websocket_service:
                self.websocket_service.update_progress(
                    blueprint_id, 4, "final_compilation",
                    "Compiling quick blueprint..."
                )
            
            from .blueprint_utils import is_google_apis_enabled
            from utils.google_apis.migration_manager import MigrationManager as get_migration_manager
            
            generation_time = int(time.time() - start_time)
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            quick_blueprint = {
                'id': blueprint_id,
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
                    'version': '2.0-quick-realtime',
                    'blueprint_id': blueprint_id,
                    'components_used': [
                        'competitor_analysis', 'content_analysis', 'serp_optimization', 
                        'ai_generation', 'realtime_updates'
                    ],
                    'blueprint_type': 'quick',
                    'realtime_enabled': True
                },
                'google_apis_status': {
                    'enabled': google_apis_enabled,
                    'migration_manager_available': bool(migration_manager),
                    'processing_method': 'google_apis' if google_apis_enabled and migration_manager else 'fallback_apis',
                    'blueprint_type': 'quick'
                }
            }
            
            if self.websocket_service:
                self.websocket_service.complete_step(blueprint_id, 4, "final_compilation")
                self.websocket_service.complete_generation(blueprint_id, quick_blueprint, generation_time)
            
            logger.info(f"Realtime quick blueprint generation completed for keyword: '{keyword}' "
                       f"(blueprint_id: {blueprint_id}) in {generation_time}s")
            return quick_blueprint
        
        except Exception as e:
            error_message = f"Quick blueprint generation failed: {str(e)}"
            logger.error(f"Error in realtime quick blueprint generation for keyword '{keyword}': {error_message}")
            
            # Notify WebSocket clients of failure
            if self.websocket_service:
                self.websocket_service.fail_generation(
                    blueprint_id, error_message,
                    {"keyword": keyword, "user_id": user_id, "error_type": type(e).__name__}
                )
            
            raise Exception(error_message)
    
    def send_progress_update(self, blueprint_id: str, message: str, 
                           details: Optional[Dict[str, Any]] = None) -> None:
        """
        Send a custom progress update to WebSocket clients.
        
        Args:
            blueprint_id: Blueprint identifier
            message: Progress message
            details: Optional additional details
        """
        if self.websocket_service:
            self.websocket_service.send_custom_message(
                blueprint_id, 'custom_progress',
                {'message': message, 'details': details or {}}
            )
    
    def get_realtime_status(self) -> Dict[str, Any]:
        """
        Get the current status of the realtime service.
        
        Returns:
            Service status including WebSocket information
        """
        base_status = self.get_service_status()
        
        # Add WebSocket service information
        websocket_status = {
            'websocket_service_available': self.websocket_service is not None,
            'active_sessions': len(self.websocket_service.get_active_sessions()) if self.websocket_service else 0,
            'realtime_features_enabled': True
        }
        
        if self.websocket_service:
            websocket_status['active_session_ids'] = list(self.websocket_service.get_active_sessions().keys())
        
        base_status['realtime_status'] = websocket_status
        base_status['service_name'] = 'RealtimeBlueprintGenerator'
        base_status['capabilities'].extend(['realtime_updates', 'websocket_communication', 'progress_tracking'])
        
        return base_status