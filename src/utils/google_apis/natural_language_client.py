"""
Google Natural Language API Client

Provides integration with Google Cloud Natural Language API for content analysis,
entity extraction, sentiment analysis, and content optimization.
"""

import os
import logging
from typing import Dict, Any, List, Optional

try:
    from google.cloud import language_v1
    from google.oauth2 import service_account
except ImportError:
    language_v1 = None
    service_account = None

# Configure logging
logger = logging.getLogger(__name__)

class NaturalLanguageClient:
    """
    Google Cloud Natural Language API client for content analysis
    """
    
    def __init__(self):
        """Initialize Natural Language client"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google Natural Language service"""
        try:
            if not language_v1 or not service_account:
                logger.warning("Google Cloud Natural Language library not installed")
                return
            
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_path or not os.path.exists(credentials_path):
                logger.warning("Google service account credentials not found")
                return
            
            # Create credentials and client
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = language_v1.LanguageServiceClient(credentials=credentials)
            
            logger.info("Natural Language client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Natural Language client: {e}")
    
    def analyze_content(self, content: str, analyze_entities: bool = True, 
                       analyze_sentiment: bool = True, analyze_syntax: bool = False) -> Dict[str, Any]:
        """
        Comprehensive content analysis
        
        Args:
            content: Text content to analyze
            analyze_entities: Whether to extract entities
            analyze_sentiment: Whether to analyze sentiment
            analyze_syntax: Whether to analyze syntax
            
        Returns:
            Complete content analysis
        """
        if not self.client:
            return self._get_mock_content_analysis(content)
        
        try:
            # Prepare document
            document = language_v1.Document(
                content=content,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            analysis_results = {
                'content_length': len(content),
                'word_count': len(content.split()),
                'analysis_features': []
            }
            
            # Entity analysis
            if analyze_entities:
                entities_response = self.client.analyze_entities(
                    request={'document': document}
                )
                analysis_results['entities'] = self._process_entities(entities_response.entities)
                analysis_results['analysis_features'].append('entities')
            
            # Sentiment analysis
            if analyze_sentiment:
                sentiment_response = self.client.analyze_sentiment(
                    request={'document': document}
                )
                analysis_results['sentiment'] = self._process_sentiment(sentiment_response)
                analysis_results['analysis_features'].append('sentiment')
            
            # Syntax analysis
            if analyze_syntax:
                syntax_response = self.client.analyze_syntax(
                    request={'document': document}
                )
                analysis_results['syntax'] = self._process_syntax(syntax_response.tokens)
                analysis_results['analysis_features'].append('syntax')
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return self._get_mock_content_analysis(content)
    
    def extract_entities(self, content: str, entity_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Extract entities from content
        
        Args:
            content: Text content to analyze
            entity_types: Filter by specific entity types
            
        Returns:
            List of extracted entities
        """
        analysis = self.analyze_content(content, analyze_entities=True, 
                                      analyze_sentiment=False, analyze_syntax=False)
        
        entities = analysis.get('entities', [])
        
        # Filter by entity types if specified
        if entity_types:
            entities = [e for e in entities if e['type'] in entity_types]
        
        return entities
    
    def analyze_content_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze content sentiment
        
        Args:
            content: Text content to analyze
            
        Returns:
            Sentiment analysis results
        """
        analysis = self.analyze_content(content, analyze_entities=False, 
                                      analyze_sentiment=True, analyze_syntax=False)
        
        return analysis.get('sentiment', {})
    
    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze content quality for SEO optimization
        
        Args:
            content: Text content to analyze
            
        Returns:
            Content quality analysis
        """
        # Get full analysis
        analysis = self.analyze_content(content, analyze_entities=True, 
                                      analyze_sentiment=True, analyze_syntax=True)
        
        # Calculate quality metrics
        word_count = analysis['word_count']
        entities = analysis.get('entities', [])
        sentiment = analysis.get('sentiment', {})
        
        # Quality scoring
        quality_score = 0.0
        recommendations = []
        
        # Word count scoring
        if word_count >= 300:
            quality_score += 0.2
        else:
            recommendations.append(f"Consider expanding content (current: {word_count} words, recommended: 300+)")
        
        # Entity diversity scoring
        entity_count = len(entities)
        if entity_count >= 5:
            quality_score += 0.2
        else:
            recommendations.append(f"Add more relevant entities (current: {entity_count}, recommended: 5+)")
        
        # Sentiment scoring (neutral to positive is good for most content)
        sentiment_score = sentiment.get('score', 0)
        if sentiment_score >= -0.1:  # Neutral to positive
            quality_score += 0.15
        else:
            recommendations.append("Consider adjusting tone to be more neutral or positive")
        
        # Entity salience scoring (entities should be well-distributed)
        if entities:
            avg_salience = sum(e['salience'] for e in entities) / len(entities)
            if avg_salience >= 0.1:
                quality_score += 0.15
            else:
                recommendations.append("Improve entity prominence and relevance")
        
        # Readability estimation (simplified)
        avg_sentence_length = word_count / max(content.count('.'), 1)
        if 15 <= avg_sentence_length <= 25:
            quality_score += 0.1
        else:
            recommendations.append("Optimize sentence length for better readability")
        
        # Content structure (simplified check for headings)
        if any(line.strip().isupper() or line.startswith('#') for line in content.split('\n')):
            quality_score += 0.1
        else:
            recommendations.append("Add headings and structure to improve content organization")
        
        # Final quality assessment
        if quality_score >= 0.8:
            quality_level = 'excellent'
        elif quality_score >= 0.6:
            quality_level = 'good'
        elif quality_score >= 0.4:
            quality_level = 'fair'
        else:
            quality_level = 'needs_improvement'
        
        return {
            'quality_score': quality_score,
            'quality_level': quality_level,
            'content_metrics': {
                'word_count': word_count,
                'entity_count': entity_count,
                'sentiment_score': sentiment_score,
                'avg_sentence_length': avg_sentence_length
            },
            'recommendations': recommendations,
            'detailed_analysis': analysis
        }
    
    def suggest_content_improvements(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Suggest content improvements for SEO
        
        Args:
            content: Text content to analyze
            target_keywords: Keywords to optimize for
            
        Returns:
            Content improvement suggestions
        """
        quality_analysis = self.analyze_content_quality(content)
        entities = quality_analysis['detailed_analysis'].get('entities', [])
        
        suggestions = {
            'content_optimization': [],
            'entity_enhancement': [],
            'keyword_optimization': [],
            'structure_improvements': []
        }
        
        # Content optimization suggestions
        word_count = quality_analysis['content_metrics']['word_count']
        if word_count < 500:
            suggestions['content_optimization'].append({
                'type': 'length',
                'suggestion': 'Expand content to at least 500 words for better SEO performance',
                'priority': 'high'
            })
        
        # Entity enhancement suggestions
        entity_types = set(e['type'] for e in entities)
        if 'PERSON' not in entity_types:
            suggestions['entity_enhancement'].append({
                'type': 'entities',
                'suggestion': 'Consider mentioning relevant people or experts in the field',
                'priority': 'medium'
            })
        
        if 'ORGANIZATION' not in entity_types:
            suggestions['entity_enhancement'].append({
                'type': 'entities',
                'suggestion': 'Reference relevant organizations or companies',
                'priority': 'medium'
            })
        
        # Keyword optimization suggestions
        if target_keywords:
            content_lower = content.lower()
            for keyword in target_keywords:
                if keyword.lower() not in content_lower:
                    suggestions['keyword_optimization'].append({
                        'type': 'missing_keyword',
                        'suggestion': f'Consider including the keyword "{keyword}" naturally in the content',
                        'keyword': keyword,
                        'priority': 'high'
                    })
        
        # Structure improvements
        if not any(line.startswith('#') for line in content.split('\n')):
            suggestions['structure_improvements'].append({
                'type': 'headings',
                'suggestion': 'Add clear headings (H1, H2, H3) to improve content structure',
                'priority': 'high'
            })
        
        return {
            'overall_quality': quality_analysis['quality_level'],
            'quality_score': quality_analysis['quality_score'],
            'suggestions': suggestions,
            'total_suggestions': sum(len(cat) for cat in suggestions.values())
        }
    
    def health_check(self) -> bool:
        """Perform health check"""
        try:
            if not self.client:
                return False
            
            # Test with simple text analysis
            test_result = self.analyze_content("Test content for health check.", 
                                            analyze_entities=False, 
                                            analyze_sentiment=True, 
                                            analyze_syntax=False)
            return 'sentiment' in test_result
            
        except Exception as e:
            logger.error(f"Natural Language health check failed: {e}")
            return False
    
    def _process_entities(self, entities) -> List[Dict[str, Any]]:
        """Process entity analysis results"""
        processed_entities = []
        
        for entity in entities:
            processed_entity = {
                'name': entity.name,
                'type': entity.type_.name,
                'salience': entity.salience,
                'mentions': []
            }
            
            # Process mentions
            for mention in entity.mentions:
                processed_mention = {
                    'text': mention.text.content,
                    'type': mention.type_.name,
                    'begin_offset': mention.text.begin_offset
                }
                processed_entity['mentions'].append(processed_mention)
            
            # Add metadata if available
            if hasattr(entity, 'metadata') and entity.metadata:
                processed_entity['metadata'] = dict(entity.metadata)
            
            processed_entities.append(processed_entity)
        
        return processed_entities
    
    def _process_sentiment(self, sentiment_response) -> Dict[str, Any]:
        """Process sentiment analysis results"""
        return {
            'score': sentiment_response.document_sentiment.score,
            'magnitude': sentiment_response.document_sentiment.magnitude,
            'interpretation': self._interpret_sentiment(
                sentiment_response.document_sentiment.score,
                sentiment_response.document_sentiment.magnitude
            )
        }
    
    def _process_syntax(self, tokens) -> Dict[str, Any]:
        """Process syntax analysis results"""
        pos_counts = {}
        total_tokens = len(tokens)
        
        for token in tokens:
            pos = token.part_of_speech.tag.name
            pos_counts[pos] = pos_counts.get(pos, 0) + 1
        
        return {
            'total_tokens': total_tokens,
            'pos_distribution': pos_counts,
            'complexity_indicators': {
                'avg_token_length': sum(len(token.text.content) for token in tokens) / max(total_tokens, 1),
                'sentence_count': pos_counts.get('PUNCT', 0),  # Rough estimate
                'noun_ratio': pos_counts.get('NOUN', 0) / max(total_tokens, 1),
                'verb_ratio': pos_counts.get('VERB', 0) / max(total_tokens, 1)
            }
        }
    
    def _interpret_sentiment(self, score: float, magnitude: float) -> str:
        """Interpret sentiment score and magnitude"""
        if score >= 0.25:
            return 'positive'
        elif score <= -0.25:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_mock_content_analysis(self, content: str) -> Dict[str, Any]:
        """Return mock analysis when API is not available"""
        word_count = len(content.split())
        
        # Simple mock entity extraction
        import re
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        mock_entities = []
        for i, entity in enumerate(potential_entities[:5]):
            mock_entities.append({
                'name': entity,
                'type': 'UNKNOWN',
                'salience': 0.1 + (i * 0.05),
                'mentions': [{'text': entity, 'type': 'PROPER', 'begin_offset': content.find(entity)}],
                'metadata': {}
            })
        
        # Mock sentiment (neutral for most content)
        mock_sentiment = {
            'score': 0.1,
            'magnitude': 0.3,
            'interpretation': 'neutral'
        }
        
        return {
            'content_length': len(content),
            'word_count': word_count,
            'analysis_features': ['entities', 'sentiment'],
            'entities': mock_entities,
            'sentiment': mock_sentiment,
            'note': 'Mock data - Configure Google Natural Language API for real analysis'
        }
