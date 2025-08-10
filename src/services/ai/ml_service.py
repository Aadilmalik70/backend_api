"""
ML Service - Machine learning classification and analysis using scikit-learn

Provides ML-powered content analysis including:
- Content classification and categorization
- Feature extraction and selection
- Predictive analytics for content performance
- Automated content scoring
- Topic modeling and clustering

Designed for SEO content strategy optimization and competitor analysis.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import time
import re

class MLService:
    """
    scikit-learn based machine learning service for content analysis.
    
    Features:
    - Content classification and categorization
    - Topic modeling with LDA
    - Feature extraction and TF-IDF analysis
    - Content quality scoring
    - Performance prediction models
    - Memory-efficient processing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
        # Model components
        self.tfidf_vectorizer = None
        self.topic_model = None
        self.classifier = None
        self.scaler = None
        self.label_encoder = None
        
        # Configuration
        self.config = {
            'max_features': 5000,  # TF-IDF features
            'n_topics': 10,  # LDA topics
            'min_df': 2,  # Minimum document frequency
            'max_df': 0.8,  # Maximum document frequency
            'ngram_range': (1, 2),  # Unigrams and bigrams
            'random_state': 42,
            'batch_size': 100
        }
        
        # Pre-trained models cache
        self.models_cache = {}
        
        # Content categories for classification
        self.content_categories = [
            'informational', 'commercial', 'navigational', 'transactional',
            'blog_post', 'product_page', 'landing_page', 'news_article',
            'tutorial', 'review', 'comparison', 'faq'
        ]
    
    async def initialize(self):
        """Initialize ML models and components."""
        if self.initialized:
            return True
        
        try:
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=self.config['max_features'],
                min_df=self.config['min_df'],
                max_df=self.config['max_df'],
                ngram_range=self.config['ngram_range'],
                stop_words='english',
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Initialize topic model (LDA)
            self.topic_model = LatentDirichletAllocation(
                n_components=self.config['n_topics'],
                random_state=self.config['random_state'],
                max_iter=10,  # Reduced for faster initialization
                learning_method='online'
            )
            
            # Initialize classifier
            self.classifier = RandomForestClassifier(
                n_estimators=50,  # Reduced for memory efficiency
                random_state=self.config['random_state'],
                max_depth=10,
                min_samples_split=5,
                n_jobs=2  # Use 2 cores max
            )
            
            # Initialize preprocessing components
            self.scaler = StandardScaler()
            self.label_encoder = LabelEncoder()
            
            self.logger.info("✅ ML Service (scikit-learn) models initialized")
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"ML service initialization failed: {e}")
            return False
    
    async def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Classify content types and extract features from text batch.
        
        Args:
            texts: List of text content to classify
            
        Returns:
            List of classification results for each text
        """
        if not self.initialized:
            return []
        
        try:
            start_time = time.time()
            
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts if text and text.strip()]
            if not processed_texts:
                return []
            
            # Extract features using TF-IDF
            try:
                # Fit TF-IDF if not already fitted
                if not hasattr(self.tfidf_vectorizer, 'vocabulary_') or self.tfidf_vectorizer.vocabulary_ is None:
                    tfidf_features = self.tfidf_vectorizer.fit_transform(processed_texts)
                else:
                    tfidf_features = self.tfidf_vectorizer.transform(processed_texts)
                
                self.logger.debug(f"TF-IDF features shape: {tfidf_features.shape}")
                
            except Exception as e:
                self.logger.warning(f"TF-IDF extraction failed: {e}")
                return []
            
            results = []
            
            for i, text in enumerate(processed_texts):
                try:
                    # Extract various ML-based features
                    text_features = await self._extract_ml_features(text, tfidf_features[i] if i < tfidf_features.shape[0] else None)
                    
                    # Content classification
                    classification = self._classify_content_type(text, text_features)
                    
                    # Topic analysis
                    topics = await self._analyze_topics(text, tfidf_features[i] if i < tfidf_features.shape[0] else None)
                    
                    # Quality scoring
                    quality_score = self._calculate_content_quality_score(text, text_features)
                    
                    # Performance prediction
                    performance_prediction = self._predict_content_performance(text_features)
                    
                    result = {
                        'classification': classification,
                        'topics': topics,
                        'ml_features': text_features,
                        'quality_score': quality_score,
                        'performance_prediction': performance_prediction,
                        'processing_timestamp': time.time()
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Processing text {i} failed: {e}")
                    results.append(None)
            
            processing_time = time.time() - start_time
            self.logger.debug(f"ML classification completed in {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"ML batch classification failed: {e}")
            return []
    
    async def _extract_ml_features(self, text: str, tfidf_vector: Optional[Any] = None) -> Dict[str, Any]:
        """Extract comprehensive ML features from text."""
        try:
            features = {}
            
            # Basic text statistics
            features.update(self._extract_basic_features(text))
            
            # TF-IDF based features
            if tfidf_vector is not None:
                features.update(self._extract_tfidf_features(tfidf_vector))
            
            # Linguistic features
            features.update(self._extract_linguistic_features(text))
            
            # SEO-specific features
            features.update(self._extract_seo_features(text))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return {}
    
    def _extract_basic_features(self, text: str) -> Dict[str, float]:
        """Extract basic statistical features from text."""
        try:
            words = text.split()
            sentences = text.split('.')
            
            return {
                'char_count': len(text),
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
                'avg_sentence_length': len(words) / max(len(sentences), 1),
                'unique_word_ratio': len(set(words)) / max(len(words), 1),
                'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
                'digit_ratio': sum(1 for c in text if c.isdigit()) / max(len(text), 1),
                'punctuation_ratio': sum(1 for c in text if c in '.,!?;:') / max(len(text), 1)
            }
        except Exception:
            return {}
    
    def _extract_tfidf_features(self, tfidf_vector) -> Dict[str, float]:
        """Extract features from TF-IDF vector."""
        try:
            if hasattr(tfidf_vector, 'toarray'):
                vector_array = tfidf_vector.toarray().flatten()
            else:
                vector_array = np.array(tfidf_vector).flatten()
            
            return {
                'tfidf_sum': float(np.sum(vector_array)),
                'tfidf_mean': float(np.mean(vector_array)),
                'tfidf_std': float(np.std(vector_array)),
                'tfidf_max': float(np.max(vector_array)),
                'tfidf_non_zero_count': int(np.count_nonzero(vector_array)),
                'tfidf_sparsity': 1.0 - (np.count_nonzero(vector_array) / len(vector_array))
            }
        except Exception as e:
            self.logger.warning(f"TF-IDF feature extraction failed: {e}")
            return {}
    
    def _extract_linguistic_features(self, text: str) -> Dict[str, float]:
        """Extract linguistic complexity features."""
        try:
            # Simple linguistic analysis without external dependencies
            words = text.split()
            
            # Lexical diversity
            unique_words = set(word.lower() for word in words)
            lexical_diversity = len(unique_words) / max(len(words), 1)
            
            # Word length distribution
            word_lengths = [len(word) for word in words]
            avg_word_length = np.mean(word_lengths) if word_lengths else 0
            
            # Complex words (>2 syllables approximation)
            complex_words = sum(1 for word in words if len(word) > 6)
            complex_word_ratio = complex_words / max(len(words), 1)
            
            return {
                'lexical_diversity': lexical_diversity,
                'avg_word_length': avg_word_length,
                'complex_word_ratio': complex_word_ratio,
                'vocabulary_richness': len(unique_words) / max(len(words), 1)
            }
        except Exception:
            return {}
    
    def _extract_seo_features(self, text: str) -> Dict[str, float]:
        """Extract SEO-relevant features."""
        try:
            text_lower = text.lower()
            
            # Keyword density patterns
            question_words = ['what', 'how', 'why', 'when', 'where', 'who']
            question_count = sum(text_lower.count(word) for word in question_words)
            
            # Action words
            action_words = ['buy', 'get', 'download', 'learn', 'discover', 'find']
            action_count = sum(text_lower.count(word) for word in action_words)
            
            # Commercial intent indicators
            commercial_words = ['price', 'cost', 'buy', 'purchase', 'deal', 'discount']
            commercial_count = sum(text_lower.count(word) for word in commercial_words)
            
            # Content structure indicators
            has_numbers = bool(re.search(r'\d+', text))
            has_lists = bool(re.search(r'(\n\s*[\-\*\+]|\d+\.)', text))
            
            return {
                'question_density': question_count / max(len(text.split()), 1),
                'action_word_density': action_count / max(len(text.split()), 1),
                'commercial_intent_score': commercial_count / max(len(text.split()), 1),
                'has_numbers': 1.0 if has_numbers else 0.0,
                'has_structured_content': 1.0 if has_lists else 0.0,
                'title_case_ratio': sum(1 for word in text.split() if word.istitle()) / max(len(text.split()), 1)
            }
        except Exception:
            return {}
    
    def _classify_content_type(self, text: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Classify content type based on features."""
        try:
            # Rule-based classification (simplified)
            text_lower = text.lower()
            
            # Initialize scores for different content types
            type_scores = {content_type: 0.0 for content_type in self.content_categories}
            
            # Informational content indicators
            if any(word in text_lower for word in ['what is', 'how to', 'guide', 'tutorial']):
                type_scores['informational'] += 0.3
                type_scores['tutorial'] += 0.2
            
            # Commercial content indicators
            if any(word in text_lower for word in ['buy', 'price', 'purchase', 'deal']):
                type_scores['commercial'] += 0.3
                type_scores['product_page'] += 0.2
            
            # Review indicators
            if any(word in text_lower for word in ['review', 'rating', 'pros', 'cons']):
                type_scores['review'] += 0.4
            
            # Comparison indicators
            if any(word in text_lower for word in ['vs', 'versus', 'compare', 'comparison']):
                type_scores['comparison'] += 0.4
            
            # Blog post indicators
            if features.get('avg_sentence_length', 0) > 15 and len(text) > 500:
                type_scores['blog_post'] += 0.2
            
            # FAQ indicators
            if features.get('question_density', 0) > 0.1:
                type_scores['faq'] += 0.3
            
            # Find the most likely content type
            predicted_type = max(type_scores.items(), key=lambda x: x[1])
            
            return {
                'predicted_type': predicted_type[0],
                'confidence': predicted_type[1],
                'type_scores': type_scores,
                'classification_method': 'rule_based'
            }
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            return {}
    
    async def _analyze_topics(self, text: str, tfidf_vector: Optional[Any] = None) -> Dict[str, Any]:
        """Analyze topics in the text using LDA."""
        try:
            if tfidf_vector is None:
                return {}
            
            # For single text, we can't perform LDA effectively
            # Instead, we'll return top TF-IDF terms as "topics"
            if hasattr(tfidf_vector, 'toarray'):
                vector_array = tfidf_vector.toarray().flatten()
            else:
                vector_array = np.array(tfidf_vector).flatten()
            
            # Get feature names from vectorizer
            if hasattr(self.tfidf_vectorizer, 'get_feature_names_out'):
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
            else:
                feature_names = getattr(self.tfidf_vectorizer, 'feature_names_', [])
            
            if len(feature_names) == 0 or len(vector_array) != len(feature_names):
                return {}
            
            # Get top terms
            top_indices = np.argsort(vector_array)[-10:][::-1]
            top_terms = []
            
            for idx in top_indices:
                if idx < len(feature_names) and vector_array[idx] > 0:
                    top_terms.append({
                        'term': feature_names[idx],
                        'score': float(vector_array[idx])
                    })
            
            return {
                'top_terms': top_terms,
                'topic_coherence_score': float(np.mean([term['score'] for term in top_terms])) if top_terms else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Topic analysis failed: {e}")
            return {}
    
    def _calculate_content_quality_score(self, text: str, features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate content quality score based on ML features."""
        try:
            quality_factors = {}
            
            # Length quality (optimal range)
            word_count = features.get('word_count', 0)
            if 300 <= word_count <= 2000:
                quality_factors['length_quality'] = 1.0
            elif word_count < 300:
                quality_factors['length_quality'] = word_count / 300
            else:
                quality_factors['length_quality'] = max(0.5, 1.0 - (word_count - 2000) / 5000)
            
            # Readability quality
            avg_sentence_length = features.get('avg_sentence_length', 0)
            readability_score = max(0, 1.0 - abs(avg_sentence_length - 20) / 20)
            quality_factors['readability_quality'] = readability_score
            
            # Vocabulary richness
            vocab_richness = features.get('vocabulary_richness', 0)
            quality_factors['vocabulary_quality'] = min(vocab_richness * 2, 1.0)
            
            # Structure quality
            structure_score = 0
            if features.get('has_structured_content', 0) > 0:
                structure_score += 0.5
            if features.get('has_numbers', 0) > 0:
                structure_score += 0.3
            quality_factors['structure_quality'] = min(structure_score, 1.0)
            
            # SEO optimization
            seo_score = 0
            if features.get('question_density', 0) > 0.02:
                seo_score += 0.3
            if features.get('title_case_ratio', 0) > 0.1:
                seo_score += 0.2
            quality_factors['seo_quality'] = min(seo_score, 1.0)
            
            # Overall quality score (weighted average)
            weights = {
                'length_quality': 0.25,
                'readability_quality': 0.25,
                'vocabulary_quality': 0.2,
                'structure_quality': 0.15,
                'seo_quality': 0.15
            }
            
            overall_score = sum(
                quality_factors.get(factor, 0) * weight 
                for factor, weight in weights.items()
            )
            
            return {
                'overall_score': round(overall_score * 100, 2),
                'quality_factors': quality_factors,
                'quality_grade': self._get_quality_grade(overall_score * 100)
            }
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return {}
    
    def _predict_content_performance(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict content performance based on features."""
        try:
            # Simple performance prediction model
            performance_factors = {}
            
            # Engagement prediction
            engagement_score = 0
            if features.get('question_density', 0) > 0.05:
                engagement_score += 0.3
            if features.get('action_word_density', 0) > 0.02:
                engagement_score += 0.2
            if features.get('complex_word_ratio', 0) < 0.2:
                engagement_score += 0.2
            
            performance_factors['engagement_prediction'] = min(engagement_score, 1.0)
            
            # SEO performance prediction
            seo_performance = 0
            word_count = features.get('word_count', 0)
            if 500 <= word_count <= 1500:
                seo_performance += 0.4
            if features.get('has_structured_content', 0):
                seo_performance += 0.3
            if features.get('lexical_diversity', 0) > 0.5:
                seo_performance += 0.3
            
            performance_factors['seo_performance'] = min(seo_performance, 1.0)
            
            # Social sharing prediction
            sharing_score = 0
            if features.get('question_density', 0) > 0.03:
                sharing_score += 0.4
            if features.get('has_numbers', 0):
                sharing_score += 0.3
            if 800 <= word_count <= 1200:
                sharing_score += 0.3
            
            performance_factors['sharing_potential'] = min(sharing_score, 1.0)
            
            # Overall performance prediction
            overall_performance = np.mean(list(performance_factors.values()))
            
            return {
                'overall_performance_score': round(overall_performance * 100, 2),
                'performance_factors': performance_factors,
                'performance_tier': self._get_performance_tier(overall_performance * 100),
                'recommendations': self._generate_performance_recommendations(features)
            }
            
        except Exception as e:
            self.logger.error(f"Performance prediction failed: {e}")
            return {}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for ML analysis."""
        try:
            # Basic text cleaning
            text = re.sub(r'https?://\S+', '', text)  # Remove URLs
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            return text
        except Exception:
            return text
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_performance_tier(self, score: float) -> str:
        """Convert performance score to tier."""
        if score >= 80:
            return "High Performance"
        elif score >= 60:
            return "Good Performance"
        elif score >= 40:
            return "Average Performance"
        else:
            return "Needs Improvement"
    
    def _generate_performance_recommendations(self, features: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations."""
        try:
            recommendations = []
            
            # Word count recommendations
            word_count = features.get('word_count', 0)
            if word_count < 300:
                recommendations.append("Increase content length to at least 300 words for better SEO")
            elif word_count > 2000:
                recommendations.append("Consider breaking long content into multiple sections or pages")
            
            # Structure recommendations
            if not features.get('has_structured_content', False):
                recommendations.append("Add bullet points or numbered lists to improve readability")
            
            # Engagement recommendations
            if features.get('question_density', 0) < 0.02:
                recommendations.append("Include more questions to increase user engagement")
            
            # Vocabulary recommendations
            if features.get('vocabulary_richness', 0) < 0.4:
                recommendations.append("Diversify vocabulary to make content more interesting")
            
            # SEO recommendations
            if features.get('action_word_density', 0) < 0.01:
                recommendations.append("Add more action-oriented language to encourage user interaction")
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return []
    
    async def train_custom_classifier(self, texts: List[str], labels: List[str]) -> Dict[str, Any]:
        """
        Train a custom classifier on provided data.
        
        Args:
            texts: Training texts
            labels: Corresponding labels
            
        Returns:
            Training results and model performance
        """
        if not self.initialized or len(texts) != len(labels):
            return {}
        
        try:
            self.logger.info(f"Training custom classifier on {len(texts)} samples")
            
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Extract features
            X = self.tfidf_vectorizer.fit_transform(processed_texts)
            
            # Encode labels
            y = self.label_encoder.fit_transform(labels)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=self.config['random_state']
            )
            
            # Train classifier
            self.classifier.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Get feature importance
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            feature_importance = self.classifier.feature_importances_
            top_features = sorted(
                zip(feature_names, feature_importance),
                key=lambda x: x[1],
                reverse=True
            )[:20]
            
            self.logger.info(f"Custom classifier trained with {accuracy:.3f} accuracy")
            
            return {
                'accuracy': float(accuracy),
                'n_samples': len(texts),
                'n_features': X.shape[1],
                'classes': self.label_encoder.classes_.tolist(),
                'top_features': [(str(name), float(importance)) for name, importance in top_features],
                'training_timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Custom classifier training failed: {e}")
            return {}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models and configuration."""
        return {
            'initialized': self.initialized,
            'tfidf_features': self.config['max_features'],
            'n_topics': self.config['n_topics'],
            'content_categories': self.content_categories,
            'models_loaded': {
                'tfidf_vectorizer': self.tfidf_vectorizer is not None,
                'topic_model': self.topic_model is not None,
                'classifier': self.classifier is not None
            },
            'config': self.config
        }