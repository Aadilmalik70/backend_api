"""
AI Blueprint Enhancer - Enhanced blueprint generation using AI services

Integrates all AI services to provide comprehensive content blueprint enhancement:
- NLP-powered content analysis and optimization
- Semantic understanding for content gaps identification
- ML-based content classification and performance prediction
- Graph-based content relationship mapping

Transforms traditional blueprint generation into AI-powered content strategy.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import time
import json
from .ai_manager import ai_manager

class AIBlueprintEnhancer:
    """
    AI-powered blueprint enhancement service that integrates all AI capabilities.
    
    Features:
    - Multi-service AI analysis integration
    - Content quality optimization recommendations
    - Semantic content gap identification  
    - Performance prediction and optimization
    - Content relationship mapping
    - Strategic content recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_manager = ai_manager
        
        # Enhancement configuration
        self.config = {
            'min_quality_score': 70.0,
            'target_content_length': 800,
            'similarity_threshold': 0.7,
            'max_recommendations': 10,
            'enhancement_modes': [
                'content_optimization',
                'semantic_enhancement', 
                'performance_prediction',
                'relationship_mapping'
            ]
        }
    
    async def enhance_blueprint(self, blueprint_data: Dict[str, Any], 
                              competitor_content: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enhance a content blueprint using AI analysis.
        
        Args:
            blueprint_data: Original blueprint data
            competitor_content: Optional competitor content for analysis
            
        Returns:
            Enhanced blueprint with AI-powered insights and recommendations
        """
        try:
            start_time = time.time()
            
            # Ensure AI services are initialized
            if not self.ai_manager._initialized:
                await self.ai_manager.initialize_services()
            
            # Extract content for analysis
            content_pieces = self._extract_content_from_blueprint(blueprint_data)
            
            if competitor_content:
                content_pieces.extend(competitor_content)
            
            if not content_pieces:
                self.logger.warning("No content available for AI enhancement")
                return blueprint_data
            
            # Perform parallel AI analysis
            ai_analysis = await self.ai_manager.process_content_parallel(content_pieces)
            
            # Generate enhancement recommendations
            enhancements = await self._generate_enhancements(blueprint_data, ai_analysis, content_pieces)
            
            # Create enhanced blueprint
            enhanced_blueprint = await self._create_enhanced_blueprint(
                blueprint_data, enhancements, ai_analysis
            )
            
            processing_time = time.time() - start_time
            enhanced_blueprint['ai_enhancement'] = {
                'processing_time': processing_time,
                'services_used': list(ai_analysis.keys()),
                'enhancement_version': '1.0.0',
                'timestamp': time.time()
            }
            
            self.logger.info(f"Blueprint enhancement completed in {processing_time:.2f}s")
            return enhanced_blueprint
            
        except Exception as e:
            self.logger.error(f"Blueprint enhancement failed: {e}")
            # Return original blueprint if enhancement fails
            return blueprint_data
    
    def _extract_content_from_blueprint(self, blueprint_data: Dict[str, Any]) -> List[str]:
        """Extract text content from blueprint data for AI analysis."""
        try:
            content_pieces = []
            
            # Extract from common blueprint fields
            fields_to_extract = [
                'content_outline',
                'main_content',
                'introduction',
                'conclusion',
                'headings',
                'meta_description',
                'seo_title'
            ]
            
            for field in fields_to_extract:
                if field in blueprint_data:
                    value = blueprint_data[field]
                    if isinstance(value, str) and value.strip():
                        content_pieces.append(value.strip())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and item.strip():
                                content_pieces.append(item.strip())
                            elif isinstance(item, dict) and 'text' in item:
                                content_pieces.append(str(item['text']).strip())
            
            # Extract from nested structures
            if 'content_structure' in blueprint_data:
                structure = blueprint_data['content_structure']
                if isinstance(structure, dict):
                    self._extract_from_nested_structure(structure, content_pieces)
            
            # Remove duplicates and very short content
            unique_content = []
            seen = set()
            
            for content in content_pieces:
                content_hash = hash(content.lower())
                if content_hash not in seen and len(content) > 20:
                    unique_content.append(content)
                    seen.add(content_hash)
            
            return unique_content
            
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            return []
    
    def _extract_from_nested_structure(self, structure: Dict[str, Any], content_pieces: List[str]):
        """Recursively extract content from nested blueprint structure."""
        try:
            for key, value in structure.items():
                if isinstance(value, str) and len(value) > 20:
                    content_pieces.append(value)
                elif isinstance(value, dict):
                    self._extract_from_nested_structure(value, content_pieces)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and len(item) > 20:
                            content_pieces.append(item)
                        elif isinstance(item, dict):
                            self._extract_from_nested_structure(item, content_pieces)
        except Exception:
            pass
    
    async def _generate_enhancements(self, blueprint_data: Dict[str, Any], 
                                   ai_analysis: Dict[str, Any], 
                                   content_pieces: List[str]) -> Dict[str, Any]:
        """Generate enhancement recommendations based on AI analysis."""
        try:
            enhancements = {
                'content_optimization': [],
                'semantic_insights': {},
                'performance_predictions': {},
                'structural_recommendations': [],
                'quality_improvements': []
            }
            
            # NLP-based enhancements
            if 'nlp' in ai_analysis and ai_analysis['nlp']:
                nlp_enhancements = await self._generate_nlp_enhancements(ai_analysis['nlp'])
                enhancements['content_optimization'].extend(nlp_enhancements)
            
            # Semantic enhancements
            if 'semantic' in ai_analysis and ai_analysis['semantic']:
                semantic_enhancements = await self._generate_semantic_enhancements(ai_analysis['semantic'])
                enhancements['semantic_insights'] = semantic_enhancements
            
            # ML-based enhancements
            if 'ml' in ai_analysis and ai_analysis['ml']:
                ml_enhancements = await self._generate_ml_enhancements(ai_analysis['ml'])
                enhancements['performance_predictions'] = ml_enhancements
            
            # Graph-based enhancements
            if 'graph' in ai_analysis and ai_analysis['graph']:
                graph_enhancements = await self._generate_graph_enhancements(ai_analysis['graph'])
                enhancements['structural_recommendations'].extend(graph_enhancements)
            
            # Cross-service enhancements
            cross_service_enhancements = await self._generate_cross_service_enhancements(ai_analysis)
            enhancements['quality_improvements'].extend(cross_service_enhancements)
            
            return enhancements
            
        except Exception as e:
            self.logger.error(f"Enhancement generation failed: {e}")
            return {}
    
    async def _generate_nlp_enhancements(self, nlp_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate enhancements based on NLP analysis."""
        try:
            enhancements = []
            
            for i, result in enumerate(nlp_results):
                if not result:
                    continue
                
                # Readability enhancements
                readability = result.get('readability', {})
                if readability.get('readability_score', 0) < 60:
                    enhancements.append({
                        'type': 'readability_improvement',
                        'priority': 'high',
                        'description': 'Improve content readability by simplifying sentence structure',
                        'current_score': readability.get('readability_score', 0),
                        'target_score': 70,
                        'content_index': i
                    })
                
                # Entity enrichment
                entities = result.get('entities', [])
                if len(entities) < 3:
                    enhancements.append({
                        'type': 'entity_enrichment',
                        'priority': 'medium',
                        'description': 'Add more specific entities (people, places, organizations)',
                        'current_entities': len(entities),
                        'target_entities': 5,
                        'content_index': i
                    })
                
                # SEO elements enhancement
                seo_elements = result.get('seo_elements', {})
                if not seo_elements.get('questions'):
                    enhancements.append({
                        'type': 'engagement_improvement',
                        'priority': 'medium',
                        'description': 'Add questions to improve user engagement',
                        'content_index': i
                    })
            
            return enhancements
            
        except Exception as e:
            self.logger.error(f"NLP enhancement generation failed: {e}")
            return []
    
    async def _generate_semantic_enhancements(self, semantic_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhancements based on semantic analysis."""
        try:
            enhancements = {}
            
            # Content diversity analysis
            diversity = semantic_results.get('diversity', {})
            if diversity:
                enhancements['content_diversity'] = {
                    'current_level': diversity.get('diversity_level', 'Unknown'),
                    'diversity_score': diversity.get('diversity_score', 0),
                    'recommendation': 'Increase content diversity' if diversity.get('diversity_score', 0) < 0.5 else 'Good diversity maintained'
                }
            
            # Similarity insights
            similarity_stats = semantic_results.get('similarity_stats', {})
            if similarity_stats:
                enhancements['content_similarity'] = {
                    'mean_similarity': similarity_stats.get('mean_similarity', 0),
                    'high_similarity_pairs': similarity_stats.get('high_similarity_pairs', 0),
                    'recommendation': self._get_similarity_recommendation(similarity_stats)
                }
            
            # Content gaps
            content_gaps = semantic_results.get('content_gaps', {})
            if content_gaps:
                enhancements['identified_gaps'] = content_gaps
            
            # Semantic keywords
            semantic_keywords = semantic_results.get('semantic_keywords', [])
            if semantic_keywords:
                enhancements['semantic_focus'] = {
                    'top_themes': semantic_keywords[:5],
                    'recommendation': 'Expand on identified semantic themes for better topical authority'
                }
            
            return enhancements
            
        except Exception as e:
            self.logger.error(f"Semantic enhancement generation failed: {e}")
            return {}
    
    async def _generate_ml_enhancements(self, ml_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate enhancements based on ML analysis."""
        try:
            enhancements = {}
            
            # Aggregate quality scores
            quality_scores = []
            performance_predictions = []
            
            for result in ml_results:
                if not result:
                    continue
                
                quality_score = result.get('quality_score', {})
                if quality_score:
                    quality_scores.append(quality_score.get('overall_score', 0))
                
                performance = result.get('performance_prediction', {})
                if performance:
                    performance_predictions.append(performance.get('overall_performance_score', 0))
            
            # Quality analysis
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                enhancements['content_quality'] = {
                    'average_score': avg_quality,
                    'quality_distribution': quality_scores,
                    'improvement_needed': avg_quality < self.config['min_quality_score'],
                    'recommendation': self._get_quality_recommendation(avg_quality)
                }
            
            # Performance predictions
            if performance_predictions:
                avg_performance = sum(performance_predictions) / len(performance_predictions)
                enhancements['performance_forecast'] = {
                    'predicted_performance': avg_performance,
                    'performance_tier': self._get_performance_tier(avg_performance),
                    'optimization_potential': 100 - avg_performance if avg_performance < 100 else 0
                }
            
            # Content classification insights
            classifications = []
            for result in ml_results:
                if result and 'classification' in result:
                    classifications.append(result['classification'])
            
            if classifications:
                enhancements['content_classification'] = {
                    'detected_types': [c.get('predicted_type', 'unknown') for c in classifications],
                    'confidence_scores': [c.get('confidence', 0) for c in classifications],
                    'recommendation': self._get_classification_recommendation(classifications)
                }
            
            return enhancements
            
        except Exception as e:
            self.logger.error(f"ML enhancement generation failed: {e}")
            return {}
    
    async def _generate_graph_enhancements(self, graph_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhancements based on graph analysis."""
        try:
            enhancements = []
            
            # Connectivity enhancements
            basic_metrics = graph_results.get('basic_metrics', {})
            if not basic_metrics.get('is_connected', True):
                enhancements.append({
                    'type': 'content_connectivity',
                    'priority': 'high',
                    'description': 'Create bridging content to connect isolated topics',
                    'components': basic_metrics.get('number_of_components', 1)
                })
            
            # Density improvements
            density = basic_metrics.get('density', 0)
            if density < 0.2:
                enhancements.append({
                    'type': 'content_density',
                    'priority': 'medium',
                    'description': 'Increase content interconnectedness',
                    'current_density': density,
                    'target_density': 0.3
                })
            
            # Community insights
            communities = graph_results.get('communities', {})
            if communities.get('num_communities', 0) > 1:
                enhancements.append({
                    'type': 'topic_clustering',
                    'priority': 'low',
                    'description': f"Content naturally clusters into {communities.get('num_communities', 0)} topics",
                    'clusters': communities.get('num_communities', 0)
                })
            
            # Influential content identification
            influential_content = graph_results.get('influential_content', [])
            if influential_content:
                enhancements.append({
                    'type': 'content_authority',
                    'priority': 'medium',
                    'description': 'Leverage high-authority content for internal linking',
                    'authority_pieces': len(influential_content)
                })
            
            return enhancements
            
        except Exception as e:
            self.logger.error(f"Graph enhancement generation failed: {e}")
            return []
    
    async def _generate_cross_service_enhancements(self, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhancements by combining insights from multiple AI services."""
        try:
            enhancements = []
            
            # Combine NLP and ML insights for content optimization
            if 'nlp' in ai_analysis and 'ml' in ai_analysis:
                nlp_results = ai_analysis['nlp']
                ml_results = ai_analysis['ml']
                
                # Check for consistency between readability and performance predictions
                for i, (nlp_result, ml_result) in enumerate(zip(nlp_results or [], ml_results or [])):
                    if nlp_result and ml_result:
                        readability_score = nlp_result.get('readability', {}).get('readability_score', 0)
                        performance_score = ml_result.get('performance_prediction', {}).get('overall_performance_score', 0)
                        
                        if abs(readability_score - performance_score) > 30:
                            enhancements.append({
                                'type': 'consistency_optimization',
                                'priority': 'medium',
                                'description': 'Align content readability with performance expectations',
                                'content_index': i,
                                'readability_gap': abs(readability_score - performance_score)
                            })
            
            # Combine semantic and graph analysis for strategic recommendations
            if 'semantic' in ai_analysis and 'graph' in ai_analysis:
                semantic_gaps = ai_analysis['semantic'].get('content_gaps', {})
                graph_gaps = ai_analysis['graph'].get('content_gaps', [])
                
                if semantic_gaps and graph_gaps:
                    enhancements.append({
                        'type': 'strategic_gap_filling',
                        'priority': 'high',
                        'description': 'Create content to fill identified semantic and structural gaps',
                        'semantic_gaps': len(semantic_gaps.get('content_gaps', [])),
                        'structural_gaps': len(graph_gaps)
                    })
            
            return enhancements
            
        except Exception as e:
            self.logger.error(f"Cross-service enhancement generation failed: {e}")
            return []
    
    async def _create_enhanced_blueprint(self, original_blueprint: Dict[str, Any], 
                                       enhancements: Dict[str, Any], 
                                       ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final enhanced blueprint with AI insights."""
        try:
            # Start with original blueprint
            enhanced = original_blueprint.copy()
            
            # Add AI analysis section
            enhanced['ai_analysis'] = {
                'content_optimization': enhancements.get('content_optimization', []),
                'semantic_insights': enhancements.get('semantic_insights', {}),
                'performance_predictions': enhancements.get('performance_predictions', {}),
                'structural_recommendations': enhancements.get('structural_recommendations', []),
                'quality_improvements': enhancements.get('quality_improvements', [])
            }
            
            # Add AI-powered recommendations
            enhanced['ai_recommendations'] = await self._generate_final_recommendations(enhancements)
            
            # Add performance metrics
            enhanced['ai_metrics'] = await self._calculate_enhancement_metrics(ai_analysis)
            
            # Add optimization scores
            enhanced['optimization_scores'] = await self._calculate_optimization_scores(enhancements)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Enhanced blueprint creation failed: {e}")
            return original_blueprint
    
    async def _generate_final_recommendations(self, enhancements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate final prioritized recommendations."""
        try:
            all_recommendations = []
            
            # Collect all recommendations with priorities
            for category, items in enhancements.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and 'description' in item:
                            all_recommendations.append({
                                'category': category,
                                'priority': item.get('priority', 'medium'),
                                'description': item['description'],
                                'type': item.get('type', 'general'),
                                'impact': self._estimate_impact(item)
                            })
            
            # Sort by priority and impact
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            all_recommendations.sort(
                key=lambda x: (priority_order.get(x['priority'], 1), x.get('impact', 0)), 
                reverse=True
            )
            
            return all_recommendations[:self.config['max_recommendations']]
            
        except Exception as e:
            self.logger.error(f"Final recommendations generation failed: {e}")
            return []
    
    async def _calculate_enhancement_metrics(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for the AI enhancement."""
        try:
            metrics = {}
            
            # Content analysis coverage
            services_used = [service for service, result in ai_analysis.items() if result is not None]
            metrics['analysis_coverage'] = {
                'services_used': services_used,
                'coverage_score': len(services_used) / 4 * 100  # Out of 4 possible services
            }
            
            # Quality assessment
            if 'ml' in ai_analysis and ai_analysis['ml']:
                quality_scores = []
                for result in ai_analysis['ml']:
                    if result and 'quality_score' in result:
                        quality_scores.append(result['quality_score'].get('overall_score', 0))
                
                if quality_scores:
                    metrics['content_quality'] = {
                        'average_score': sum(quality_scores) / len(quality_scores),
                        'score_range': [min(quality_scores), max(quality_scores)]
                    }
            
            # Semantic coherence
            if 'semantic' in ai_analysis and ai_analysis['semantic']:
                diversity = ai_analysis['semantic'].get('diversity', {})
                metrics['semantic_coherence'] = {
                    'diversity_score': diversity.get('diversity_score', 0),
                    'coherence_level': diversity.get('diversity_level', 'Unknown')
                }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Enhancement metrics calculation failed: {e}")
            return {}
    
    async def _calculate_optimization_scores(self, enhancements: Dict[str, Any]) -> Dict[str, float]:
        """Calculate optimization scores for different aspects."""
        try:
            scores = {}
            
            # Content optimization score
            content_optimizations = enhancements.get('content_optimization', [])
            high_priority_count = sum(1 for opt in content_optimizations if opt.get('priority') == 'high')
            scores['content_optimization'] = max(0, 100 - high_priority_count * 20)
            
            # Semantic optimization score
            semantic_insights = enhancements.get('semantic_insights', {})
            diversity = semantic_insights.get('content_diversity', {})
            if diversity:
                scores['semantic_optimization'] = diversity.get('diversity_score', 0) * 100
            else:
                scores['semantic_optimization'] = 75  # Default
            
            # Performance optimization score
            performance = enhancements.get('performance_predictions', {})
            if performance:
                scores['performance_optimization'] = performance.get('predicted_performance', 75)
            else:
                scores['performance_optimization'] = 75  # Default
            
            # Structural optimization score
            structural_recs = enhancements.get('structural_recommendations', [])
            scores['structural_optimization'] = max(0, 100 - len(structural_recs) * 15)
            
            # Overall optimization score
            scores['overall_optimization'] = sum(scores.values()) / len(scores)
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Optimization scores calculation failed: {e}")
            return {}
    
    def _get_similarity_recommendation(self, similarity_stats: Dict[str, float]) -> str:
        """Get recommendation based on similarity statistics."""
        mean_sim = similarity_stats.get('mean_similarity', 0)
        if mean_sim > 0.8:
            return "Content is highly similar - consider diversifying topics"
        elif mean_sim < 0.3:
            return "Content is very diverse - consider adding connecting themes"
        else:
            return "Good balance of similarity and diversity"
    
    def _get_quality_recommendation(self, quality_score: float) -> str:
        """Get recommendation based on quality score."""
        if quality_score < 50:
            return "Significant quality improvements needed"
        elif quality_score < 70:
            return "Moderate quality improvements recommended"
        else:
            return "Good quality maintained"
    
    def _get_performance_tier(self, performance_score: float) -> str:
        """Get performance tier based on score."""
        if performance_score >= 80:
            return "High Performance"
        elif performance_score >= 60:
            return "Good Performance"
        elif performance_score >= 40:
            return "Average Performance"
        else:
            return "Needs Improvement"
    
    def _get_classification_recommendation(self, classifications: List[Dict[str, Any]]) -> str:
        """Get recommendation based on content classifications."""
        types = [c.get('predicted_type', 'unknown') for c in classifications]
        unique_types = set(types)
        
        if len(unique_types) == 1:
            return f"Content is consistently classified as {list(unique_types)[0]} - consider diversifying content types"
        elif len(unique_types) > 3:
            return "Content spans multiple types - ensure coherent messaging"
        else:
            return "Good variety of content types"
    
    def _estimate_impact(self, recommendation: Dict[str, Any]) -> float:
        """Estimate the impact of a recommendation."""
        impact_scores = {
            'readability_improvement': 0.8,
            'entity_enrichment': 0.6,
            'engagement_improvement': 0.7,
            'content_connectivity': 0.9,
            'content_density': 0.5,
            'strategic_gap_filling': 0.9,
            'consistency_optimization': 0.7
        }
        
        rec_type = recommendation.get('type', 'general')
        return impact_scores.get(rec_type, 0.5)