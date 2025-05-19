# Filename: src/modules/keyword_processor_enhanced.py
import logging
import json
import re
import math
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field

logger = logging.getLogger("keyword_research.keyword_processor_enhanced")

class KeywordTrend(BaseModel):
    """Trend analysis for a keyword."""
    trend_direction: str = Field(..., description="Direction of the trend (increasing, decreasing, stable).")
    trend_strength: str = Field(..., description="Strength of the trend (strong, moderate, weak).")
    seasonality: Optional[str] = Field(None, description="Seasonality pattern if detected.")
    peak_months: List[str] = Field(default_factory=list, description="Months with peak interest.")
    trend_notes: Optional[str] = Field(None, description="Additional notes about the trend.")

class KeywordCompetitorMetrics(BaseModel):
    """Competitive metrics for a keyword."""
    top_competitors: List[str] = Field(default_factory=list, description="Top competitors ranking for this keyword.")
    avg_content_length: Optional[int] = Field(None, description="Average content length of top results.")
    avg_domain_authority: Optional[float] = Field(None, description="Average domain authority of top results.")
    serp_features_present: List[str] = Field(default_factory=list, description="SERP features present for this keyword.")
    ranking_difficulty_factors: List[str] = Field(default_factory=list, description="Factors contributing to ranking difficulty.")

class EnhancedKeywordMetrics(BaseModel):
    """Enhanced metrics for a keyword."""
    search_volume: Optional[int] = Field(None, description="Monthly search volume.")
    keyword_difficulty: Optional[float] = Field(None, description="Keyword difficulty score (0-100).")
    cpc: Optional[float] = Field(None, description="Cost per click (if available).")
    competition: Optional[float] = Field(None, description="Competition level (0-1).")
    trend_data: Optional[KeywordTrend] = Field(None, description="Trend analysis for the keyword.")
    clicks_data: Optional[Dict[str, Any]] = Field(None, description="Click data including CTR estimates.")
    intent_confidence: Optional[float] = Field(None, description="Confidence score for intent classification (0-1).")
    competitor_metrics: Optional[KeywordCompetitorMetrics] = Field(None, description="Competitive metrics for the keyword.")
    opportunity_score: Optional[float] = Field(None, description="Calculated opportunity score (0-100).")
    opportunity_factors: List[str] = Field(default_factory=list, description="Factors contributing to opportunity score.")

class KeywordClusterEnhanced(BaseModel):
    """Enhanced keyword cluster with additional metrics."""
    name: str = Field(..., description="Name of the cluster.")
    keywords: List[str] = Field(default_factory=list, description="Keywords in the cluster.")
    main_topic: str = Field(..., description="Main topic of the cluster.")
    subtopics: List[str] = Field(default_factory=list, description="Subtopics within the cluster.")
    total_search_volume: Optional[int] = Field(None, description="Combined search volume of all keywords.")
    average_difficulty: Optional[float] = Field(None, description="Average difficulty of keywords in cluster.")
    intent_distribution: Dict[str, float] = Field(default_factory=dict, description="Distribution of intents within cluster.")
    opportunity_score: Optional[float] = Field(None, description="Overall opportunity score for the cluster.")
    recommended_content_type: Optional[str] = Field(None, description="Recommended content type for this cluster.")

class KeywordProcessorEnhanced:
    """
    Enhanced keyword processor with advanced metrics and trend analysis.
    """
    
    def __init__(self):
        self.intent_classifiers = {
            "informational": self._is_informational,
            "navigational": self._is_navigational,
            "commercial": self._is_commercial,
            "transactional": self._is_transactional
        }
        
    def process_keywords(self, keywords, serp_data, competitor_data=None):
        """
        Process keywords with enhanced metrics and trend analysis.
        
        Args:
            keywords (list): List of keywords to process
            serp_data (dict): SERP data including search volume, difficulty, features
            competitor_data (dict, optional): Competitor content analysis data
            
        Returns:
            dict: Processed keyword data with enhanced metrics
        """
        logger.info(f"Processing {len(keywords)} keywords with enhanced metrics")
        
        result = {
            "intent_classification": {},
            "keyword_scores": {},
            "question_keywords": [],
            "clusters": [],
            "enhanced_metrics": {},
            "trend_analysis": {},
            "seasonal_keywords": [],
            "high_opportunity_keywords": []
        }
        
        # Extract search volume and keyword difficulty
        search_volume = serp_data.get("search_volume", {})
        keyword_difficulty = serp_data.get("keyword_difficulty", {})
        serp_features = serp_data.get("features", {})
        
        # Process each keyword
        for keyword in keywords:
            # Classify intent
            intent = self._classify_intent(keyword)
            result["intent_classification"][keyword] = intent
            
            # Check if it's a question
            if self._is_question(keyword):
                result["question_keywords"].append(keyword)
            
            # Calculate basic scores
            difficulty = keyword_difficulty.get(keyword, 50)  # Default to medium difficulty if unknown
            opportunity = self._calculate_opportunity(keyword, intent, search_volume.get(keyword, 0), difficulty)
            
            # Store basic scores
            result["keyword_scores"][keyword] = {
                "difficulty": difficulty,
                "opportunity": opportunity,
                "score": self._calculate_overall_score(opportunity, difficulty)
            }
            
            # Generate enhanced metrics
            result["enhanced_metrics"][keyword] = self._generate_enhanced_metrics(
                keyword, 
                intent, 
                search_volume.get(keyword, 0),
                difficulty,
                serp_features.get(keyword, []),
                competitor_data
            )
            
            # Generate trend analysis
            result["trend_analysis"][keyword] = self._generate_trend_analysis(keyword, search_volume.get(keyword, 0))
            
            # Check if seasonal
            trend_data = result["trend_analysis"].get(keyword, {})
            if trend_data and trend_data.get("seasonality") != "none":
                result["seasonal_keywords"].append(keyword)
            
            # Check if high opportunity
            if result["keyword_scores"][keyword]["score"] >= 70:
                result["high_opportunity_keywords"].append(keyword)
        
        # Generate enhanced clusters
        result["clusters"] = self._generate_enhanced_clusters(
            keywords, 
            result["intent_classification"],
            result["keyword_scores"],
            search_volume,
            keyword_difficulty
        )
        
        return result
    
    def _classify_intent(self, keyword):
        """Classify keyword intent."""
        # Check each intent type
        for intent, classifier in self.intent_classifiers.items():
            if classifier(keyword):
                return intent
        
        # Default to informational if no specific intent detected
        return "informational"
    
    def _is_informational(self, keyword):
        """Check if keyword has informational intent."""
        informational_patterns = [
            r'\b(what|who|where|when|why|how|guide|tutorial|learn|tips|ideas|examples)\b',
            r'\b(vs|versus|difference between|compare|comparison)\b',
            r'\b(meaning|definition|explain|understand)\b'
        ]
        
        return any(re.search(pattern, keyword.lower()) for pattern in informational_patterns)
    
    def _is_navigational(self, keyword):
        """Check if keyword has navigational intent."""
        navigational_patterns = [
            r'\b(login|signin|sign in|signup|sign up|account|download|website|official|homepage)\b',
            r'\b(app|application|software|tool|platform|portal|dashboard)\b'
        ]
        
        # Check for brand names (simplified approach)
        words = keyword.lower().split()
        if len(words) <= 2 and not any(re.search(r'\b(what|who|where|when|why|how)\b', keyword.lower())):
            return True
        
        return any(re.search(pattern, keyword.lower()) for pattern in navigational_patterns)
    
    def _is_commercial(self, keyword):
        """Check if keyword has commercial intent."""
        commercial_patterns = [
            r'\b(best|top|review|vs|versus|comparison|compare|alternative|recommended)\b',
            r'\b(cheap|cheapest|affordable|price|pricing|cost|free)\b'
        ]
        
        return any(re.search(pattern, keyword.lower()) for pattern in commercial_patterns)
    
    def _is_transactional(self, keyword):
        """Check if keyword has transactional intent."""
        transactional_patterns = [
            r'\b(buy|purchase|order|deal|discount|coupon|shop|sale|offer)\b',
            r'\b(subscription|trial|demo|download|get|acquire)\b'
        ]
        
        return any(re.search(pattern, keyword.lower()) for pattern in transactional_patterns)
    
    def _is_question(self, keyword):
        """Check if keyword is a question."""
        question_patterns = [
            r'^(what|who|where|when|why|how|is|are|can|do|does|will|should)',
            r'\?$'
        ]
        
        return any(re.search(pattern, keyword.lower()) for pattern in question_patterns)
    
    def _calculate_opportunity(self, keyword, intent, search_volume, difficulty):
        """Calculate opportunity score for a keyword."""
        # Base opportunity on search volume and difficulty
        if search_volume == 0:
            search_volume = 10  # Assign a minimal value to avoid zeros
            
        # Log scale for search volume to prevent very high volume keywords from dominating
        volume_score = min(100, 20 * math.log10(search_volume + 1))
        
        # Invert difficulty (higher difficulty = lower opportunity)
        difficulty_factor = max(0, 100 - difficulty) / 100
        
        # Intent modifier
        intent_modifier = {
            "informational": 0.8,
            "navigational": 0.6,
            "commercial": 1.0,
            "transactional": 1.2
        }.get(intent, 0.8)
        
        # Question bonus (questions often have less competition)
        question_bonus = 10 if self._is_question(keyword) else 0
        
        # Calculate final opportunity score
        opportunity = (volume_score * difficulty_factor * intent_modifier) + question_bonus
        
        # Ensure score is within 0-100 range
        return min(100, max(0, opportunity))
    
    def _calculate_overall_score(self, opportunity, difficulty):
        """Calculate overall score balancing opportunity and difficulty."""
        # Weight opportunity more than difficulty
        weighted_score = (opportunity * 0.7) + ((100 - difficulty) * 0.3)
        
        # Ensure score is within 0-100 range
        return min(100, max(0, weighted_score))
    
    def _generate_enhanced_metrics(self, keyword, intent, search_volume, difficulty, serp_features, competitor_data):
        """Generate enhanced metrics for a keyword."""
        # Initialize enhanced metrics
        metrics = {
            "search_volume": search_volume,
            "keyword_difficulty": difficulty,
            "cpc": self._estimate_cpc(keyword, intent),
            "competition": self._estimate_competition(difficulty),
            "clicks_data": self._estimate_clicks_data(keyword, search_volume, serp_features),
            "intent_confidence": self._calculate_intent_confidence(keyword, intent),
            "competitor_metrics": self._extract_competitor_metrics(keyword, competitor_data, serp_features),
            "opportunity_score": None,
            "opportunity_factors": []
        }
        
        # Calculate opportunity score and factors
        opportunity_score, opportunity_factors = self._calculate_enhanced_opportunity(
            keyword, 
            intent, 
            search_volume, 
            difficulty, 
            metrics["clicks_data"].get("organic_ctr", 0) if metrics["clicks_data"] else 0,
            serp_features
        )
        
        metrics["opportunity_score"] = opportunity_score
        metrics["opportunity_factors"] = opportunity_factors
        
        return metrics
    
    def _estimate_cpc(self, keyword, intent):
        """Estimate CPC based on keyword and intent."""
        # This is a simplified estimation - in a real implementation, you would use actual CPC data
        base_cpc = {
            "informational": 0.5,
            "navigational": 0.7,
            "commercial": 1.2,
            "transactional": 2.0
        }.get(intent, 0.5)
        
        # Adjust based on keyword characteristics
        if re.search(r'\b(buy|purchase|order|price|cost)\b', keyword.lower()):
            base_cpc *= 1.5
            
        if re.search(r'\b(cheap|free|discount|deal|coupon)\b', keyword.lower()):
            base_cpc *= 0.8
            
        if re.search(r'\b(best|top|review|premium|luxury)\b', keyword.lower()):
            base_cpc *= 1.3
            
        # Add some randomness to simulate real-world variation
        variation = np.random.uniform(0.8, 1.2)
        
        return round(base_cpc * variation, 2)
    
    def _estimate_competition(self, difficulty):
        """Estimate competition level based on difficulty."""
        # Simple linear transformation from difficulty (0-100) to competition (0-1)
        return round(difficulty / 100, 2)
    
    def _estimate_clicks_data(self, keyword, search_volume, serp_features):
        """Estimate click data including CTR based on SERP features."""
        if search_volume == 0:
            return {
                "total_clicks": 0,
                "organic_clicks": 0,
                "paid_clicks": 0,
                "no_click_percent": 0,
                "organic_ctr": 0,
                "paid_ctr": 0
            }
            
        # Base CTR estimates
        base_organic_ctr = 0.6  # 60% of searches result in organic clicks
        base_paid_ctr = 0.1     # 10% of searches result in paid clicks
        base_no_click = 0.3     # 30% of searches result in no clicks
        
        # Adjust based on SERP features
        if serp_features:
            # Features that typically reduce organic CTR
            ctr_reducing_features = [
                "featured_snippet", "knowledge_panel", "answer_box", "local_pack",
                "shopping_results", "top_stories", "recipes", "images_pack", "video_carousel"
            ]
            
            # Count how many CTR-reducing features are present
            reducing_feature_count = sum(1 for feature in serp_features if any(rf in feature.lower() for rf in ctr_reducing_features))
            
            # Reduce organic CTR based on feature count
            organic_ctr_reduction = min(0.4, reducing_feature_count * 0.1)  # Cap at 40% reduction
            base_organic_ctr -= organic_ctr_reduction
            
            # Increase no-click percentage
            base_no_click += organic_ctr_reduction * 0.8  # 80% of the reduction goes to no-clicks
            base_paid_ctr += organic_ctr_reduction * 0.2  # 20% of the reduction goes to paid clicks
        
        # Calculate actual click numbers
        total_clicks = search_volume * (1 - base_no_click)
        organic_clicks = search_volume * base_organic_ctr
        paid_clicks = search_volume * base_paid_ctr
        
        return {
            "total_clicks": round(total_clicks),
            "organic_clicks": round(organic_clicks),
            "paid_clicks": round(paid_clicks),
            "no_click_percent": round(base_no_click * 100, 1),
            "organic_ctr": round(base_organic_ctr * 100, 1),
            "paid_ctr": round(base_paid_ctr * 100, 1)
        }
    
    def _calculate_intent_confidence(self, keyword, intent):
        """Calculate confidence score for intent classification."""
        # Count how many patterns match for the assigned intent
        intent_classifier = self.intent_classifiers.get(intent)
        if not intent_classifier:
            return 0.5  # Default confidence
            
        # Check if the keyword matches the assigned intent
        if intent_classifier(keyword):
            # Check if it also matches other intents
            other_intents_match = sum(1 for i, c in self.intent_classifiers.items() 
                                     if i != intent and c(keyword))
            
            if other_intents_match == 0:
                return 0.9  # High confidence if no other intents match
            else:
                return 0.7  # Medium confidence if other intents also match
        else:
            return 0.5  # Low confidence if it doesn't match the assigned intent
    
    def _extract_competitor_metrics(self, keyword, competitor_data, serp_features):
        """Extract competitor metrics for a keyword."""
        if not competitor_data:
            return {
                "top_competitors": [],
                "avg_content_length": None,
                "avg_domain_authority": None,
                "serp_features_present": serp_features,
                "ranking_difficulty_factors": []
            }
            
        # Extract relevant competitor data
        top_competitors = []
        content_lengths = []
        domain_authorities = []
        
        # In a real implementation, you would extract this data from competitor_data
        # This is a simplified placeholder
        
        # Calculate averages
        avg_content_length = int(np.mean(content_lengths)) if content_lengths else None
        avg_domain_authority = round(np.mean(domain_authorities), 1) if domain_authorities else None
        
        # Determine ranking difficulty factors
        ranking_difficulty_factors = []
        
        if avg_content_length and avg_content_length > 2000:
            ranking_difficulty_factors.append("Long-form content dominates results")
            
        if avg_domain_authority and avg_domain_authority > 50:
            ranking_difficulty_factors.append("High domain authority competitors")
            
        if "featured_snippet" in serp_features:
            ranking_difficulty_factors.append("Featured snippet present")
            
        if not ranking_difficulty_factors:
            ranking_difficulty_factors.append("Standard competition level")
            
        return {
            "top_competitors": top_competitors,
            "avg_content_length": avg_content_length,
            "avg_domain_authority": avg_domain_authority,
            "serp_features_present": serp_features,
            "ranking_difficulty_factors": ranking_difficulty_factors
        }
    
    def _calculate_enhanced_opportunity(self, keyword, intent, search_volume, difficulty, organic_ctr, serp_features):
        """Calculate enhanced opportunity score with contributing factors."""
        opportunity_factors = []
        
        # Base opportunity calculation
        base_opportunity = self._calculate_opportunity(keyword, intent, search_volume, difficulty)
        
        # Adjust based on CTR
        ctr_modifier = 1.0
        if organic_ctr > 60:
            ctr_modifier = 1.2
            opportunity_factors.append("High organic CTR potential")
        elif organic_ctr < 40:
            ctr_modifier = 0.8
            opportunity_factors.append("Low organic CTR potential")
            
        # Adjust based on SERP features
        feature_modifier = 1.0
        positive_features = ["featured_snippet", "people_also_ask", "image_pack", "video_carousel"]
        negative_features = ["knowledge_panel", "local_pack", "top_stories"]
        
        positive_count = sum(1 for feature in serp_features if any(pf in feature.lower() for pf in positive_features))
        negative_count = sum(1 for feature in serp_features if any(nf in feature.lower() for nf in negative_features))
        
        if positive_count > negative_count:
            feature_modifier = 1.1
            opportunity_factors.append("Favorable SERP features present")
        elif negative_count > positive_count:
            feature_modifier = 0.9
            opportunity_factors.append("Challenging SERP features present")
            
        # Adjust based on intent
        if intent == "commercial" or intent == "transactional":
            opportunity_factors.append("High commercial/transactional value")
            
        if self._is_question(keyword):
            opportunity_factors.append("Question format with potential for featured snippet")
            
        # Calculate final opportunity score
        enhanced_opportunity = base_opportunity * ctr_modifier * feature_modifier
        
        # Ensure score is within 0-100 range
        return min(100, max(0, enhanced_opportunity)), opportunity_factors
    
    def _generate_trend_analysis(self, keyword, search_volume):
        """Generate trend analysis for a keyword."""
        # In a real implementation, this would use historical search volume data
        # This is a simplified placeholder that generates synthetic trend data
        
        # Determine if keyword might be seasonal
        seasonal_patterns = {
            r'\b(christmas|holiday|winter|snow|santa|gift)\b': {
                "seasonality": "annual",
                "peak_months": ["November", "December"],
                "trend_notes": "Strong holiday season trend peaking in November-December"
            },
            r'\b(summer|beach|swim|vacation|travel)\b': {
                "seasonality": "annual",
                "peak_months": ["June", "July", "August"],
                "trend_notes": "Summer seasonal trend peaking in June-August"
            },
            r'\b(tax|taxes|irs|return|filing)\b': {
                "seasonality": "annual",
                "peak_months": ["January", "February", "March", "April"],
                "trend_notes": "Tax season trend peaking in January-April"
            },
            r'\b(school|college|university|campus|student)\b': {
                "seasonality": "biannual",
                "peak_months": ["August", "September", "January"],
                "trend_notes": "Academic calendar trend with peaks at semester starts"
            },
            r'\b(garden|gardening|plant|lawn|flower)\b': {
                "seasonality": "annual",
                "peak_months": ["March", "April", "May"],
                "trend_notes": "Spring gardening season trend"
            }
        }
        
        # Check if keyword matches any seasonal pattern
        seasonality_data = None
        for pattern, data in seasonal_patterns.items():
            if re.search(pattern, keyword.lower()):
                seasonality_data = data
                break
                
        # Generate trend direction and strength
        # In a real implementation, this would be based on historical data
        trend_options = ["increasing", "decreasing", "stable"]
        strength_options = ["strong", "moderate", "weak"]
        
        # Use keyword characteristics to influence trend (simplified)
        if re.search(r'\b(new|latest|upcoming|trend|popular)\b', keyword.lower()):
            trend_direction = "increasing"
            trend_strength = np.random.choice(strength_options, p=[0.6, 0.3, 0.1])
        elif re.search(r'\b(old|outdated|obsolete|replaced)\b', keyword.lower()):
            trend_direction = "decreasing"
            trend_strength = np.random.choice(strength_options, p=[0.5, 0.3, 0.2])
        else:
            trend_direction = np.random.choice(trend_options, p=[0.3, 0.2, 0.5])
            trend_strength = np.random.choice(strength_options)
            
        # Combine all trend data
        trend_data = {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "seasonality": seasonality_data["seasonality"] if seasonality_data else "none",
            "peak_months": seasonality_data["peak_months"] if seasonality_data else [],
            "trend_notes": seasonality_data["trend_notes"] if seasonality_data else None
        }
        
        # Add current month context if seasonal
        if seasonality_data:
            current_month = datetime.now().strftime("%B")
            if current_month in seasonality_data["peak_months"]:
                trend_data["trend_notes"] = f"Currently in peak season ({current_month}). " + trend_data["trend_notes"]
            else:
                next_peak = min((seasonality_data["peak_months"].index(month) for month in seasonality_data["peak_months"] 
                               if self._month_is_after(month, current_month)), default=0)
                next_peak_month = seasonality_data["peak_months"][next_peak]
                trend_data["trend_notes"] = f"Next peak expected in {next_peak_month}. " + trend_data["trend_notes"]
                
        return trend_data
    
    def _month_is_after(self, month, reference_month):
        """Check if a month comes after a reference month."""
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        month_idx = months.index(month)
        ref_idx = months.index(reference_month)
        return month_idx > ref_idx
    
    def _generate_enhanced_clusters(self, keywords, intent_classification, keyword_scores, search_volume, keyword_difficulty):
        """Generate enhanced keyword clusters with additional metrics."""
        # In a real implementation, this would use sophisticated clustering algorithms
        # This is a simplified placeholder that groups keywords by common terms
        
        # Extract terms from keywords
        keyword_terms = {}
        for keyword in keywords:
            terms = set(re.findall(r'\b\w+\b', keyword.lower()))
            keyword_terms[keyword] = terms
            
        # Find common terms across keywords
        common_terms = {}
        for keyword, terms in keyword_terms.items():
            for term in terms:
                if len(term) > 3:  # Ignore short terms
                    if term not in common_terms:
                        common_terms[term] = []
                    common_terms[term].append(keyword)
                    
        # Filter to terms that appear in multiple keywords
        common_terms = {term: keywords for term, keywords in common_terms.items() if len(keywords) > 1}
        
        # Sort terms by number of keywords
        sorted_terms = sorted(common_terms.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Create clusters
        clusters = []
        used_keywords = set()
        
        for term, term_keywords in sorted_terms:
            # Skip if all keywords in this term are already used
            if all(kw in used_keywords for kw in term_keywords):
                continue
                
            # Create a new cluster
            cluster_keywords = [kw for kw in term_keywords if kw not in used_keywords]
            
            if not cluster_keywords:
                continue
                
            # Mark keywords as used
            used_keywords.update(cluster_keywords)
            
            # Calculate cluster metrics
            total_sv = sum(search_volume.get(kw, 0) for kw in cluster_keywords)
            avg_difficulty = np.mean([keyword_difficulty.get(kw, 50) for kw in cluster_keywords])
            
            # Calculate intent distribution
            intent_counts = {}
            for kw in cluster_keywords:
                intent = intent_classification.get(kw, "informational")
                if intent not in intent_counts:
                    intent_counts[intent] = 0
                intent_counts[intent] += 1
                
            total_intents = sum(intent_counts.values())
            intent_distribution = {intent: count / total_intents for intent, count in intent_counts.items()}
            
            # Calculate opportunity score
            opportunity_scores = [keyword_scores.get(kw, {}).get("score", 0) for kw in cluster_keywords]
            avg_opportunity = np.mean(opportunity_scores) if opportunity_scores else 0
            
            # Determine recommended content type based on intent distribution
            recommended_content_type = self._recommend_content_type(intent_distribution)
            
            # Create cluster
            cluster = {
                "name": f"{term.title()} Cluster",
                "keywords": cluster_keywords,
                "main_topic": term,
                "subtopics": self._extract_subtopics(cluster_keywords, term),
                "total_search_volume": total_sv,
                "average_difficulty": round(avg_difficulty, 1),
                "intent_distribution": {k: round(v * 100, 1) for k, v in intent_distribution.items()},
                "opportunity_score": round(avg_opportunity, 1),
                "recommended_content_type": recommended_content_type
            }
            
            clusters.append(cluster)
            
        # Add remaining keywords as a miscellaneous cluster
        remaining = [kw for kw in keywords if kw not in used_keywords]
        if remaining:
            # Calculate cluster metrics
            total_sv = sum(search_volume.get(kw, 0) for kw in remaining)
            avg_difficulty = np.mean([keyword_difficulty.get(kw, 50) for kw in remaining])
            
            # Calculate intent distribution
            intent_counts = {}
            for kw in remaining:
                intent = intent_classification.get(kw, "informational")
                if intent not in intent_counts:
                    intent_counts[intent] = 0
                intent_counts[intent] += 1
                
            total_intents = sum(intent_counts.values())
            intent_distribution = {intent: count / total_intents for intent, count in intent_counts.items()}
            
            # Calculate opportunity score
            opportunity_scores = [keyword_scores.get(kw, {}).get("score", 0) for kw in remaining]
            avg_opportunity = np.mean(opportunity_scores) if opportunity_scores else 0
            
            # Determine recommended content type based on intent distribution
            recommended_content_type = self._recommend_content_type(intent_distribution)
            
            # Create cluster
            cluster = {
                "name": "Miscellaneous Keywords",
                "keywords": remaining,
                "main_topic": "miscellaneous",
                "subtopics": [],
                "total_search_volume": total_sv,
                "average_difficulty": round(avg_difficulty, 1),
                "intent_distribution": {k: round(v * 100, 1) for k, v in intent_distribution.items()},
                "opportunity_score": round(avg_opportunity, 1),
                "recommended_content_type": recommended_content_type
            }
            
            clusters.append(cluster)
            
        return clusters
    
    def _extract_subtopics(self, keywords, main_topic):
        """Extract subtopics from a list of keywords."""
        subtopics = set()
        
        for keyword in keywords:
            # Split keyword into terms
            terms = set(re.findall(r'\b\w+\b', keyword.lower()))
            
            # Remove the main topic
            terms.discard(main_topic)
            
            # Add remaining terms as potential subtopics
            for term in terms:
                if len(term) > 3:  # Ignore short terms
                    subtopics.add(term)
                    
        # Return top subtopics (limit to 5)
        return list(subtopics)[:5]
    
    def _recommend_content_type(self, intent_distribution):
        """Recommend content type based on intent distribution."""
        # Find the dominant intent
        dominant_intent = max(intent_distribution.items(), key=lambda x: x[1])[0]
        
        # Recommend content type based on dominant intent
        content_type_map = {
            "informational": "Comprehensive Guide",
            "navigational": "Resource Directory",
            "commercial": "Product Comparison",
            "transactional": "Product/Service Page"
        }
        
        return content_type_map.get(dominant_intent, "Blog Post")
