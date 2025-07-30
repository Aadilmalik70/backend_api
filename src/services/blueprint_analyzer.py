"""
Blueprint Analyzer - Content and competitor analysis methods.

This module handles competitor analysis, content analysis, and SERP feature analysis
for blueprint generation.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    # Try absolute imports from src directory
    from competitor_analysis_real import CompetitorAnalysisReal
    from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
    from serp_feature_optimizer_real import SerpFeatureOptimizerReal
    from utils.quick_competitor_analyzer import QuickCompetitorAnalyzer
    from utils.google_apis.migration_manager import MigrationManager as get_migration_manager
    logger.info("Successfully imported all modules with absolute imports")
except ImportError as e:
    # Fallback to relative imports
    logger.warning(f"Absolute imports failed: {e}, trying relative imports")
    try:
        import sys
        import os
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from competitor_analysis_real import CompetitorAnalysisReal
        from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal  
        from serp_feature_optimizer_real import SerpFeatureOptimizerReal
        from utils.quick_competitor_analyzer import QuickCompetitorAnalyzer
        from utils.google_apis.migration_manager import MigrationManager as get_migration_manager
        logger.info("Successfully imported all modules with path adjustment")
    except ImportError as e2:
        logger.error(f"Both import methods failed: {e2}")
        # Create fallback placeholder classes
        class CompetitorAnalysisReal:
            def __init__(self, *args, **kwargs): pass
        class ContentAnalyzerEnhancedReal:
            def __init__(self, *args, **kwargs): pass
        class SerpFeatureOptimizerReal:
            def __init__(self, *args, **kwargs): pass
        class QuickCompetitorAnalyzer:
            def __init__(self, *args, **kwargs): pass
            def analyze_competitors_quick(self, keyword): return {"analysis_status": "fallback"}
        def get_migration_manager(): return None
        logger.warning("Using fallback placeholder classes due to import failures")
from .blueprint_utils import (
    is_google_apis_enabled,
    get_fallback_competitors,
    get_fallback_serp_features,
    get_fallback_content_insights,
    safe_execution
)

class BlueprintAnalyzer:
    """
    Analyzer for competitor, content, and SERP feature analysis.
    """
    
    def __init__(self, serpapi_key: str, gemini_api_key: str):
        """
        Initialize the analyzer with API credentials.
        
        Args:
            serpapi_key: SerpAPI key for search data
            gemini_api_key: Google Gemini API key for AI processing
        """
        self.serpapi_key = serpapi_key
        self.gemini_api_key = gemini_api_key
        
        # Initialize analysis services
        try:
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
            
            logger.info("Blueprint analyzer services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize blueprint analyzer: {str(e)}")
            raise Exception(f"Blueprint analyzer initialization failed: {str(e)}")
    
    def analyze_competitors(self, keyword: str) -> Dict[str, Any]:
        """Analyze competitors for the given keyword with timeout protection."""
        try:
            # Check if Google APIs are enabled and get migration manager
            migration_manager = get_migration_manager()

            if  migration_manager:
                logger.info(f"🚀 Using Google APIs (migration manager) for competitor analysis: {keyword}")
                try:
                    competitors = migration_manager.get_competitors_analysis(keyword)
                    logger.info(f"✅ Competitor analysis completed with Google APIs for: {keyword}")
                    return competitors
                except Exception as e:
                    logger.warning(f"⚠️  Google APIs competitor analysis failed: {e}")
            else:
                logger.info("⚠️  Google APIs not available, using fallback methods")
            
            # Fallback to quick analyzer
            logger.info(f"Using quick competitor analysis for: {keyword}")
            success, competitors, error = safe_execution(
                self.quick_analyzer.analyze_competitors_quick, keyword
            )
            
            if success and competitors:
                logger.info(f"Successfully analyzed competitors for keyword: {keyword}")
                return competitors
            else:
                logger.warning(f"Quick competitor analysis failed: {error}")
                
        except Exception as e:
            logger.warning(f"All competitor analysis methods failed for '{keyword}': {str(e)}")
        
        logger.info(f"Using fallback competitor data for: {keyword}")
        return get_fallback_competitors(keyword)
    
    def analyze_serp_features(self, keyword: str) -> Dict[str, Any]:
        """Analyze SERP features for the given keyword."""
        try:
            # Check if Google APIs are enabled and get migration manager
            migration_manager = get_migration_manager()
            
            if  migration_manager:
                logger.info(f"🚀 Using Google APIs (migration manager) for SERP analysis: {keyword}")
                try:
                    serp_optimization = migration_manager.optimize_serp_features(keyword)
                    logger.info(f"✅ SERP optimization completed with Google APIs for: {keyword}")
                    return serp_optimization
                except Exception as e:
                    logger.warning(f"⚠️  Google APIs SERP analysis failed: {e}")
            else:
                logger.info("⚠️  Google APIs not available, using fallback SERP analysis")
            
            # Fallback to SerpFeatureOptimizer
            success, serp_features, error = safe_execution(
                self.serp_optimizer.generate_recommendations, keyword
            )
            
            if success and serp_features:
                logger.info(f"Successfully analyzed SERP features for keyword: {keyword}")
                return serp_features
            else:
                logger.warning(f"SERP feature analysis failed: {error}")
                
        except Exception as e:
            logger.warning(f"SERP feature analysis failed for '{keyword}': {str(e)}")
        
        return get_fallback_serp_features(keyword, str(e) if 'e' in locals() else "Analysis failed")
    
    def analyze_competitor_content(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
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
                        success, analysis, error = safe_execution(
                            self.content_analyzer.analyze_url, url
                        )
                        
                        if success and analysis:
                            # Extract word count and sections
                            if 'content_analysis' in analysis:
                                content_data = analysis['content_analysis']
                                word_counts.append(content_data.get('word_count', 0))
                                
                                # Extract headings/sections
                                headings = content_data.get('headings', [])
                                all_sections.extend(headings)
                        else:
                            logger.warning(f"Failed to analyze competitor URL {url}: {error}")
                
                except Exception as e:
                    logger.warning(f"Failed to analyze competitor URL: {str(e)}")
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
    
    def analyze_content_gaps(self, competitors: Dict[str, Any], 
                           target_keyword: str) -> Dict[str, Any]:
        """Analyze content gaps and opportunities."""
        try:
            gaps_analysis = {
                'missing_topics': [],
                'underserved_keywords': [],
                'content_opportunities': [],
                'format_gaps': [],
                'analysis_status': 'completed'
            }
            
            # Extract common topics from competitors
            competitor_topics = set()
            if 'insights' in competitors and 'common_topics' in competitors['insights']:
                competitor_topics.update(competitors['insights']['common_topics'])
            
            # Basic gap analysis
            keyword_variations = [
                f"{target_keyword} guide",
                f"{target_keyword} tutorial", 
                f"{target_keyword} tips",
                f"{target_keyword} best practices",
                f"how to {target_keyword}",
                f"{target_keyword} examples",
                f"{target_keyword} tools",
                f"{target_keyword} strategy"
            ]
            
            # Find potential gaps
            for variation in keyword_variations:
                if not any(topic.lower() in variation.lower() for topic in competitor_topics):
                    gaps_analysis['missing_topics'].append(variation)
            
            # Content format opportunities
            gaps_analysis['format_gaps'] = [
                'Interactive tools or calculators',
                'Video tutorials',
                'Downloadable templates', 
                'Case studies',
                'Comparison charts',
                'FAQ sections'
            ]
            
            # Content opportunities
            gaps_analysis['content_opportunities'] = [
                f"Comprehensive {target_keyword} beginner guide",
                f"Advanced {target_keyword} techniques",
                f"{target_keyword} troubleshooting guide",
                f"{target_keyword} industry trends and updates"
            ]
            
            logger.info("Content gap analysis completed successfully")
            return gaps_analysis
            
        except Exception as e:
            logger.warning(f"Content gap analysis failed: {str(e)}")
            return {
                'missing_topics': [],
                'underserved_keywords': [],
                'content_opportunities': [],
                'format_gaps': [],
                'analysis_status': 'failed',
                'error': str(e)
            }
    
    def get_comprehensive_analysis(self, keyword: str, competitors: dict = None) -> Dict[str, Any]:
        """Get comprehensive analysis combining all analysis methods.
        If competitors is provided, use it instead of running competitor analysis.
        """
        logger.info(f"Starting comprehensive analysis for keyword: {keyword}")
        
        try:
            # Step 1: Competitor Analysis
            logger.info("Step 1: Analyzing competitors")
            if competitors is None:
                competitors = self.analyze_competitors(keyword)
            
            # Step 2: SERP Features Analysis
            logger.info("Step 2: Analyzing SERP features")
            serp_features = self.analyze_serp_features(keyword)
            
            # Step 3: Content Analysis
            logger.info("Step 3: Analyzing competitor content")
            content_insights = self.analyze_competitor_content(competitors)
            
            # Step 4: Gap Analysis
            logger.info("Step 4: Analyzing content gaps")
            content_gaps = self.analyze_content_gaps(competitors, keyword)
            
            comprehensive_analysis = {
                'keyword': keyword,
                'competitors': competitors,
                'serp_features': serp_features,
                'content_insights': content_insights,
                'content_gaps': content_gaps,
                'analysis_metadata': {
                    'total_components': 4,
                    'successful_components': sum([
                        1 if competitors.get('analysis_status') != 'fallback' else 0,
                        1 if serp_features.get('analysis_status') != 'fallback' else 0,
                        1 if content_insights.get('analysis_status') == 'completed' else 0,
                        1 if content_gaps.get('analysis_status') == 'completed' else 0
                    ]),
                    'analysis_quality': 'high' if all([
                        competitors.get('analysis_status') != 'fallback',
                        serp_features.get('analysis_status') != 'fallback',
                        content_insights.get('analysis_status') == 'completed'
                    ]) else 'medium'
                }
            }
            
            logger.info(f"Comprehensive analysis completed for keyword: {keyword}")
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for keyword '{keyword}': {str(e)}")
            raise Exception(f"Comprehensive analysis failed: {str(e)}")
    
    def analyze_content_with_google_apis(self, text: str) -> Dict[str, Any]:
        """Analyze content using Google APIs Natural Language API."""
        try:
            google_apis_enabled = is_google_apis_enabled()
            migration_manager = get_migration_manager()
            
            if google_apis_enabled and migration_manager:
                logger.info("🚀 Using Google APIs for content analysis")
                try:
                    content_analysis = migration_manager.analyze_content(
                        f"Content analysis for: {text[:100]}..."
                    )
                    logger.info("✅ Content analysis completed with Google APIs")
                    return content_analysis
                except Exception as e:
                    logger.warning(f"⚠️  Google APIs content analysis failed: {e}")
                    return {"error": str(e)}
            else:
                logger.info("⚠️  Google APIs not available for content analysis")
                return {"error": "Google APIs not available"}
                
        except Exception as e:
            logger.warning(f"Content analysis with Google APIs failed: {str(e)}")
            return {"error": str(e)}
    
    def analyze_entities_with_google_apis(self, entities: List[str]) -> Dict[str, Any]:
        """Analyze entities using Google Knowledge Graph API."""
        try:
            migration_manager = get_migration_manager()
            
            if  migration_manager:
                logger.info("🚀 Using Google APIs for entity analysis")
                try:
                    entity_analysis = migration_manager.verify_entities(entities)
                    logger.info("✅ Entity analysis completed with Google APIs")
                    return entity_analysis
                except Exception as e:
                    logger.warning(f"⚠️  Google APIs entity analysis failed: {e}")
                    return {"error": str(e)}
            else:
                logger.info("⚠️  Google APIs not available for entity analysis")
                return {"error": "Google APIs not available"}
                
        except Exception as e:
            logger.warning(f"Entity analysis with Google APIs failed: {str(e)}")
            return {"error": str(e)}
    
    def get_serp_data_with_google_apis(self, keyword: str) -> Dict[str, Any]:
        """Get SERP data using Google Custom Search API."""
        try:
            migration_manager = get_migration_manager()
            
            if  migration_manager:
                logger.info(f"🚀 Using Google APIs for SERP data: {keyword}")
                try:
                    serp_data = migration_manager.get_serp_data(keyword)
                    logger.info(f"✅ SERP data completed with Google APIs for: {keyword}")
                    return serp_data
                except Exception as e:
                    logger.warning(f"⚠️  Google APIs SERP data failed: {e}")
                    return {"error": str(e)}
            else:
                logger.info("⚠️  Google APIs not available for SERP data")
                return {"error": "Google APIs not available"}
                
        except Exception as e:
            logger.warning(f"SERP data with Google APIs failed: {str(e)}")
            return {"error": str(e)}
