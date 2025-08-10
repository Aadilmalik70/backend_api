"""
NLP Service - Advanced natural language processing using spaCy

Provides comprehensive text analysis including:
- Named Entity Recognition (NER)
- Part-of-speech tagging
- Dependency parsing
- Text preprocessing and cleaning
- Linguistic feature extraction

Optimized for SERP content analysis and SEO optimization.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import hashlib
from concurrent.futures import ThreadPoolExecutor
import time

class NLPService:
    """
    spaCy-based NLP service with memory-efficient processing.
    
    Features:
    - Lazy model loading
    - Batch processing for efficiency  
    - Memory zone management for large documents
    - Comprehensive linguistic analysis
    - SEO-specific feature extraction
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nlp = None
        self.model_name = "en_core_web_sm"
        self.initialized = False
        
        # Performance configuration
        self.config = {
            'batch_size': 32,
            'max_doc_length': 1000000,  # 1M chars
            'disable_components': [],  # Keep all components by default
            'enable_memory_zone': True
        }
        
        # Feature extractors
        self.feature_extractors = {
            'entities': self._extract_entities,
            'keywords': self._extract_keywords, 
            'readability': self._calculate_readability,
            'structure': self._analyze_structure,
            'seo_elements': self._extract_seo_elements
        }
    
    async def initialize(self):
        """Initialize spaCy model with error handling and fallbacks."""
        if self.initialized:
            return True
        
        try:
            import spacy
            from spacy.lang.en import English
            
            self.logger.info("Loading spaCy model...")
            
            # Try to load the preferred model
            try:
                self.nlp = spacy.load(self.model_name)
                self.logger.info(f"✅ Loaded spaCy model: {self.model_name}")
            except OSError:
                self.logger.warning(f"Model {self.model_name} not found, using blank English model")
                self.nlp = English()
            
            # Configure pipeline components
            if self.config['disable_components']:
                self.nlp.disable_pipes(self.config['disable_components'])
                self.logger.info(f"Disabled components: {self.config['disable_components']}")
            
            # Set maximum document length
            self.nlp.max_length = self.config['max_doc_length']
            
            self.initialized = True
            return True
            
        except ImportError as e:
            self.logger.error(f"spaCy not available: {e}")
            self.logger.info("Install with: pip install spacy && python -m spacy download en_core_web_sm")
            return False
        except Exception as e:
            self.logger.error(f"spaCy initialization failed: {e}")
            return False
    
    async def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple texts efficiently using spaCy's batch processing.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of analysis results for each text
        """
        if not self.initialized or not self.nlp:
            self.logger.warning("NLP service not initialized")
            return []
        
        try:
            start_time = time.time()
            
            # Filter and preprocess texts
            valid_texts = []
            text_indices = []
            
            for i, text in enumerate(texts):
                if isinstance(text, str) and text.strip():
                    # Truncate overly long texts
                    if len(text) > self.config['max_doc_length']:
                        text = text[:self.config['max_doc_length']]
                    valid_texts.append(text)
                    text_indices.append(i)
            
            if not valid_texts:
                return []
            
            # Process texts in batches
            results = []
            batch_size = self.config['batch_size']
            
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                batch_results = await self._process_batch_internal(batch)
                results.extend(batch_results)
            
            # Create full results list with None for invalid texts
            full_results = [None] * len(texts)
            for result, original_index in zip(results, text_indices):
                full_results[original_index] = result
            
            processing_time = time.time() - start_time
            self.logger.debug(f"Processed {len(texts)} texts in {processing_time:.2f}s")
            
            return full_results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return []
    
    async def _process_batch_internal(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Internal batch processing with memory zone management."""
        try:
            if self.config['enable_memory_zone'] and hasattr(self.nlp, 'memory_zone'):
                # Use memory zone for efficient processing
                with self.nlp.memory_zone():
                    docs = list(self.nlp.pipe(texts))
                    return await self._extract_features_from_docs(docs)
            else:
                # Standard processing
                docs = list(self.nlp.pipe(texts))
                return await self._extract_features_from_docs(docs)
                
        except Exception as e:
            self.logger.error(f"Internal batch processing failed: {e}")
            return []
    
    async def _extract_features_from_docs(self, docs) -> List[Dict[str, Any]]:
        """Extract comprehensive features from processed documents."""
        try:
            results = []
            
            for doc in docs:
                # Extract all features
                features = {}
                
                for feature_name, extractor in self.feature_extractors.items():
                    try:
                        features[feature_name] = extractor(doc)
                    except Exception as e:
                        self.logger.warning(f"Feature extraction '{feature_name}' failed: {e}")
                        features[feature_name] = None
                
                # Add basic statistics
                features['stats'] = {
                    'token_count': len(doc),
                    'sentence_count': len(list(doc.sents)),
                    'char_count': len(doc.text),
                    'word_count': len([token for token in doc if not token.is_space])
                }
                
                results.append(features)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return []
    
    def _extract_entities(self, doc) -> List[Dict[str, Any]]:
        """Extract named entities with confidence scores."""
        try:
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': ent.label_,
                    'start_char': ent.start_char,
                    'end_char': ent.end_char,
                    'confidence': getattr(ent, 'ent_score_', 1.0) if hasattr(ent, 'ent_score_') else 1.0
                })
            return entities
        except Exception as e:
            self.logger.warning(f"Entity extraction failed: {e}")
            return []
    
    def _extract_keywords(self, doc) -> List[Dict[str, Any]]:
        """Extract potential keywords based on POS tags and frequency."""
        try:
            # Focus on nouns, adjectives, and proper nouns
            keyword_pos = ['NOUN', 'ADJ', 'PROPN']
            
            # Count word frequencies
            word_freq = {}
            keywords = []
            
            for token in doc:
                if (token.pos_ in keyword_pos and 
                    not token.is_stop and 
                    not token.is_punct and 
                    len(token.text) > 2):
                    
                    lemma = token.lemma_.lower()
                    word_freq[lemma] = word_freq.get(lemma, 0) + 1
            
            # Convert to keyword list with scores
            for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
                keywords.append({
                    'keyword': word,
                    'frequency': freq,
                    'relevance_score': min(freq / len(doc) * 100, 100)
                })
            
            return keywords[:20]  # Top 20 keywords
            
        except Exception as e:
            self.logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    def _calculate_readability(self, doc) -> Dict[str, float]:
        """Calculate readability metrics."""
        try:
            sentences = list(doc.sents)
            words = [token for token in doc if not token.is_space and not token.is_punct]
            
            if not sentences or not words:
                return {}
            
            avg_words_per_sentence = len(words) / len(sentences)
            avg_chars_per_word = sum(len(token.text) for token in words) / len(words)
            
            # Simple readability approximation
            readability_score = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * (avg_chars_per_word / 100)
            
            return {
                'avg_words_per_sentence': round(avg_words_per_sentence, 2),
                'avg_chars_per_word': round(avg_chars_per_word, 2),
                'readability_score': round(readability_score, 2),
                'readability_level': self._get_readability_level(readability_score)
            }
            
        except Exception as e:
            self.logger.warning(f"Readability calculation failed: {e}")
            return {}
    
    def _get_readability_level(self, score: float) -> str:
        """Convert readability score to level description."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _analyze_structure(self, doc) -> Dict[str, Any]:
        """Analyze document structure and linguistic patterns."""
        try:
            sentences = list(doc.sents)
            
            # POS tag distribution
            pos_counts = {}
            dep_counts = {}
            
            for token in doc:
                if not token.is_space:
                    pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1
                    dep_counts[token.dep_] = dep_counts.get(token.dep_, 0) + 1
            
            # Sentence lengths
            sentence_lengths = [len([t for t in sent if not t.is_space]) for sent in sentences]
            
            return {
                'sentence_length_distribution': {
                    'min': min(sentence_lengths) if sentence_lengths else 0,
                    'max': max(sentence_lengths) if sentence_lengths else 0,
                    'avg': round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0
                },
                'pos_distribution': pos_counts,
                'dependency_distribution': dict(sorted(dep_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                'linguistic_complexity': self._calculate_complexity_score(pos_counts, sentence_lengths)
            }
            
        except Exception as e:
            self.logger.warning(f"Structure analysis failed: {e}")
            return {}
    
    def _calculate_complexity_score(self, pos_counts: Dict[str, int], sentence_lengths: List[int]) -> float:
        """Calculate linguistic complexity score."""
        try:
            if not pos_counts or not sentence_lengths:
                return 0.0
            
            # Factors that increase complexity
            total_tokens = sum(pos_counts.values())
            complex_pos_ratio = (
                pos_counts.get('ADJ', 0) + 
                pos_counts.get('ADV', 0) + 
                pos_counts.get('SCONJ', 0)
            ) / total_tokens if total_tokens > 0 else 0
            
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
            sentence_variance = sum((x - avg_sentence_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
            
            # Normalize to 0-100 scale
            complexity = (
                complex_pos_ratio * 30 +
                min(avg_sentence_length / 20, 1) * 40 +
                min(sentence_variance / 100, 1) * 30
            )
            
            return round(complexity, 2)
            
        except Exception:
            return 0.0
    
    def _extract_seo_elements(self, doc) -> Dict[str, Any]:
        """Extract SEO-relevant elements from the text."""
        try:
            # Find potential headings (sentences that start with capital words)
            potential_headings = []
            questions = []
            call_to_actions = []
            
            # CTA indicators
            cta_words = ['click', 'buy', 'order', 'subscribe', 'download', 'register', 'join', 'contact']
            
            for sent in doc.sents:
                sent_text = sent.text.strip()
                
                # Potential headings (short sentences, mostly nouns/adjectives)
                if len(sent_text) < 100 and len([t for t in sent if t.pos_ in ['NOUN', 'ADJ', 'PROPN']]) > len(sent) * 0.4:
                    potential_headings.append(sent_text)
                
                # Questions
                if sent_text.endswith('?'):
                    questions.append(sent_text)
                
                # Call to actions
                if any(cta_word in sent_text.lower() for cta_word in cta_words):
                    call_to_actions.append(sent_text)
            
            return {
                'potential_headings': potential_headings[:10],
                'questions': questions[:5],
                'call_to_actions': call_to_actions[:5],
                'seo_keywords': [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART']][:10]
            }
            
        except Exception as e:
            self.logger.warning(f"SEO element extraction failed: {e}")
            return {}
    
    async def analyze_content_quality(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive content quality analysis.
        
        Args:
            text: Content to analyze
            
        Returns:
            Content quality metrics and recommendations
        """
        if not self.initialized:
            return {}
        
        try:
            results = await self.process_batch([text])
            if not results or not results[0]:
                return {}
            
            analysis = results[0]
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(analysis)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis)
            
            return {
                'quality_score': quality_score,
                'analysis': analysis,
                'recommendations': recommendations,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Content quality analysis failed: {e}")
            return {}
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall content quality score (0-100)."""
        try:
            score = 0.0
            max_score = 100.0
            
            # Readability (25 points)
            if analysis.get('readability'):
                readability_score = analysis['readability'].get('readability_score', 0)
                score += min(readability_score / 4, 25)
            
            # Entity richness (20 points)
            entities = analysis.get('entities', [])
            entity_score = min(len(entities) * 2, 20)
            score += entity_score
            
            # Keyword diversity (20 points)
            keywords = analysis.get('keywords', [])
            keyword_score = min(len(keywords), 20)
            score += keyword_score
            
            # Structure quality (20 points)
            structure = analysis.get('structure', {})
            if structure:
                complexity = structure.get('linguistic_complexity', 0)
                structure_score = min(complexity, 20)
                score += structure_score
            
            # SEO elements (15 points)
            seo_elements = analysis.get('seo_elements', {})
            seo_score = 0
            if seo_elements.get('potential_headings'):
                seo_score += 5
            if seo_elements.get('questions'):
                seo_score += 5
            if seo_elements.get('seo_keywords'):
                seo_score += 5
            score += seo_score
            
            return round(min(score, max_score), 2)
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return 0.0
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate content improvement recommendations."""
        try:
            recommendations = []
            
            # Check readability
            readability = analysis.get('readability', {})
            if readability:
                score = readability.get('readability_score', 0)
                if score < 30:
                    recommendations.append("Consider simplifying sentence structure for better readability")
                elif score > 90:
                    recommendations.append("Content may be too simple for the target audience")
            
            # Check entity diversity
            entities = analysis.get('entities', [])
            if len(entities) < 3:
                recommendations.append("Add more specific entities (people, places, organizations) to improve content richness")
            
            # Check structure
            stats = analysis.get('stats', {})
            if stats.get('sentence_count', 0) < 3:
                recommendations.append("Consider expanding content with more detailed explanations")
            
            # Check SEO elements
            seo_elements = analysis.get('seo_elements', {})
            if not seo_elements.get('questions'):
                recommendations.append("Consider adding questions to improve engagement")
            if not seo_elements.get('potential_headings'):
                recommendations.append("Add clear headings to improve content structure")
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return []