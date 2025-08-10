"""
AI Enhanced Blueprint Generator - Integration layer for AI services

Extends the existing blueprint generation system with comprehensive AI capabilities:
- Integrates with existing BlueprintGeneratorService
- Adds AI-powered content analysis and optimization
- Maintains backward compatibility with current system
- Provides optional AI enhancement layer

This service acts as a bridge between the existing blueprint system and new AI capabilities.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import existing services
from .blueprint_generator import BlueprintGeneratorService
from .blueprint_utils import validate_blueprint_data

# Import AI services
from .ai.ai_manager import ai_manager
from .ai.ai_blueprint_enhancer import AIBlueprintEnhancer

class AIEnhancedBlueprintGenerator:
    """
    Enhanced blueprint generator that integrates AI services with existing blueprint generation.
    
    Features:
    - Maintains compatibility with existing BlueprintGeneratorService
    - Optional AI enhancement layer
    - Async processing for performance
    - Intelligent fallback to traditional generation
    - Resource-efficient AI integration
    """
    
    def __init__(self, serpapi_key: str, gemini_api_key: str, enable_ai: bool = True):
        """
        Initialize the AI-enhanced blueprint generator.
        
        Args:
            serpapi_key: SerpAPI key for search data
            gemini_api_key: Google Gemini API key
            enable_ai: Whether to enable AI enhancements
        """
        self.logger = logging.getLogger(__name__)
        self.enable_ai = enable_ai
        
        # Initialize traditional blueprint generator
        self.traditional_generator = BlueprintGeneratorService(
            serpapi_key=serpapi_key,
            gemini_api_key=gemini_api_key
        )
        
        # Initialize AI components
        self.ai_enhancer = None
        self.ai_initialized = False
        
        if self.enable_ai:
            self.ai_enhancer = AIBlueprintEnhancer()
            
        self.performance_metrics = {
            'total_generations': 0,
            'ai_enhanced_generations': 0,
            'traditional_generations': 0,
            'ai_initialization_time': 0,
            'average_enhancement_time': 0,
            'enhancement_success_rate': 0
        }
    
    async def generate_blueprint(self, keyword: str, user_id: str, 
                               enable_ai_enhancement: Optional[bool] = None) -> Dict[str, Any]:
        """
        Generate a content blueprint with optional AI enhancement.
        
        Args:
            keyword: Target keyword for blueprint generation
            user_id: User identifier for personalization
            enable_ai_enhancement: Override AI enhancement setting
            
        Returns:
            Enhanced blueprint with AI insights and recommendations
        """
        start_time = time.time()
        
        try:
            # Determine AI enhancement setting
            use_ai = (enable_ai_enhancement if enable_ai_enhancement is not None 
                     else self.enable_ai)
            
            self.logger.info(f"Generating blueprint for keyword: '{keyword}' (AI: {use_ai})")
            
            # Generate traditional blueprint first
            traditional_blueprint = await self._generate_traditional_blueprint(keyword, user_id)
            
            if not traditional_blueprint:
                self.logger.error("Traditional blueprint generation failed")
                return self._create_error_response("Blueprint generation failed")
            
            # Apply AI enhancement if enabled
            if use_ai:
                enhanced_blueprint = await self._apply_ai_enhancement(
                    traditional_blueprint, keyword, user_id
                )
                
                if enhanced_blueprint:
                    self.performance_metrics['ai_enhanced_generations'] += 1
                    generation_time = time.time() - start_time
                    
                    self.logger.info(f"AI-enhanced blueprint generated in {generation_time:.2f}s")
                    return enhanced_blueprint
                else:
                    self.logger.warning("AI enhancement failed, returning traditional blueprint")
            
            # Return traditional blueprint
            self.performance_metrics['traditional_generations'] += 1
            self.performance_metrics['total_generations'] += 1
            
            generation_time = time.time() - start_time
            self.logger.info(f"Traditional blueprint generated in {generation_time:.2f}s")
            
            return traditional_blueprint
            
        except Exception as e:
            self.logger.error(f"Blueprint generation failed: {e}")
            return self._create_error_response(f"Generation error: {str(e)}")
    
    async def _generate_traditional_blueprint(self, keyword: str, user_id: str) -> Dict[str, Any]:
        """Generate blueprint using traditional method."""
        try:
            # Use existing blueprint generator
            # Note: Converting sync call to async context
            loop = asyncio.get_event_loop()
            blueprint = await loop.run_in_executor(
                None, 
                self.traditional_generator.generate_blueprint,
                keyword
            )
            
            if blueprint:
                # Add metadata
                blueprint['generation_method'] = 'traditional'
                blueprint['user_id'] = user_id
                blueprint['generation_timestamp'] = datetime.utcnow().isoformat()
                
                # Validate blueprint structure
                if validate_blueprint_data(blueprint):
                    return blueprint
                else:
                    self.logger.warning("Generated blueprint failed validation")
                    return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Traditional blueprint generation failed: {e}")
            return None
    
    async def _apply_ai_enhancement(self, blueprint: Dict[str, Any], 
                                  keyword: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Apply AI enhancement to traditional blueprint."""
        try:
            if not self.ai_enhancer:
                return None
            
            # Initialize AI services if needed
            if not self.ai_initialized:
                ai_init_start = time.time()
                success = await ai_manager.initialize_services()
                
                if success:
                    self.ai_initialized = True
                    init_time = time.time() - ai_init_start
                    self.performance_metrics['ai_initialization_time'] = init_time
                    self.logger.info(f"AI services initialized in {init_time:.2f}s")
                else:
                    self.logger.error("AI services initialization failed")
                    return None
            
            # Gather competitor content for analysis
            competitor_content = await self._gather_competitor_content(keyword)
            
            # Apply AI enhancement
            enhancement_start = time.time()
            enhanced_blueprint = await self.ai_enhancer.enhance_blueprint(
                blueprint, competitor_content
            )
            
            enhancement_time = time.time() - enhancement_start
            
            # Update performance metrics
            current_avg = self.performance_metrics['average_enhancement_time']
            current_count = self.performance_metrics['ai_enhanced_generations']
            new_avg = (current_avg * current_count + enhancement_time) / (current_count + 1)
            self.performance_metrics['average_enhancement_time'] = new_avg
            
            # Mark as AI-enhanced
            enhanced_blueprint['generation_method'] = 'ai_enhanced'
            enhanced_blueprint['ai_enhancement_time'] = enhancement_time
            
            self.logger.debug(f"AI enhancement completed in {enhancement_time:.2f}s")
            return enhanced_blueprint
            
        except Exception as e:
            self.logger.error(f"AI enhancement failed: {e}")
            return None
    
    async def _gather_competitor_content(self, keyword: str) -> List[str]:
        """Gather competitor content for AI analysis."""
        try:
            # Extract competitor content from analyzer if available
            if hasattr(self.traditional_generator, 'analyzer'):
                analyzer = self.traditional_generator.analyzer
                
                # Try to get search results for the keyword
                if hasattr(analyzer, 'get_serp_data'):
                    loop = asyncio.get_event_loop()
                    serp_data = await loop.run_in_executor(
                        None,
                        analyzer.get_serp_data,
                        keyword
                    )
                    
                    if serp_data and 'organic_results' in serp_data:
                        competitor_content = []
                        for result in serp_data['organic_results'][:5]:  # Top 5 competitors
                            if 'snippet' in result:
                                competitor_content.append(result['snippet'])
                            if 'title' in result:
                                competitor_content.append(result['title'])
                        
                        return competitor_content
            
            return []
            
        except Exception as e:
            self.logger.error(f"Competitor content gathering failed: {e}")
            return []
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat(),
            'generation_method': 'error',
            'ai_enhancement': None
        }
    
    async def generate_quick_blueprint(self, keyword: str, user_id: str) -> Dict[str, Any]:
        """
        Generate a quick blueprint optimized for speed.
        
        Args:
            keyword: Target keyword
            user_id: User identifier
            
        Returns:
            Quick blueprint with minimal AI processing
        """
        try:
            self.logger.info(f"Generating quick blueprint for: '{keyword}'")
            
            # Generate traditional blueprint
            blueprint = await self._generate_traditional_blueprint(keyword, user_id)
            
            if not blueprint:
                return self._create_error_response("Quick blueprint generation failed")
            
            # Add quick AI insights if available and initialized
            if self.ai_initialized and self.ai_enhancer:
                try:
                    # Quick content analysis only
                    content_pieces = self.ai_enhancer._extract_content_from_blueprint(blueprint)
                    
                    if content_pieces:
                        # Basic NLP analysis only (fastest service)
                        if ai_manager.nlp_service:
                            nlp_results = await ai_manager.nlp_service.process_batch(content_pieces[:3])
                            
                            if nlp_results:
                                blueprint['quick_ai_insights'] = {
                                    'readability_scores': [
                                        r.get('readability', {}).get('readability_score', 0)
                                        for r in nlp_results if r
                                    ],
                                    'entity_counts': [
                                        len(r.get('entities', []))
                                        for r in nlp_results if r
                                    ],
                                    'processing_time': time.time() - time.time()
                                }
                
                except Exception as e:
                    self.logger.warning(f"Quick AI insights failed: {e}")
            
            blueprint['generation_method'] = 'quick'
            self.performance_metrics['total_generations'] += 1
            
            return blueprint
            
        except Exception as e:
            self.logger.error(f"Quick blueprint generation failed: {e}")
            return self._create_error_response(f"Quick generation error: {str(e)}")
    
    async def analyze_blueprint_performance(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the performance potential of a generated blueprint.
        
        Args:
            blueprint: Blueprint to analyze
            
        Returns:
            Performance analysis results
        """
        try:
            if not self.ai_initialized or not self.ai_enhancer:
                return {'error': 'AI services not available'}
            
            # Extract content for analysis
            content_pieces = self.ai_enhancer._extract_content_from_blueprint(blueprint)
            
            if not content_pieces:
                return {'error': 'No analyzable content found'}
            
            # Perform ML analysis for performance prediction
            if ai_manager.ml_service:
                ml_results = await ai_manager.ml_service.classify_batch(content_pieces)
                
                performance_scores = []
                quality_scores = []
                
                for result in ml_results:
                    if result:
                        perf = result.get('performance_prediction', {})
                        if perf:
                            performance_scores.append(perf.get('overall_performance_score', 0))
                        
                        qual = result.get('quality_score', {})
                        if qual:
                            quality_scores.append(qual.get('overall_score', 0))
                
                return {
                    'performance_analysis': {
                        'average_performance_score': sum(performance_scores) / len(performance_scores) if performance_scores else 0,
                        'average_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                        'performance_distribution': performance_scores,
                        'quality_distribution': quality_scores,
                        'content_pieces_analyzed': len(content_pieces)
                    },
                    'recommendations': await self._generate_performance_recommendations(ml_results)
                }
            
            return {'error': 'ML service not available'}
            
        except Exception as e:
            self.logger.error(f"Blueprint performance analysis failed: {e}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    async def _generate_performance_recommendations(self, ml_results: List[Dict[str, Any]]) -> List[str]:
        """Generate performance improvement recommendations."""
        try:
            recommendations = []
            
            for result in ml_results:
                if result and 'performance_prediction' in result:
                    perf_recs = result['performance_prediction'].get('recommendations', [])
                    recommendations.extend(perf_recs)
            
            # Remove duplicates and limit
            unique_recommendations = list(set(recommendations))
            return unique_recommendations[:5]
            
        except Exception:
            return []
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get current AI services status and performance metrics."""
        try:
            status = {
                'ai_enabled': self.enable_ai,
                'ai_initialized': self.ai_initialized,
                'performance_metrics': self.performance_metrics.copy()
            }
            
            if self.ai_initialized:
                # Get AI manager metrics
                ai_metrics = ai_manager.get_performance_metrics()
                status['ai_services_metrics'] = ai_metrics
                
                # Calculate success rate
                total_ai_attempts = self.performance_metrics['ai_enhanced_generations']
                if total_ai_attempts > 0:
                    success_rate = (total_ai_attempts / 
                                  max(self.performance_metrics['total_generations'], 1)) * 100
                    status['ai_success_rate'] = success_rate
            
            return status
            
        except Exception as e:
            self.logger.error(f"AI status retrieval failed: {e}")
            return {'error': f'Status error: {str(e)}'}
    
    async def warm_up_ai_services(self) -> bool:
        """Warm up AI services for better performance."""
        try:
            if not self.enable_ai or self.ai_initialized:
                return True
            
            self.logger.info("Warming up AI services...")
            start_time = time.time()
            
            success = await ai_manager.initialize_services()
            
            if success:
                self.ai_initialized = True
                warm_up_time = time.time() - start_time
                self.performance_metrics['ai_initialization_time'] = warm_up_time
                self.logger.info(f"AI services warmed up in {warm_up_time:.2f}s")
                return True
            else:
                self.logger.error("AI services warm-up failed")
                return False
                
        except Exception as e:
            self.logger.error(f"AI services warm-up error: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown AI services."""
        try:
            if self.ai_initialized:
                ai_manager.shutdown()
                self.ai_initialized = False
                self.logger.info("AI services shut down successfully")
                
        except Exception as e:
            self.logger.error(f"AI services shutdown error: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            # Note: This is a sync context, so we can't await
            if self.ai_initialized:
                ai_manager.shutdown()
        except Exception:
            pass