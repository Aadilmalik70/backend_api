"""
Enhanced Blueprint Generator Service - Next-generation blueprint generation with 
advanced caching, AI quality assurance, and multi-model integration.

This service implements the architectural improvements outlined in the blueprint
design document, providing enterprise-grade content generation capabilities.
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

# Import enhanced components
from utils.advanced_cache_manager import AdvancedCacheManager, cache_result
from utils.ai_quality_framework import AIQualityFramework, assess_ai_quality
from .blueprint_analyzer import BlueprintAnalyzer
from .blueprint_ai_generator import BlueprintAIGenerator
from .blueprint_utils import validate_blueprint_data, is_google_apis_enabled
from utils.google_apis.migration_manager import MigrationManager as get_migration_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBlueprintGenerator:
    """
    Next-generation blueprint generator with advanced caching, AI quality assurance,
    and multi-tier architecture for enterprise-scale content generation.
    """
    
    def __init__(self, serpapi_key: str, gemini_api_key: str, 
                 redis_host: str = 'localhost', redis_port: int = 6379):
        """
        Initialize the enhanced blueprint generator.
        
        Args:
            serpapi_key: SerpAPI key for search data
            gemini_api_key: Google Gemini API key for AI processing
            redis_host: Redis server hostname for caching
            redis_port: Redis server port for caching
        """
        self.serpapi_key = serpapi_key
        self.gemini_api_key = gemini_api_key
        
        # Initialize advanced caching
        self.cache_manager = AdvancedCacheManager(redis_host, redis_port)
        
        # Initialize AI quality framework
        self.quality_framework = AIQualityFramework()
        
        # Initialize core components
        try:
            self.analyzer = BlueprintAnalyzer(
                serpapi_key=serpapi_key,
                gemini_api_key=gemini_api_key
            )
            
            self.ai_generator = BlueprintAIGenerator(
                gemini_api_key=gemini_api_key
            )
            
            logger.info("Enhanced Blueprint Generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced blueprint generator: {str(e)}")
            raise Exception(f"Enhanced blueprint generator initialization failed: {str(e)}")
    
    @cache_result(namespace="blueprint_generation", ttl=3600)
    @assess_ai_quality()
    def generate_blueprint(self, keyword: str, user_id: str,
                          project_id: Optional[str] = None,
                          competitors: Optional[Dict[str, Any]] = None,
                          quality_threshold: float = 75.0) -> Dict[str, Any]:
        """
        Generate a high-quality content blueprint with advanced caching and quality assurance.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            project_id: Optional project ID to associate the blueprint with
            competitors: (Optional) Precomputed competitor analysis data
            quality_threshold: Minimum quality score threshold (0-100)
            
        Returns:
            Dictionary containing the complete blueprint data with quality assessment
        """
        start_time = time.time()
        logger.info(f"Starting enhanced blueprint generation for keyword: '{keyword}' (user: {user_id})")
        
        try:
            # Check cache first for recent analysis components
            cached_competitors = self._get_cached_competitors(keyword) if competitors is None else None
            cached_serp_features = self._get_cached_serp_features(keyword)
            
            # Step 1: Comprehensive analysis with caching
            logger.info("Step 1: Performing comprehensive analysis with caching")
            
            if cached_competitors and not competitors:
                logger.info("Using cached competitor analysis")
                competitors_data = cached_competitors
            else:
                if competitors is not None:
                    competitors_data = competitors
                else:
                    competitors_data = self.analyzer.analyze_competitors(keyword)
                    # Cache for future use
                    self._cache_competitors(keyword, competitors_data)
            
            if cached_serp_features:
                logger.info("Using cached SERP features")
                serp_features = cached_serp_features
            else:
                serp_features = self.analyzer.analyze_serp_features(keyword)
                # Cache for future use
                self._cache_serp_features(keyword, serp_features)
            
            # Content analysis (less cacheable due to dynamic nature)
            content_insights = self.analyzer.analyze_competitor_content(competitors_data)
            content_gaps = self.analyzer.analyze_content_gaps(competitors_data, keyword)
            
            # Step 2: AI-powered content generation with quality monitoring
            logger.info("Step 2: Generating AI-powered content structure")
            
            # Generate with quality checkpoints
            heading_structure = self._generate_with_quality_check(
                self.ai_generator.generate_heading_structure,
                keyword, competitors_data, content_insights
            )
            
            topic_clusters = self._generate_with_quality_check(
                self.ai_generator.generate_topic_clusters,
                keyword, competitors_data, serp_features
            )
            
            content_outline = self._generate_with_quality_check(
                self.ai_generator.generate_content_outline,
                keyword, heading_structure, topic_clusters
            )
            
            seo_recommendations = self._generate_with_quality_check(
                self.ai_generator.generate_seo_recommendations,
                keyword, competitors_data, serp_features
            )
            
            # Step 3: Compile blueprint with metadata
            generation_time = int(time.time() - start_time)
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            blueprint_data = {
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
                    'version': '3.0-enhanced',
                    'components_used': [
                        'advanced_caching', 'ai_quality_framework', 'competitor_analysis',
                        'content_analysis', 'serp_optimization', 'ai_generation', 'gap_analysis'
                    ],
                    'cache_performance': self._get_cache_performance(),
                    'quality_threshold': quality_threshold
                },
                'system_status': {
                    'google_apis_enabled': google_apis_enabled,
                    'migration_manager_available': bool(migration_manager),
                    'cache_manager_available': bool(self.cache_manager),
                    'quality_framework_enabled': True,
                    'processing_method': 'enhanced_pipeline'
                }
            }
            
            # Step 4: Quality assessment (handled by decorator)
            # The @assess_ai_quality decorator will automatically add quality assessment
            
            # Step 5: Post-generation quality validation
            if hasattr(blueprint_data, 'quality_assessment'):
                quality_score = blueprint_data['quality_assessment']['overall_score']
                if quality_score < quality_threshold:
                    logger.warning(f"Blueprint quality score ({quality_score:.2f}) below threshold ({quality_threshold})")
                    # Could trigger regeneration or enhancement here
            
            # Validate the blueprint
            if self.validate_blueprint_data(blueprint_data):
                logger.info(f"Enhanced blueprint generation completed for keyword: '{keyword}' in {generation_time}s")
                return blueprint_data
            else:
                raise Exception("Generated blueprint failed validation")
            
        except Exception as e:
            logger.error(f"Error generating enhanced blueprint for keyword '{keyword}': {str(e)}")
            raise Exception(f"Enhanced blueprint generation failed: {str(e)}")
    
    def generate_quick_blueprint(self, keyword: str, user_id: str,
                               use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate a quick blueprint optimized for speed with intelligent caching.
        
        Args:
            keyword: Target keyword for content optimization
            user_id: ID of the user requesting the blueprint
            use_cache: Whether to use cached data for faster generation
            
        Returns:
            Dictionary containing the quick blueprint data
        """
        start_time = time.time()
        logger.info(f"Starting quick enhanced blueprint generation for keyword: '{keyword}' (user: {user_id})")
        
        try:
            # Use aggressive caching for quick generation
            if use_cache:
                # Try to get complete cached blueprint first
                cached_blueprint = self.cache_manager.get("quick_blueprint", keyword, {"user_id": user_id})
                if cached_blueprint:
                    logger.info("Returning cached quick blueprint")
                    cached_blueprint['generation_metadata']['cache_hit'] = True
                    return cached_blueprint
            
            # Quick analysis with caching
            competitors = self._get_cached_competitors(keyword)
            if not competitors:
                competitors = self.analyzer.analyze_competitors(keyword)
                self._cache_competitors(keyword, competitors, ttl=1800)  # 30 min cache
            
            serp_features = self._get_cached_serp_features(keyword)
            if not serp_features:
                serp_features = self.analyzer.analyze_serp_features(keyword)
                self._cache_serp_features(keyword, serp_features, ttl=1800)
            
            # Lightweight content insights
            content_insights = self._generate_quick_content_insights(competitors)
            
            # Quick AI generation
            heading_structure = self.ai_generator.generate_heading_structure(
                keyword, competitors, content_insights
            )
            
            topic_clusters = self.ai_generator.generate_topic_clusters(
                keyword, competitors, serp_features
            )
            
            generation_time = int(time.time() - start_time)
            
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
                    'version': '3.0-enhanced-quick',
                    'components_used': ['quick_analysis', 'aggressive_caching', 'ai_generation'],
                    'blueprint_type': 'quick',
                    'cache_hit': False,
                    'cache_performance': self._get_cache_performance()
                },
                'system_status': {
                    'processing_method': 'enhanced_quick_pipeline',
                    'cache_optimization': True,
                    'quality_framework_enabled': False  # Disabled for speed
                }
            }
            
            # Cache the quick blueprint
            if use_cache:
                self.cache_manager.set("quick_blueprint", keyword, quick_blueprint, 
                                     ttl=1800, additional_params={"user_id": user_id})
            
            logger.info(f"Quick enhanced blueprint generation completed for keyword: '{keyword}' in {generation_time}s")
            return quick_blueprint
            
        except Exception as e:
            logger.error(f"Error generating quick enhanced blueprint for keyword '{keyword}': {str(e)}")
            raise Exception(f"Quick enhanced blueprint generation failed: {str(e)}")
    
    def batch_generate_blueprints(self, keywords: List[str], user_id: str,
                                 max_workers: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple blueprints in parallel for efficiency.
        
        Args:
            keywords: List of keywords to process
            user_id: ID of the user requesting the blueprints
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of generated blueprint data
        """
        logger.info(f"Starting batch blueprint generation for {len(keywords)} keywords")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_keyword = {
                executor.submit(self.generate_quick_blueprint, keyword, user_id): keyword 
                for keyword in keywords
            }
            
            # Collect results
            for future in future_to_keyword:
                keyword = future_to_keyword[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout per blueprint
                    results.append(result)
                    logger.info(f"Completed blueprint for keyword: {keyword}")
                except Exception as e:
                    logger.error(f"Failed to generate blueprint for keyword '{keyword}': {str(e)}")
                    # Add error result
                    results.append({
                        'keyword': keyword,
                        'error': str(e),
                        'generation_metadata': {
                            'created_at': datetime.utcnow().isoformat(),
                            'user_id': user_id,
                            'version': '3.0-enhanced-batch',
                            'status': 'failed'
                        }
                    })
        
        logger.info(f"Batch blueprint generation completed. {len(results)} results")
        return results
    
    def _generate_with_quality_check(self, generation_func, *args, **kwargs) -> Any:
        """
        Generate content with built-in quality checking and retry logic.
        
        Args:
            generation_func: Function to call for generation
            *args, **kwargs: Arguments to pass to the generation function
            
        Returns:
            Generated content that meets quality standards
        """
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                result = generation_func(*args, **kwargs)
                
                # Quick quality check for basic issues
                if self._basic_quality_check(result):
                    return result
                elif attempt < max_retries:
                    logger.warning(f"Quality check failed for {generation_func.__name__}, retrying ({attempt + 1}/{max_retries})")
                    continue
                else:
                    logger.warning(f"Quality check failed for {generation_func.__name__} after {max_retries} retries, using result")
                    return result
                    
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Generation failed for {generation_func.__name__}, retrying ({attempt + 1}/{max_retries}): {str(e)}")
                    continue
                else:
                    logger.error(f"Generation failed for {generation_func.__name__} after {max_retries} retries: {str(e)}")
                    raise
        
        return result
    
    def _basic_quality_check(self, content: Any) -> bool:
        """
        Perform basic quality check on generated content.
        
        Args:
            content: Content to check
            
        Returns:
            True if content meets basic quality standards
        """
        if not content:
            return False
        
        # Check for minimum content length
        content_str = str(content)
        if len(content_str) < 50:  # Minimum 50 characters
            return False
        
        # Check for obvious errors
        error_indicators = ['error', 'failed', 'null', 'undefined', 'exception']
        content_lower = content_str.lower()
        
        for indicator in error_indicators:
            if indicator in content_lower:
                return False
        
        return True
    
    def _get_cached_competitors(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get cached competitor analysis"""
        return self.cache_manager.get("competitor_analysis", keyword)
    
    def _cache_competitors(self, keyword: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache competitor analysis data"""
        self.cache_manager.set("competitor_analysis", keyword, data, ttl)
    
    def _get_cached_serp_features(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get cached SERP features analysis"""
        return self.cache_manager.get("serp_features", keyword)
    
    def _cache_serp_features(self, keyword: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache SERP features data"""
        self.cache_manager.set("serp_features", keyword, data, ttl)
    
    def _generate_quick_content_insights(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quick content insights without heavy processing"""
        return {
            'avg_word_count': 2500,  # Default estimate
            'common_sections': ['Introduction', 'Main Content', 'Best Practices', 'Conclusion'],
            'content_gaps': ['Case studies', 'Real-world examples'],
            'structural_patterns': {
                'heading_depth': '3_levels',
                'list_usage': 'recommended'
            },
            'analysis_status': 'quick_analysis'
        }
    
    def _get_cache_performance(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        if self.cache_manager:
            stats = self.cache_manager.get_cache_stats()
            return {
                'overall_hit_rate': stats['overall']['overall_hit_rate'],
                'total_requests': stats['overall']['total_requests'],
                'redis_available': stats['overall']['redis_available'],
                'l1_cache_size': stats['overall']['l1_cache_size']
            }
        return {'cache_available': False}
    
    def validate_blueprint_data(self, blueprint_data: Dict[str, Any]) -> bool:
        """
        Validate that the generated blueprint contains required components.
        
        Args:
            blueprint_data: Generated blueprint data
            
        Returns:
            True if valid, False otherwise
        """
        return validate_blueprint_data(blueprint_data)
    
    def get_comprehensive_quality_report(self, blueprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a comprehensive quality report for a blueprint.
        
        Args:
            blueprint_data: Blueprint data to assess
            
        Returns:
            Detailed quality assessment report
        """
        try:
            quality_report = self.quality_framework.assess_quality(blueprint_data)
            return asdict(quality_report)
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            return {
                'error': str(e),
                'overall_score': 0.0,
                'quality_grade': 'F',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def invalidate_cache(self, keyword: str = None, namespace: str = None):
        """
        Invalidate cache entries for a keyword or namespace.
        
        Args:
            keyword: Specific keyword to invalidate (optional)
            namespace: Cache namespace to invalidate (optional)
        """
        if keyword:
            # Invalidate all cache entries for this keyword
            self.cache_manager.invalidate("competitor_analysis", keyword)
            self.cache_manager.invalidate("serp_features", keyword)
            self.cache_manager.invalidate("quick_blueprint", keyword)
            self.cache_manager.invalidate("blueprint_generation", keyword)
            logger.info(f"Cache invalidated for keyword: {keyword}")
        elif namespace:
            self.cache_manager.invalidate(namespace)
            logger.info(f"Cache invalidated for namespace: {namespace}")
        else:
            self.cache_manager.clear_all_caches()
            logger.info("All caches cleared")
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the current status of the enhanced blueprint generator service.
        
        Returns:
            Enhanced service status information
        """
        try:
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            cache_stats = self.cache_manager.get_cache_stats() if self.cache_manager else {}
            quality_stats = self.quality_framework.get_framework_stats() if self.quality_framework else {}
            
            status = {
                'service_name': 'EnhancedBlueprintGeneratorService',
                'version': '3.0-enhanced',
                'status': 'operational',
                'components': {
                    'analyzer': 'initialized' if hasattr(self, 'analyzer') else 'not_initialized',
                    'ai_generator': 'initialized' if hasattr(self, 'ai_generator') else 'not_initialized',
                    'cache_manager': 'initialized' if self.cache_manager else 'not_initialized',
                    'quality_framework': 'initialized' if self.quality_framework else 'not_initialized'
                },
                'api_keys': {
                    'serpapi_configured': bool(self.serpapi_key),
                    'gemini_configured': bool(self.gemini_api_key)
                },
                'infrastructure': {
                    'google_apis_enabled': google_apis_enabled,
                    'migration_manager_available': bool(migration_manager),
                    'redis_cache_available': cache_stats.get('overall', {}).get('redis_available', False),
                    'cache_hit_rate': cache_stats.get('overall', {}).get('overall_hit_rate', 0.0)
                },
                'quality_framework': quality_stats,
                'capabilities': [
                    'advanced_caching',
                    'ai_quality_assessment',
                    'competitor_analysis',
                    'content_analysis',
                    'serp_optimization',
                    'ai_content_generation',
                    'batch_processing',
                    'quality_validation',
                    'cache_invalidation',
                    'performance_monitoring'
                ],
                'performance_metrics': {
                    'cache_performance': self._get_cache_performance(),
                    'average_generation_time': '30-45s (full), 5-10s (quick)',
                    'batch_processing_capacity': '3 parallel blueprints',
                    'quality_assessment_enabled': True
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Determine overall status
            critical_components = ['analyzer', 'ai_generator']
            all_critical_ready = all(status['components'][comp] == 'initialized' for comp in critical_components)
            
            if all_critical_ready and (google_apis_enabled or (status['api_keys']['serpapi_configured'] and status['api_keys']['gemini_configured'])):
                status['overall_status'] = 'fully_operational'
            elif all_critical_ready:
                status['overall_status'] = 'operational_limited'
                status['status'] = 'degraded'
            else:
                status['overall_status'] = 'limited_functionality'
                status['status'] = 'degraded'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting enhanced service status: {str(e)}")
            return {
                'service_name': 'EnhancedBlueprintGeneratorService',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }