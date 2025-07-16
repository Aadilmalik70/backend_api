"""
Enhanced SERP Feature Optimizer with Real Google APIs Integration - Phase 2.5

This module provides advanced SERP feature optimization functionality using:
- Google Custom Search API for real SERP data
- Google Knowledge Graph API for entity optimization
- Google Gemini AI for intelligent recommendations
- SerpAPI as fallback for reliability

Phase 2.5 Implementation: Multi-tier architecture with AI-powered insights
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Core dependencies
from utils.serpapi_client import SerpAPIClient

# Google APIs Integration (Phase 2.5)
from utils.google_apis.custom_search_client import CustomSearchClient
from utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
from utils.google_apis.gemini_client import GeminiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerpFeatureOptimizerReal:
    """
    Enhanced SERP feature optimizer with Google APIs integration and AI-powered recommendations.
    
    Phase 2.5 Features:
    - Real Google search data via Custom Search API
    - Entity optimization via Knowledge Graph API
    - AI-powered recommendations via Gemini API
    - Multi-tier architecture with SerpAPI fallback
    - Enhanced opportunity scoring and prioritization
    """
    
    def __init__(self, serpapi_key: Optional[str] = None):
        """
        Initialize the enhanced SERP feature optimizer.
        
        Args:
            serpapi_key: SerpAPI key for fallback functionality
        """
        logger.info("Initializing Phase 2.5 Enhanced SERP Feature Optimizer")
        
        # Google APIs Integration (Primary)
        try:
            self.google_search = CustomSearchClient()
            self.knowledge_graph = KnowledgeGraphClient()
            self.gemini_client = GeminiClient()
            self.google_apis_enabled = True
            logger.info("Google APIs clients initialized successfully")
        except Exception as e:
            logger.warning(f"Google APIs initialization failed: {e}")
            self.google_search = None
            self.knowledge_graph = None
            self.gemini_client = None
            self.google_apis_enabled = False
        
        # SerpAPI Fallback
        self.serpapi_client = SerpAPIClient(api_key=serpapi_key)
        
        # Enhanced feature recommendations database
        self.recommendations = {
            "featured_snippets": [
                "Structure content with clear headings and concise paragraphs",
                "Answer the query directly and succinctly at the beginning",
                "Use lists, tables, or step-by-step formats where appropriate",
                "Include the target keyword in the heading and first paragraph",
                "Keep answers between 40-60 words for optimal snippet length",
                "Use question-and-answer format for better extraction",
                "Add relevant statistics and data points",
                "Ensure content is factually accurate and well-sourced"
            ],
            "people_also_ask": [
                "Research related questions using SERP data",
                "Create comprehensive FAQ sections addressing related questions",
                "Structure answers in a concise, direct format",
                "Use schema markup for FAQ content",
                "Link to more detailed content for each question",
                "Address question intent variations",
                "Include long-tail keyword variations",
                "Optimize for voice search queries"
            ],
            "knowledge_panels": [
                "Ensure consistent entity information across the web",
                "Create or claim Google Business Profile if applicable",
                "Use schema markup for organization or person entities",
                "Provide clear 'about' information on your website",
                "Build authoritative backlinks to strengthen entity recognition",
                "Optimize Wikipedia presence if applicable",
                "Maintain consistent NAP (Name, Address, Phone) information",
                "Create comprehensive entity-focused content"
            ],
            "image_packs": [
                "Use high-quality, relevant images with descriptive filenames",
                "Add comprehensive alt text including target keywords",
                "Implement image schema markup",
                "Ensure images are responsive and fast-loading",
                "Place images near relevant text content",
                "Use original, high-resolution images",
                "Optimize image file sizes for performance",
                "Include images in XML sitemaps"
            ],
            "video_results": [
                "Create video content addressing the search query",
                "Optimize video titles and descriptions with target keywords",
                "Add timestamps and transcripts to videos",
                "Embed videos on relevant pages with supporting text",
                "Use video schema markup",
                "Create thumbnail images that attract clicks",
                "Optimize for YouTube search if applicable",
                "Include captions and subtitles"
            ],
            "local_pack": [
                "Create or optimize Google Business Profile",
                "Ensure NAP (Name, Address, Phone) consistency across the web",
                "Collect and respond to reviews",
                "Use local business schema markup",
                "Create location-specific content pages",
                "Build local citations and directories",
                "Optimize for local keywords",
                "Add location pages for multiple locations"
            ],
            "top_stories": [
                "Publish timely, newsworthy content",
                "Follow journalistic standards and cite sources",
                "Use news schema markup",
                "Ensure mobile responsiveness and fast loading",
                "Build authority in the topic area",
                "Create breaking news content",
                "Optimize headlines for click-through",
                "Maintain editorial standards"
            ]
        }
    
    def generate_recommendations(self, keyword: str) -> Dict[str, Any]:
        """
        Generate enhanced SERP feature recommendations using multi-tier architecture.
        
        Args:
            keyword: Target keyword for optimization
            
        Returns:
            Dictionary containing enhanced SERP feature recommendations with AI insights
        """
        logger.info(f"Generating Phase 2.5 enhanced SERP recommendations for: {keyword}")
        
        try:
            # Step 1: Enhanced SERP feature detection
            serp_features = self.detect_serp_features_enhanced(keyword)
            logger.info(f"SERP features detected using: {serp_features.get('data_source', 'unknown')}")
            
            # Step 2: Entity analysis for Knowledge Panel optimization
            entity_optimization = None
            if self._is_entity_query(keyword):
                entity_optimization = self.optimize_for_knowledge_panel(keyword, "")
                logger.info("Knowledge Panel optimization analysis completed")
            
            # Step 3: AI-powered recommendations
            ai_recommendations = None
            if self.google_apis_enabled and self.gemini_client:
                ai_recommendations = self.generate_ai_optimization_recommendations(
                    keyword, "", serp_features
                )
                logger.info("AI-powered recommendations generated")
            
            # Step 4: Compile enhanced recommendations
            enhanced_recommendations = []
            for feature_name, feature_data in serp_features.items():
                if feature_name in ['data_source', 'analysis_metadata']:
                    continue
                    
                feature_rec = {
                    'feature': feature_name,
                    'status': self._determine_enhanced_feature_status(feature_name, feature_data),
                    'opportunity': self._calculate_enhanced_opportunity(feature_name, feature_data, keyword),
                    'recommendations': self._generate_enhanced_feature_recommendations(
                        feature_name, feature_data, ai_recommendations, keyword
                    ),
                    'implementation_priority': self._calculate_implementation_priority(feature_data),
                    'expected_impact': self._estimate_optimization_impact(feature_name, feature_data),
                    'optimization_complexity': self._assess_optimization_complexity(feature_name, feature_data)
                }
                enhanced_recommendations.append(feature_rec)
            
            # Step 5: Create optimization summary
            optimization_summary = self._create_optimization_summary(enhanced_recommendations, keyword)
            
            # Convert serp_features to list format for backward compatibility
            serp_features_list = self._format_serp_features_for_output(serp_features)
            
            result = {
                'keyword': keyword,
                'serp_features': serp_features_list,
                'recommendations': enhanced_recommendations,
                'entity_optimization': entity_optimization,
                'ai_insights': ai_recommendations,
                'optimization_summary': optimization_summary,
                'data_source': serp_features.get('data_source', 'fallback'),
                'analysis_timestamp': datetime.now().isoformat(),
                'google_apis_enabled': self.google_apis_enabled
            }
            
            logger.info(f"Enhanced recommendations generated successfully for: {keyword}")
            return result
            
        except Exception as e:
            logger.error(f"Enhanced recommendations failed for {keyword}: {str(e)}")
            return self._generate_fallback_recommendations(keyword)
    
    def detect_serp_features_enhanced(self, query: str) -> Dict[str, Any]:
        """
        Enhanced SERP feature detection using Google APIs with SerpAPI fallback.
        
        Args:
            query: Search query to analyze
            
        Returns:
            Dictionary containing detected SERP features with enhanced analysis
        """
        if self.google_apis_enabled and self.google_search:
            try:
                logger.info(f"Using Google Custom Search for SERP analysis: {query}")
                return self._detect_features_with_google(query)
            except Exception as e:
                logger.warning(f"Google APIs failed, using SerpAPI fallback: {str(e)}")
                return self._detect_features_with_serpapi_fallback(query)
        else:
            logger.info(f"Using SerpAPI for SERP analysis: {query}")
            return self._detect_features_with_serpapi_fallback(query)
    
    def _detect_features_with_google(self, query: str) -> Dict[str, Any]:
        """
        Detect SERP features using Google Custom Search API.
        
        Args:
            query: Search query to analyze
            
        Returns:
            Dictionary containing SERP features detected from Google data
        """
        # Get search results from Google Custom Search
        search_results = self.google_search.search(query, num_results=10)
        
        # Analyze SERP features from real Google data
        features = {
            'featured_snippets': self._detect_featured_snippets(search_results, query),
            'people_also_ask': self._detect_paa_opportunities(search_results, query),
            'knowledge_panels': self._detect_knowledge_panel_opportunities(search_results, query),
            'image_packs': self._detect_image_opportunities(search_results, query),
            'video_results': self._detect_video_opportunities(search_results, query),
            'local_pack': self._detect_local_opportunities(search_results, query),
            'top_stories': self._detect_news_opportunities(search_results, query),
            'data_source': 'google_custom_search',
            'analysis_metadata': {
                'total_results': search_results.get('search_information', {}).get('total_results', 0),
                'search_time': search_results.get('search_information', {}).get('search_time', 0),
                'items_analyzed': len(search_results.get('items', []))
            }
        }
        
        return features
    
    def _detect_features_with_serpapi_fallback(self, query: str) -> Dict[str, Any]:
        """
        Fallback SERP feature detection using SerpAPI.
        
        Args:
            query: Search query to analyze
            
        Returns:
            Dictionary containing SERP features from SerpAPI
        """
        serp_features = self.serpapi_client.get_serp_features(query)
        
        # Add metadata to indicate fallback usage
        if isinstance(serp_features, dict):
            serp_features['data_source'] = 'serpapi_fallback'
        
        return serp_features
    
    def _detect_featured_snippets(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze potential for featured snippet optimization from Google search results.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            Featured snippet analysis
        """
        items = search_results.get('items', [])
        
        snippet_analysis = {
            'presence': 'none',
            'opportunity_score': 0.0,
            'recommended_format': 'paragraph',
            'target_length': '40-60 words',
            'content_gaps': [],
            'optimization_potential': 'low'
        }
        
        if not items:
            return snippet_analysis
        
        # Analyze top results for snippet patterns
        for i, item in enumerate(items[:3]):
            snippet = item.get('snippet', '')
            title = item.get('title', '')
            
            # Check for answer-style patterns
            if self._is_answer_pattern(snippet, title, query):
                opportunity_score = max(0.9 - (i * 0.2), 0.3)
                
                snippet_analysis.update({
                    'presence': 'detected' if i == 0 else 'opportunity',
                    'opportunity_score': opportunity_score,
                    'current_holder': item.get('displayLink') if i == 0 else None,
                    'recommended_format': self._determine_optimal_snippet_format(snippet, query),
                    'content_gaps': self._identify_content_gaps(snippet, query),
                    'optimization_potential': 'high' if opportunity_score > 0.7 else 'medium'
                })
                break
        
        # Additional analysis for question-based queries
        if any(word in query.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            snippet_analysis['opportunity_score'] = max(snippet_analysis['opportunity_score'], 0.6)
            snippet_analysis['optimization_potential'] = 'high'
        
        return snippet_analysis
    
    def _detect_paa_opportunities(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze People Also Ask opportunities from search results.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            People Also Ask analysis
        """
        return {
            'presence': 'high' if self._has_question_intent(query) else 'medium',
            'opportunity_score': 0.8 if self._has_question_intent(query) else 0.6,
            'related_questions': self._generate_related_questions(query),
            'content_suggestions': [
                f"Create FAQ section addressing variations of: {query}",
                "Add related questions to existing content",
                "Optimize for long-tail question keywords",
                "Structure content with clear question-answer format"
            ],
            'implementation_priority': 'high' if self._has_question_intent(query) else 'medium'
        }
    
    def _detect_knowledge_panel_opportunities(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze Knowledge Panel optimization opportunities.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            Knowledge Panel analysis
        """
        is_entity = self._is_entity_query(query)
        
        return {
            'presence': 'possible' if is_entity else 'unlikely',
            'opportunity_score': 0.7 if is_entity else 0.2,
            'entity_type': self._determine_entity_type(query) if is_entity else None,
            'optimization_strategies': [
                "Implement schema markup for entity type",
                "Ensure consistent entity information across web",
                "Build authoritative backlinks",
                "Create comprehensive entity-focused content"
            ] if is_entity else [
                "Focus on other SERP features for non-entity queries"
            ],
            'knowledge_graph_potential': 'high' if is_entity else 'low'
        }
    
    def _detect_image_opportunities(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze image pack optimization opportunities.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            Image pack analysis
        """
        visual_intent = self._has_visual_intent(query)
        
        return {
            'presence': 'likely' if visual_intent else 'possible',
            'opportunity_score': 0.8 if visual_intent else 0.4,
            'visual_content_potential': 'high' if visual_intent else 'medium',
            'image_optimization_suggestions': [
                "Use high-quality, relevant images",
                "Optimize image filenames with target keywords",
                "Add comprehensive alt text",
                "Implement image schema markup",
                "Ensure fast image loading",
                "Create original visual content"
            ],
            'recommended_image_types': self._suggest_image_types(query)
        }
    
    def _detect_video_opportunities(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze video results optimization opportunities.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            Video results analysis
        """
        video_intent = self._has_video_intent(query)
        
        return {
            'presence': 'likely' if video_intent else 'possible',
            'opportunity_score': 0.9 if video_intent else 0.3,
            'video_content_potential': 'high' if video_intent else 'low',
            'video_optimization_suggestions': [
                "Create video content addressing the query",
                "Optimize video titles and descriptions",
                "Add video transcripts and captions",
                "Use video schema markup",
                "Embed videos with supporting text",
                "Create engaging thumbnails"
            ],
            'recommended_video_types': self._suggest_video_types(query)
        }
    
    def _detect_local_opportunities(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze local pack optimization opportunities.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            Local pack analysis
        """
        local_intent = self._has_local_intent(query)
        
        return {
            'presence': 'likely' if local_intent else 'unlikely',
            'opportunity_score': 0.9 if local_intent else 0.1,
            'local_seo_potential': 'high' if local_intent else 'low',
            'local_optimization_suggestions': [
                "Optimize Google Business Profile",
                "Ensure NAP consistency",
                "Collect and respond to reviews",
                "Use local business schema markup",
                "Create location-specific content"
            ] if local_intent else [
                "Focus on other SERP features for non-local queries"
            ],
            'geographic_targeting': local_intent
        }
    
    def _detect_news_opportunities(self, search_results: Dict, query: str) -> Dict[str, Any]:
        """
        Analyze top stories/news opportunities.
        
        Args:
            search_results: Google Custom Search results
            query: Original search query
            
        Returns:
            News/top stories analysis
        """
        news_intent = self._has_news_intent(query)
        
        return {
            'presence': 'likely' if news_intent else 'unlikely',
            'opportunity_score': 0.8 if news_intent else 0.2,
            'news_content_potential': 'high' if news_intent else 'low',
            'news_optimization_suggestions': [
                "Create timely, newsworthy content",
                "Use news schema markup",
                "Follow journalistic standards",
                "Ensure fast loading and mobile optimization",
                "Build topical authority"
            ] if news_intent else [
                "Focus on evergreen content optimization"
            ],
            'timeliness_factor': 'critical' if news_intent else 'low'
        }
    
    def optimize_for_knowledge_panel(self, entity_name: str, content: str) -> Dict[str, Any]:
        """
        Optimize content for Knowledge Panel appearance using Knowledge Graph API.
        
        Args:
            entity_name: Name of the entity to optimize for
            content: Content to optimize (optional for keyword-only analysis)
            
        Returns:
            Knowledge Panel optimization recommendations
        """
        if not self.knowledge_graph:
            return self._get_fallback_knowledge_panel_optimization(entity_name, content)
        
        try:
            # Get entity data from Knowledge Graph
            entity_data = self.knowledge_graph.search_entities(entity_name, limit=5)
            
            # Analyze entity authority
            authority_analysis = self.knowledge_graph.analyze_entity_authority(entity_name)
            
            return {
                'entity_name': entity_name,
                'entity_verification': {
                    'found_in_kg': len(entity_data.get('entities', [])) > 0,
                    'authority_score': authority_analysis.get('authority_score', 0.0),
                    'authority_level': authority_analysis.get('authority_level', 'none'),
                    'kg_entities': entity_data.get('entities', [])[:3]  # Top 3 matches
                },
                'optimization_recommendations': {
                    'structured_data': self._generate_entity_schema_suggestions(entity_data),
                    'content_optimization': self._analyze_content_entity_alignment(content, entity_data),
                    'authority_building': authority_analysis.get('recommendations', []),
                    'consistency_improvements': self._suggest_entity_consistency_improvements(entity_data)
                },
                'implementation_roadmap': {
                    'immediate': ['Add basic entity schema markup', 'Ensure consistent entity naming'],
                    'short_term': ['Create comprehensive entity content', 'Build relevant backlinks'],
                    'long_term': ['Establish entity authority', 'Expand entity presence']
                },
                'expected_timeline': '3-6 months for initial improvements',
                'data_source': 'google_knowledge_graph'
            }
            
        except Exception as e:
            logger.error(f"Knowledge Panel optimization failed: {str(e)}")
            return self._get_fallback_knowledge_panel_optimization(entity_name, content)
    def generate_ai_optimization_recommendations(self, query: str, content: str, serp_features: Dict) -> Dict[str, Any]:
        """
        Generate AI-powered SERP optimization recommendations using Gemini.
        
        Args:
            query: Target search query
            content: Content to optimize (optional)
            serp_features: Detected SERP features
            
        Returns:
            AI-powered optimization recommendations
        """
        if not self.gemini_client:
            return self._get_fallback_ai_recommendations(query, serp_features)
        
        try:
            # Create comprehensive analysis prompt
            prompt = self._create_optimization_prompt(query, content, serp_features)
            
            # Get AI recommendations
            ai_response = self.gemini_client.generate_content(prompt)
            
            # Handle both string and dict responses
            if isinstance(ai_response, str):
                ai_content = ai_response
                data_source = 'gemini_text'
            elif isinstance(ai_response, dict):
                ai_content = ai_response.get('content', ai_response.get('text', str(ai_response)))
                data_source = ai_response.get('data_source', 'gemini_dict')
            else:
                ai_content = str(ai_response)
                data_source = 'gemini_fallback'
            
            # If it's mock data, use fallback
            if data_source == 'mock' or not ai_content:
                return self._get_fallback_ai_recommendations(query, serp_features)
            
            # Process and structure the recommendations
            structured_recommendations = self._process_ai_recommendations(
                ai_content, serp_features, query
            )
            
            return {
                'query': query,
                'ai_analysis': structured_recommendations,
                'optimization_priorities': self._prioritize_ai_recommendations(structured_recommendations),
                'implementation_roadmap': self._create_ai_implementation_roadmap(structured_recommendations),
                'competitive_insights': self._extract_competitive_insights(ai_content),
                'content_optimization': self._extract_content_optimization_tips(ai_content),
                'data_source': data_source,
                'confidence_score': 0.85  # High confidence for Gemini recommendations
            }
            
        except Exception as e:
            logger.error(f"AI optimization recommendations failed: {str(e)}")
            return self._get_fallback_ai_recommendations(query, serp_features)
    
    def _create_optimization_prompt(self, query: str, content: str, serp_features: Dict) -> str:
        """
        Create comprehensive optimization prompt for Gemini AI.
        
        Args:
            query: Search query
            content: Content to optimize
            serp_features: Detected SERP features
            
        Returns:
            Structured prompt for AI analysis
        """
        # Extract key feature data for prompt
        feature_summary = []
        for feature_name, feature_data in serp_features.items():
            if feature_name in ['data_source', 'analysis_metadata']:
                continue
            
            presence = feature_data.get('presence', 'unknown')
            opportunity = feature_data.get('opportunity_score', 0)
            feature_summary.append(f"{feature_name}: {presence} (opportunity: {opportunity:.1f})")
        
        return f"""
        Analyze this SERP landscape and provide specific, actionable optimization recommendations:
        
        SEARCH QUERY: "{query}"
        
        CURRENT SERP FEATURES DETECTED:
        {chr(10).join(feature_summary)}
        
        CONTENT TO OPTIMIZE: {content[:1000] if content else 'No content provided - focus on keyword-level recommendations'}
        
        Please provide detailed, implementable recommendations for:
        
        1. FEATURED SNIPPET OPTIMIZATION:
           - Optimal content structure and format
           - Ideal answer length and style (40-60 words)
           - Key phrases to include
           - Content positioning strategy
           - Question-answer formatting tips
        
        2. PEOPLE ALSO ASK TARGETING:
           - Related questions to address
           - FAQ section recommendations
           - Content expansion opportunities
           - Long-tail keyword variations
        
        3. KNOWLEDGE PANEL ENHANCEMENT:
           - Entity optimization strategies
           - Schema markup recommendations
           - Authority building tactics
           - Content consistency improvements
        
        4. VISUAL CONTENT OPTIMIZATION:
           - Image optimization strategies
           - Video content opportunities
           - Visual content best practices
           - Rich media integration
        
        5. CONTENT STRUCTURE IMPROVEMENTS:
           - Heading hierarchy optimization
           - Internal linking strategy
           - Content depth and breadth
           - User experience enhancements
        
        6. COMPETITIVE OPPORTUNITIES:
           - Content gaps to exploit
           - SERP feature opportunities
           - Differentiation strategies
           - Quick wins identification
        
        Format your response with specific, implementable recommendations for each area.
        Focus on actionable advice that can be implemented within 1-4 weeks.
        Prioritize recommendations based on potential impact and implementation difficulty.
        """
    
    # Helper methods for analysis and processing
    
    def _is_answer_pattern(self, snippet: str, title: str, query: str) -> bool:
        """
        Check if content follows answer-style patterns suitable for featured snippets.
        
        Args:
            snippet: Content snippet
            title: Page title
            query: Search query
            
        Returns:
            Boolean indicating answer pattern presence
        """
        answer_indicators = [
            # Direct answer patterns
            snippet.lower().startswith(tuple(['the answer', 'yes,', 'no,', 'according to'])),
            
            # Question word matches
            any(word in query.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']) and
            any(word in snippet.lower() for word in ['is', 'are', 'can', 'will', 'does', 'do']),
            
            # List/step patterns
            any(pattern in snippet.lower() for pattern in ['step 1', 'first,', 'steps:', 'ways to']),
            
            # Definition patterns
            any(pattern in snippet.lower() for pattern in ['defined as', 'refers to', 'means', 'is a']),
            
            # Factual patterns
            bool(re.search(r'\\d+', snippet)) and len(snippet.split()) >= 10 and len(snippet.split()) <= 80
        ]
        
        return any(answer_indicators)
    
    def _determine_optimal_snippet_format(self, snippet: str, query: str) -> str:
        """
        Determine optimal format for featured snippet based on query and content analysis.
        """
        if any(word in query.lower() for word in ['steps', 'how to', 'process', 'guide']):
            return 'numbered_list'
        elif any(word in query.lower() for word in ['vs', 'versus', 'compare', 'difference']):
            return 'table'
        elif any(word in query.lower() for word in ['types', 'kinds', 'examples', 'benefits']):
            return 'bulleted_list'
        else:
            return 'paragraph'
    
    def _identify_content_gaps(self, snippet: str, query: str) -> List[str]:
        """
        Identify content gaps for optimization opportunities.
        """
        gaps = []
        
        # Check for missing question variations
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        for word in question_words:
            if word not in snippet.lower() and word in query.lower():
                gaps.append(f"Add content addressing '{word}' questions")
        
        # Check for missing statistical information
        if not re.search(r'\\d+%|\\d+\\s*(percent|million|billion|thousand)', snippet):
            gaps.append("Include relevant statistics and data points")
        
        # Check for missing actionable advice
        action_words = ['steps', 'tips', 'ways', 'methods', 'strategies']
        if not any(word in snippet.lower() for word in action_words):
            gaps.append("Add actionable steps or recommendations")
        
        return gaps[:3]  # Limit to top 3 gaps
    
    def _has_question_intent(self, query: str) -> bool:
        """
        Check if query has question intent suitable for People Also Ask.
        """
        question_indicators = [
            query.endswith('?'),
            query.lower().startswith(tuple(['what', 'how', 'why', 'when', 'where', 'who', 'which'])),
            any(phrase in query.lower() for phrase in ['can i', 'should i', 'is it', 'are there'])
        ]
        return any(question_indicators)
    
    def _generate_related_questions(self, query: str) -> List[str]:
        """
        Generate related questions for People Also Ask optimization.
        """
        base_query = query.lower()
        related = []
        
        question_starters = ['what is', 'how to', 'why does', 'when should', 'where can', 'who is']
        
        for starter in question_starters:
            if not base_query.startswith(starter):
                related.append(f"{starter} {query}")
        
        # Add variation patterns
        variations = [
            f"What are the benefits of {query}?",
            f"How does {query} work?",
            f"Why is {query} important?",
            f"When should you use {query}?"
        ]
        
        related.extend(variations[:2])
        return related[:5]  # Limit to 5 related questions
    
    def _is_entity_query(self, query: str) -> bool:
        """
        Determine if query is entity-focused for Knowledge Panel optimization.
        """
        entity_patterns = [
            # Proper nouns (capitalized words)
            bool(re.search(r'\\b[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*\\b', query)),
            
            # Company/brand indicators
            any(word in query.lower() for word in ['company', 'corporation', 'inc', 'ltd', 'llc']),
            
            # Person indicators
            any(word in query.lower() for word in ['ceo', 'founder', 'author', 'actor', 'director']),
            
            # Place indicators
            any(word in query.lower() for word in ['city', 'country', 'state', 'university', 'museum']),
            
            # Brand indicators
            len(query.split()) <= 3 and query[0].isupper()
        ]
        
        return any(entity_patterns)
    
    def _determine_entity_type(self, query: str) -> str:
        """
        Determine the type of entity for schema markup recommendations.
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['company', 'corporation', 'business', 'inc']):
            return 'Organization'
        elif any(word in query_lower for word in ['ceo', 'founder', 'author', 'actor', 'person']):
            return 'Person'
        elif any(word in query_lower for word in ['city', 'country', 'state', 'location']):
            return 'Place'
        elif any(word in query_lower for word in ['university', 'school', 'college']):
            return 'EducationalOrganization'
        elif any(word in query_lower for word in ['product', 'software', 'app', 'tool']):
            return 'Product'
        else:
            return 'Thing'
    
    def _has_visual_intent(self, query: str) -> bool:
        """
        Check if query has visual intent for image optimization.
        """
        visual_keywords = [
            'image', 'picture', 'photo', 'visual', 'design', 'screenshot',
            'what does', 'look like', 'appearance', 'example', 'diagram'
        ]
        return any(keyword in query.lower() for keyword in visual_keywords)
    
    def _suggest_image_types(self, query: str) -> List[str]:
        """
        Suggest appropriate image types based on query analysis.
        """
        suggestions = ['High-quality featured images', 'Relevant process diagrams']
        
        if 'how to' in query.lower():
            suggestions.extend(['Step-by-step screenshots', 'Tutorial images'])
        if any(word in query.lower() for word in ['product', 'tool', 'software']):
            suggestions.extend(['Product screenshots', 'Feature demonstrations'])
        if any(word in query.lower() for word in ['design', 'template', 'example']):
            suggestions.extend(['Design examples', 'Template galleries'])
        
        return suggestions[:4]
    
    def _has_video_intent(self, query: str) -> bool:
        """
        Check if query has video intent.
        """
        video_keywords = [
            'video', 'tutorial', 'how to', 'guide', 'demo', 'demonstration',
            'review', 'walkthrough', 'training', 'course'
        ]
        return any(keyword in query.lower() for keyword in video_keywords)
    
    def _suggest_video_types(self, query: str) -> List[str]:
        """
        Suggest appropriate video types based on query analysis.
        """
        suggestions = ['Explanatory videos', 'Educational content']
        
        if 'how to' in query.lower():
            suggestions.extend(['Tutorial videos', 'Step-by-step guides'])
        if 'review' in query.lower():
            suggestions.extend(['Product reviews', 'Comparison videos'])
        if any(word in query.lower() for word in ['demo', 'demonstration']):
            suggestions.extend(['Product demos', 'Feature walkthroughs'])
        
        return suggestions[:3]
    
    def _has_local_intent(self, query: str) -> bool:
        """
        Check if query has local search intent.
        """
        local_keywords = [
            'near me', 'nearby', 'close to', 'in', 'local', 'around',
            'directions to', 'hours', 'address', 'phone number'
        ]
        return any(keyword in query.lower() for keyword in local_keywords)
    
    def _has_news_intent(self, query: str) -> bool:
        """
        Check if query has news/timely content intent.
        """
        news_keywords = [
            'news', 'latest', 'recent', 'update', 'today', 'this week',
            'this month', 'current', 'breaking', 'new'
        ]
        return any(keyword in query.lower() for keyword in news_keywords)
    
    def _determine_enhanced_feature_status(self, feature: str, feature_data: Dict[str, Any]) -> str:
        """
        Determine enhanced status description for SERP features.
        """
        presence = feature_data.get('presence', 'none')
        opportunity_score = feature_data.get('opportunity_score', 0)
        
        if presence == 'none':
            if opportunity_score > 0.7:
                return "High opportunity - Feature not present but query is well-suited"
            elif opportunity_score > 0.4:
                return "Medium opportunity - Potential for feature optimization"
            else:
                return "Low opportunity - Feature unlikely for this query type"
        elif presence in ['detected', 'likely']:
            return "Feature present - Optimization opportunity available"
        elif presence in ['possible', 'medium']:
            return "Feature possible - Content optimization may trigger appearance"
        else:
            return "Feature status unclear - Monitor and optimize"
    
    def _calculate_enhanced_opportunity(self, feature: str, feature_data: Dict[str, Any], query: str) -> str:
        """
        Calculate enhanced opportunity level with query-specific analysis.
        """
        base_score = feature_data.get('opportunity_score', 0)
        
        # Query-specific adjustments
        if feature == 'featured_snippets' and self._has_question_intent(query):
            base_score = min(base_score + 0.2, 1.0)
        elif feature == 'knowledge_panels' and self._is_entity_query(query):
            base_score = min(base_score + 0.3, 1.0)
        elif feature == 'local_pack' and self._has_local_intent(query):
            base_score = min(base_score + 0.4, 1.0)
        
        if base_score >= 0.8:
            return "very_high"
        elif base_score >= 0.6:
            return "high"
        elif base_score >= 0.4:
            return "medium"
        elif base_score >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _generate_enhanced_feature_recommendations(self, feature: str, feature_data: Dict[str, Any], 
                                                  ai_recommendations: Dict[str, Any], query: str) -> List[str]:
        """
        Generate enhanced feature-specific recommendations.
        """
        # Base recommendations
        base_recs = self.recommendations.get(feature, [])
        
        # Query-specific enhancements
        enhanced_recs = base_recs.copy()
        
        # Add AI-powered recommendations if available
        if ai_recommendations and ai_recommendations.get('ai_analysis'):
            ai_content = ai_recommendations.get('ai_analysis', {})
            if isinstance(ai_content, dict):
                feature_ai_recs = ai_content.get(f'{feature}_recommendations', [])
                if feature_ai_recs:
                    enhanced_recs.extend(feature_ai_recs[:2])  # Add top 2 AI recommendations
        
        # Add query-specific recommendations
        if feature == 'featured_snippets' and self._has_question_intent(query):
            enhanced_recs.append(f"Directly answer the question: '{query}' in the first paragraph")
        elif feature == 'people_also_ask':
            related_questions = self._generate_related_questions(query)
            enhanced_recs.append(f"Address related questions: {', '.join(related_questions[:2])}")
        
        return enhanced_recs[:8]  # Limit to 8 recommendations
    
    def _calculate_implementation_priority(self, feature_data: Dict[str, Any]) -> str:
        """
        Calculate implementation priority based on opportunity and complexity.
        """
        opportunity_score = feature_data.get('opportunity_score', 0)
        complexity = feature_data.get('optimization_complexity', 'medium')
        
        if opportunity_score >= 0.8:
            return "critical" if complexity != 'high' else "high"
        elif opportunity_score >= 0.6:
            return "high" if complexity == 'low' else "medium"
        elif opportunity_score >= 0.4:
            return "medium" if complexity != 'high' else "low"
        else:
            return "low"
    
    def _estimate_optimization_impact(self, feature: str, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate potential impact of optimization efforts.
        """
        opportunity_score = feature_data.get('opportunity_score', 0)
        
        impact_levels = {
            'traffic_increase': f"{int(opportunity_score * 30)}%-{int(opportunity_score * 50)}%" if opportunity_score > 0.5 else "5%-15%",
            'click_through_rate': f"+{int(opportunity_score * 20)}%" if opportunity_score > 0.4 else "+5%",
            'visibility_improvement': "high" if opportunity_score > 0.7 else "medium" if opportunity_score > 0.4 else "low",
            'timeline': "2-4 weeks" if opportunity_score > 0.6 else "4-8 weeks"
        }
        
        return impact_levels
    
    def _assess_optimization_complexity(self, feature: str, feature_data: Dict[str, Any]) -> str:
        """
        Assess the complexity of optimizing for a specific SERP feature.
        """
        complexity_map = {
            'featured_snippets': 'medium',  # Content restructuring required
            'people_also_ask': 'low',       # FAQ content addition
            'knowledge_panels': 'high',     # Entity optimization, schema markup
            'image_packs': 'low',           # Image optimization
            'video_results': 'medium',      # Video content creation
            'local_pack': 'medium',         # Local SEO optimization
            'top_stories': 'high'           # News content requirements
        }
        
        return complexity_map.get(feature, 'medium')
    
    def _create_optimization_summary(self, recommendations: List[Dict], query: str) -> Dict[str, Any]:
        """
        Create comprehensive optimization summary.
        """
        # Calculate overall scores
        total_opportunities = len([r for r in recommendations if r.get('opportunity') in ['high', 'very_high']])
        critical_priorities = len([r for r in recommendations if r.get('implementation_priority') == 'critical'])
        
        # Identify quick wins
        quick_wins = [
            r['feature'] for r in recommendations 
            if r.get('implementation_priority') in ['critical', 'high'] and 
               r.get('optimization_complexity') == 'low'
        ]
        
        # Calculate estimated timeline
        if critical_priorities >= 3:
            timeline = "6-8 weeks for comprehensive optimization"
        elif total_opportunities >= 2:
            timeline = "4-6 weeks for priority optimizations"
        else:
            timeline = "2-4 weeks for targeted improvements"
        
        return {
            'query': query,
            'total_opportunities': total_opportunities,
            'critical_priorities': critical_priorities,
            'quick_wins': quick_wins,
            'estimated_timeline': timeline,
            'optimization_score': min(total_opportunities * 20, 100),
            'top_recommendations': [
                r['feature'] for r in sorted(
                    recommendations, 
                    key=lambda x: (x.get('implementation_priority') == 'critical', x.get('opportunity_score', 0)), 
                    reverse=True
                )[:3]
            ]
        }
    
    def _format_serp_features_for_output(self, serp_features: Dict) -> List[Dict]:
        """
        Format SERP features dictionary to list format for backward compatibility.
        """
        formatted_features = []
        
        for feature_name, feature_data in serp_features.items():
            if feature_name in ['data_source', 'analysis_metadata']:
                continue
                
            formatted_features.append({
                'name': feature_name,
                'presence': feature_data.get('presence', 'unknown'),
                'data': feature_data
            })
        
        return formatted_features
    
    # AI Processing Methods
    
    def _process_ai_recommendations(self, ai_content: str, serp_features: Dict, query: str) -> Dict[str, Any]:
        """
        Process AI recommendations into structured format.
        """
        # Simple processing - in production, would use more sophisticated NLP
        return {
            'raw_analysis': ai_content,
            'key_insights': self._extract_key_insights(ai_content),
            'priority_actions': self._extract_priority_actions(ai_content),
            'content_improvements': self._extract_content_improvements(ai_content),
            'competitive_advantages': self._extract_competitive_advantages(ai_content)
        }
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """
        Extract key insights from AI recommendations.
        """
        # Simple keyword-based extraction
        insights = []
        if not content:  # Handle empty content gracefully
            return ['Focus on high-opportunity SERP features', 'Optimize content structure', 'Monitor performance']
            
        sentences = content.split('.')
        
        for sentence in sentences:
            if sentence and any(keyword in sentence.lower() for keyword in ['optimize', 'improve', 'focus', 'target']):
                insights.append(sentence.strip())
        
        return insights[:5] if insights else ['Focus on high-opportunity SERP features']  # Top 5 insights
    
    def _extract_priority_actions(self, content: str) -> List[str]:
        """
        Extract priority actions from AI content.
        """
        actions = []
        lines = content.split('\
')
        
        for line in lines:
            if any(indicator in line.lower() for indicator in ['- ', '1.', '2.', '3.', 'step', 'action']):
                cleaned = line.strip().lstrip('- 123456789.').strip()
                if cleaned and len(cleaned) > 10:
                    actions.append(cleaned)
        
        return actions[:6]  # Top 6 actions
    
    def _extract_content_improvements(self, content: str) -> List[str]:
        """
        Extract content improvement recommendations.
        """
        improvements = []
        content_keywords = ['content', 'structure', 'heading', 'paragraph', 'format', 'organize']
        
        sentences = content.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in content_keywords):
                improvements.append(sentence.strip())
        
        return improvements[:4]  # Top 4 improvements
    
    def _extract_competitive_advantages(self, content: str) -> List[str]:
        """
        Extract competitive advantage opportunities.
        """
        advantages = []
        competitive_keywords = ['competitor', 'advantage', 'opportunity', 'gap', 'differentiate']
        
        sentences = content.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in competitive_keywords):
                advantages.append(sentence.strip())
        
        return advantages[:3]  # Top 3 advantages
    
    def _prioritize_ai_recommendations(self, structured_recs: Dict) -> Dict[str, Any]:
        """
        Prioritize AI recommendations by impact and effort.
        """
        return {
            'immediate': structured_recs.get('priority_actions', [])[:2],
            'short_term': structured_recs.get('content_improvements', [])[:2],
            'long_term': structured_recs.get('competitive_advantages', [])[:2]
        }
    
    def _create_ai_implementation_roadmap(self, structured_recs: Dict) -> Dict[str, Any]:
        """
        Create implementation roadmap from AI recommendations.
        """
        return {
            'week_1': 'Implement immediate priority actions',
            'week_2_4': 'Focus on content structure improvements',
            'week_5_8': 'Build competitive advantages and authority',
            'ongoing': 'Monitor performance and iterate'
        }
    
    def _extract_competitive_insights(self, content: str) -> List[str]:
        """
        Extract competitive insights from AI analysis.
        """
        insights = []
        insight_indicators = ['competitor', 'market', 'industry', 'benchmark']
        
        sentences = content.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in insight_indicators):
                insights.append(sentence.strip())
        
        return insights[:3]
    
    def _extract_content_optimization_tips(self, content: str) -> List[str]:
        """
        Extract content optimization tips from AI analysis.
        """
        tips = []
        tip_indicators = ['tip', 'recommend', 'suggest', 'should', 'consider']
        
        sentences = content.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in tip_indicators):
                tips.append(sentence.strip())
        
        return tips[:4]
    
    # Fallback Methods
    
    def _generate_fallback_recommendations(self, keyword: str) -> Dict[str, Any]:
        """
        Generate fallback recommendations when Google APIs fail.
        """
        logger.info(f"Generating fallback recommendations for: {keyword}")
        
        # Use original SerpAPI-based method as fallback
        serp_features_dict = self.serpapi_client.get_serp_features(keyword)
        
        # Convert to list format
        serp_features_list = []
        for feature_name, feature_data in serp_features_dict.items():
            feature_item = {
                "name": feature_name,
                "presence": feature_data.get("presence", "none"),
                "data": feature_data
            }
            serp_features_list.append(feature_item)
        
        # Generate basic recommendations
        recommendations_list = []
        for feature_name, feature_data in serp_features_dict.items():
            presence = feature_data.get("presence", "none")
            
            if presence == "none":
                opportunity = self._determine_opportunity_for_missing_feature(feature_name, keyword, {})
            else:
                opportunity = self._determine_opportunity_for_present_feature(feature_name, feature_data, {})
            
            feature_recommendations = self._generate_feature_specific_recommendations(
                feature_name, opportunity, feature_data, {}
            )
            
            recommendations_list.append({
                "feature": feature_name,
                "status": self._determine_feature_status(feature_name, feature_data),
                "opportunity": opportunity,
                "recommendations": feature_recommendations
            })
        
        return {
            "keyword": keyword,
            "serp_features": serp_features_list,
            "recommendations": recommendations_list,
            "data_source": "serpapi_fallback",
            "note": "Using fallback recommendations - Configure Google APIs for enhanced features"
        }
    
    def _get_fallback_knowledge_panel_optimization(self, entity_name: str, content: str) -> Dict[str, Any]:
        """
        Fallback knowledge panel optimization when Google APIs are unavailable.
        """
        return {
            'entity_name': entity_name,
            'entity_verification': {
                'found_in_kg': False,
                'authority_score': 0.0,
                'authority_level': 'unknown',
                'kg_entities': []
            },
            'optimization_recommendations': {
                'structured_data': ['Add basic Organization or Person schema markup'],
                'content_optimization': ['Create entity-focused content pages'],
                'authority_building': ['Build relevant backlinks', 'Ensure consistent NAP information'],
                'consistency_improvements': ['Maintain consistent entity naming across web']
            },
            'implementation_roadmap': {
                'immediate': ['Add basic schema markup'],
                'short_term': ['Create entity content'],
                'long_term': ['Build entity authority']
            },
            'expected_timeline': '4-8 weeks for basic improvements',
            'data_source': 'fallback',
            'note': 'Configure Google Knowledge Graph API for enhanced entity analysis'
        }
    
    def _get_fallback_ai_recommendations(self, query: str, serp_features: Dict) -> Dict[str, Any]:
        """
        Fallback AI recommendations when Gemini API is unavailable.
        """
        return {
            'query': query,
            'ai_analysis': {
                'raw_analysis': 'AI analysis unavailable - configure Gemini API for enhanced insights',
                'key_insights': [
                    'Focus on high-opportunity SERP features',
                    'Optimize content structure for featured snippets',
                    'Create FAQ sections for People Also Ask',
                    'Ensure mobile-friendly and fast-loading content'
                ],
                'priority_actions': [
                    'Analyze current SERP features for the target keyword',
                    'Optimize content structure and formatting',
                    'Add schema markup where applicable',
                    'Monitor SERP feature changes over time'
                ],
                'content_improvements': [
                    'Use clear headings and subheadings',
                    'Structure content for easy scanning',
                    'Include relevant images and media',
                    'Optimize for user intent and search queries'
                ],
                'competitive_advantages': [
                    'Identify content gaps in competitor pages',
                    'Create more comprehensive content',
                    'Focus on unique value propositions'
                ]
            },
            'optimization_priorities': {
                'immediate': ['Content structure optimization', 'Basic schema markup'],
                'short_term': ['FAQ section creation', 'Image optimization'],
                'long_term': ['Authority building', 'Comprehensive content expansion']
            },
            'implementation_roadmap': {
                'week_1': 'Basic content structure improvements',
                'week_2_4': 'SERP feature optimization',
                'week_5_8': 'Authority and content expansion',
                'ongoing': 'Monitor and iterate'
            },
            'competitive_insights': ['Manual competitor analysis recommended'],
            'content_optimization': ['Focus on user intent and search query alignment'],
            'data_source': 'fallback',
            'confidence_score': 0.5,
            'note': 'Configure Gemini API for AI-powered insights'
        }
    
    def _generate_entity_schema_suggestions(self, entity_data: Dict) -> List[str]:
        """
        Generate schema markup suggestions based on entity data.
        """
        suggestions = ['Add basic entity schema markup']
        
        if entity_data.get('entities'):
            entity = entity_data['entities'][0]
            entity_types = entity.get('types', [])
            
            if 'Organization' in entity_types:
                suggestions.extend([
                    'Implement Organization schema markup',
                    'Add address and contact information',
                    'Include founding date and key facts'
                ])
            elif 'Person' in entity_types:
                suggestions.extend([
                    'Implement Person schema markup',
                    'Add biographical information',
                    'Include professional details and achievements'
                ])
            else:
                suggestions.extend([
                    'Implement appropriate Thing schema markup',
                    'Add descriptive properties',
                    'Include relevant relationships'
                ])
        else:
            suggestions.extend([
                'Start with basic schema markup',
                'Add structured data for entity type',
                'Include key entity properties'
            ])
        
        return suggestions
    
    def _analyze_content_entity_alignment(self, content: str, entity_data: Dict) -> List[str]:
        """
        Analyze how well content aligns with entity information.
        """
        alignment_suggestions = []
        
        if not content:
            alignment_suggestions.append('Create comprehensive entity-focused content')
            return alignment_suggestions
        
        # Basic content analysis
        if entity_data.get('entities'):
            entity = entity_data['entities'][0]
            entity_name = entity.get('name', '')
            entity_description = entity.get('description', '')
            
            if entity_name and entity_name.lower() not in content.lower():
                alignment_suggestions.append(f'Include entity name "{entity_name}" prominently in content')
            
            if entity_description and not any(word in content.lower() for word in entity_description.lower().split()[:3]):
                alignment_suggestions.append('Align content with entity description from Knowledge Graph')
        
        # General alignment recommendations
        alignment_suggestions.extend([
            'Ensure content accurately represents the entity',
            'Include key facts and information about the entity',
            'Maintain consistent entity representation across pages'
        ])
        
        return alignment_suggestions[:5]
    
    def _suggest_entity_consistency_improvements(self, entity_data: Dict) -> List[str]:
        """
        Suggest improvements for entity consistency across the web.
        """
        return [
            'Ensure consistent entity naming across all web properties',
            'Maintain consistent NAP (Name, Address, Phone) information',
            'Update social media profiles with consistent information',
            'Claim and optimize relevant directory listings',
            'Build authoritative backlinks to strengthen entity recognition'
        ]
    
    # Original methods for backward compatibility
    
    def _determine_opportunity_for_missing_feature(self, feature: str, input_text: str, competitor_data: Dict[str, Any]) -> str:
        """
        Determine opportunity level for a missing SERP feature.
        
        Args:
            feature: SERP feature name
            input_text: The original user input text
            competitor_data: Competitor analysis data
            
        Returns:
            Opportunity level as string
        """
        # Check if the query type is suitable for this feature
        query_suitability = self._assess_query_feature_match(feature, input_text)
        
        if query_suitability == "high":
            return "high"
        elif query_suitability == "medium":
            return "medium"
        else:
            return "low"
    
    def _determine_opportunity_for_present_feature(self, feature: str, feature_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> str:
        """
        Determine opportunity level for a present SERP feature.
        
        Args:
            feature: SERP feature name
            feature_data: Feature data from SERP
            competitor_data: Competitor analysis data
            
        Returns:
            Opportunity level as string
        """
        # If competitors are dominating this feature, it's still a medium opportunity
        competitor_presence = self._check_competitor_feature_presence(feature, competitor_data)
        
        if competitor_presence == "strong":
            return "medium"
        else:
            return "low"
    
    def _assess_query_feature_match(self, feature: str, query: str) -> str:
        """
        Assess how well a query matches a SERP feature.
        
        Args:
            feature: SERP feature name
            query: Search query
            
        Returns:
            Match level as string
        """
        query_lower = query.lower()
        
        # Feature-specific patterns that indicate suitability
        feature_patterns = {
            "featured_snippets": ["what", "how", "why", "when", "where", "which", "who", "is", "are", "can", "does", "do"],
            "people_also_ask": ["what", "how", "why", "when", "where", "which", "who", "is", "are", "can", "does", "do"],
            "knowledge_panels": ["about", "who is", "what is", "definition", "meaning"],
            "image_packs": ["image", "picture", "photo", "visual", "what does", "look like", "design", "example"],
            "video_results": ["video", "how to", "tutorial", "guide", "watch", "review"],
            "local_pack": ["near me", "nearby", "in", "close to", "around", "local", "where"],
            "top_stories": ["news", "latest", "update", "recent", "today", "this week", "this month", "current"]
        }
        
        patterns = feature_patterns.get(feature, [])
        
        # Check if query contains any of the patterns
        for pattern in patterns:
            if pattern in query_lower:
                return "high"
        
        # Check if query length and structure might be suitable
        if feature in ["featured_snippets", "people_also_ask"] and len(query_lower.split()) >= 3:
            return "medium"
        
        return "low"
    
    def _check_competitor_feature_presence(self, feature: str, competitor_data: Dict[str, Any]) -> str:
        """
        Check competitor presence for a SERP feature.
        
        Args:
            feature: SERP feature name
            competitor_data: Competitor analysis data
            
        Returns:
            Presence level as string
        """
        # In a real implementation, this would analyze competitor content
        # For now, we'll return a default value
        return "moderate"
    
    def _determine_feature_status(self, feature: str, feature_data: Dict[str, Any]) -> str:
        """
        Determine the current status of a SERP feature.
        
        Args:
            feature: SERP feature name
            feature_data: Feature data from SERP
            
        Returns:
            Status description as string
        """
        presence = feature_data.get("presence", "none")
        
        if presence == "none":
            return "Not present in current SERP"
        elif presence == "weak":
            return "Present but not prominent in current SERP"
        else:
            return "Prominently featured in current SERP"
    
    def _generate_feature_specific_recommendations(self, feature: str, opportunity: str, feature_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> List[str]:
        """
        Generate specific recommendations for a SERP feature.
        
        Args:
            feature: SERP feature name
            opportunity: Opportunity level
            feature_data: Feature data from SERP
            competitor_data: Competitor analysis data
            
        Returns:
            List of recommendations
        """
        # Get base recommendations for this feature
        base_recommendations = self.recommendations.get(feature, [])
        
        # In a real implementation, we would customize these based on the specific SERP data
        # For now, we'll return the base recommendations
        return base_recommendations