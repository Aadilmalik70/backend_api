import os
import json
import random
from datetime import datetime

class ContentPerformancePredictor:
    """
    Class for predicting content performance in search results based on
    keyword data, SERP analysis, competitor analysis, and content blueprint.
    """
    
    def __init__(self):
        """Initialize the ContentPerformancePredictor with default settings."""
        self.ranking_factors = [
            "Content Comprehensiveness",
            "Keyword Optimization",
            "Content Structure",
            "Readability",
            "SERP Feature Optimization",
            "Semantic Relevance",
            "Entity Coverage",
            "User Intent Match",
            "Content Freshness",
            "Mobile Optimization"
        ]
        
        self.improvement_areas = [
            "Multimedia Enhancement",
            "Schema Markup",
            "Internal Linking",
            "Mobile Optimization",
            "User Experience",
            "Content Freshness",
            "Semantic Depth",
            "Entity Relationships",
            "Topical Authority",
            "E-A-T Signals"
        ]
    
    def predict_performance(self, input_text, keyword_data, serp_data, competitor_data, content_blueprint):
        """
        Predict content performance based on various inputs.
        
        Args:
            input_text (str): The original user input text
            keyword_data (dict): Keyword analysis data
            serp_data (dict): SERP analysis data
            competitor_data (dict): Competitor analysis data
            content_blueprint (dict): Content blueprint data
            
        Returns:
            dict: Performance prediction data
        """
        # In a real implementation, this would use ML models to predict performance
        # For now, we'll generate realistic mock data
        
        # Calculate estimated SERP position based on content quality and competition
        content_quality = self._evaluate_content_quality(content_blueprint)
        competition_strength = self._evaluate_competition(competitor_data)
        keyword_difficulty = self._get_average_keyword_difficulty(keyword_data)
        
        # Calculate estimated position (lower is better)
        estimated_position = self._calculate_position(content_quality, competition_strength, keyword_difficulty)
        
        # Calculate probability of ranking in top 10
        ranking_probability = max(0, min(1, 1.2 - (estimated_position / 15)))
        
        # Calculate estimated traffic based on position and search volume
        search_volume = self._get_total_search_volume(keyword_data)
        estimated_ctr = self._get_ctr_for_position(estimated_position)
        estimated_traffic = int(search_volume * estimated_ctr / 100)
        
        # Generate ranking factors with scores
        ranking_factors = self._generate_ranking_factors(content_blueprint, keyword_data, serp_data)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(ranking_factors)
        
        # Calculate overall confidence score
        confidence_score = int(sum(factor["score"] for factor in ranking_factors) / len(ranking_factors) * 100)
        
        return {
            "estimated_serp_position": round(estimated_position, 1),
            "ranking_probability": round(ranking_probability, 2),
            "estimated_traffic": estimated_traffic,
            "estimated_ctr": round(estimated_ctr, 1),
            "confidence_score": confidence_score,
            "ranking_factors": ranking_factors,
            "improvement_suggestions": improvement_suggestions
        }
    
    def _evaluate_content_quality(self, content_blueprint):
        """Evaluate the quality of the content blueprint."""
        # Count sections and subsections as a proxy for comprehensiveness
        section_count = len(content_blueprint.get("sections", []))
        subsection_count = sum(len(section.get("subsections", [])) for section in content_blueprint.get("sections", []))
        
        # More sections and subsections generally indicate more comprehensive content
        # Scale from 0.5 to 1.0
        return min(1.0, max(0.5, (section_count * 0.1 + subsection_count * 0.05)))
    
    def _evaluate_competition(self, competitor_data):
        """Evaluate the strength of competition."""
        # In a real implementation, this would analyze competitor metrics
        # For now, return a random value between 0.6 and 0.9
        return random.uniform(0.6, 0.9)
    
    def _get_average_keyword_difficulty(self, keyword_data):
        """Calculate average keyword difficulty."""
        difficulties = [data["difficulty"] for _, data in keyword_data.get("keyword_scores", {}).items()]
        return sum(difficulties) / len(difficulties) if difficulties else 50
    
    def _calculate_position(self, content_quality, competition_strength, keyword_difficulty):
        """Calculate estimated SERP position."""
        # Lower is better
        base_position = 10 * (1 - content_quality)
        competition_factor = competition_strength * 5
        difficulty_factor = keyword_difficulty / 20
        
        return base_position + competition_factor + difficulty_factor
    
    def _get_total_search_volume(self, keyword_data):
        """Calculate total search volume for all keywords."""
        total_volume = sum(
            data.get("search_volume", 0) 
            for _, data in keyword_data.get("enhanced_metrics", {}).items()
        )
        return total_volume if total_volume > 0 else 3000  # Default if no data
    
    def _get_ctr_for_position(self, position):
        """Get estimated CTR for a given position."""
        # Approximate CTR values by position
        ctr_values = {
            1: 31.7,
            2: 24.7,
            3: 18.7,
            4: 13.6,
            5: 9.5,
            6: 6.1,
            7: 4.2,
            8: 3.1,
            9: 2.6,
            10: 2.4
        }
        
        # For positions outside top 10, use very low CTR
        if position > 10:
            return 0.5
        
        # For positions between integers, interpolate
        position_floor = int(position)
        position_ceil = position_floor + 1
        
        if position_ceil > 10:
            return ctr_values[position_floor]
        
        floor_ctr = ctr_values[position_floor]
        ceil_ctr = ctr_values[position_ceil]
        
        # Linear interpolation
        fraction = position - position_floor
        return floor_ctr - fraction * (floor_ctr - ceil_ctr)
    
    def _generate_ranking_factors(self, content_blueprint, keyword_data, serp_data):
        """Generate ranking factors with scores."""
        factors = []
        
        # Select 5-7 factors
        selected_factors = random.sample(self.ranking_factors, random.randint(5, 7))
        
        for factor in selected_factors:
            # Generate a realistic score between 0.65 and 0.95
            score = random.uniform(0.65, 0.95)
            
            # Generate description and details based on factor
            description, details = self._get_factor_description(factor)
            
            factors.append({
                "factor_name": factor,
                "score": round(score, 2),
                "description": description,
                "details": details
            })
        
        return factors
    
    def _get_factor_description(self, factor):
        """Get description and details for a ranking factor."""
        descriptions = {
            "Content Comprehensiveness": (
                "Your content covers the topic thoroughly with appropriate depth and breadth.",
                "Content includes all major subtopics and addresses key questions identified in SERPs."
            ),
            "Keyword Optimization": (
                "Content is well-optimized for target keywords without over-optimization.",
                "Primary and secondary keywords are naturally distributed throughout the content."
            ),
            "Content Structure": (
                "Content is well-structured with appropriate headings and organization.",
                "Logical hierarchy of H1-H4 tags that helps both users and search engines navigate the content."
            ),
            "Readability": (
                "Content is readable and accessible to the target audience.",
                "Reading level is appropriate, with clear language and well-structured paragraphs."
            ),
            "SERP Feature Optimization": (
                "Content is optimized for relevant SERP features.",
                "Structured for featured snippets and includes FAQ sections for People Also Ask boxes."
            ),
            "Semantic Relevance": (
                "Content demonstrates strong semantic relevance to the topic.",
                "Uses related terms, entities, and concepts that establish topical authority."
            ),
            "Entity Coverage": (
                "Content covers important entities related to the topic.",
                "Includes definitions, explanations, and relationships between key entities."
            ),
            "User Intent Match": (
                "Content aligns well with the primary user intent for target queries.",
                "Addresses informational, navigational, or transactional needs as appropriate."
            ),
            "Content Freshness": (
                "Content appears fresh and up-to-date.",
                "Includes recent information, statistics, and references to current trends."
            ),
            "Mobile Optimization": (
                "Content is well-optimized for mobile devices.",
                "Responsive design, appropriate font sizes, and mobile-friendly interactive elements."
            )
        }
        
        return descriptions.get(factor, ("This factor affects your ranking.", "No additional details available."))
    
    def _generate_improvement_suggestions(self, ranking_factors):
        """Generate improvement suggestions based on ranking factors."""
        # Identify lowest scoring factors
        sorted_factors = sorted(ranking_factors, key=lambda x: x["score"])
        weak_areas = [factor["factor_name"] for factor in sorted_factors[:2]]
        
        # Add some random areas that weren't in the ranking factors
        ranked_factor_names = [factor["factor_name"] for factor in ranking_factors]
        additional_areas = [area for area in self.improvement_areas if area not in ranked_factor_names]
        selected_additional = random.sample(additional_areas, min(4, len(additional_areas)))
        
        all_improvement_areas = weak_areas + selected_additional
        
        # Generate 4-6 improvement suggestions
        num_suggestions = random.randint(4, 6)
        selected_areas = random.sample(all_improvement_areas, min(num_suggestions, len(all_improvement_areas)))
        
        suggestions = []
        for area in selected_areas:
            suggestion, impact, effort = self._get_improvement_suggestion(area)
            
            suggestions.append({
                "area": area,
                "suggestion": suggestion,
                "impact": impact,
                "effort": effort
            })
        
        return suggestions
    
    def _get_improvement_suggestion(self, area):
        """Get suggestion, impact, and effort for an improvement area."""
        suggestions = {
            "Multimedia Enhancement": (
                "Add more visual elements such as infographics, charts, and videos to improve engagement and time on page.",
                "Medium",
                "Medium"
            ),
            "Schema Markup": (
                "Implement additional schema markup types to enhance SERP appearance and click-through rates.",
                "Medium",
                "Low"
            ),
            "Internal Linking": (
                "Strengthen internal linking structure to better distribute page authority and improve crawlability.",
                "Medium",
                "Low"
            ),
            "Mobile Optimization": (
                "Further optimize for mobile experience, focusing on Core Web Vitals metrics.",
                "High",
                "Medium"
            ),
            "User Experience": (
                "Improve page load speed and interactive elements to reduce bounce rate and increase engagement.",
                "High",
                "Medium"
            ),
            "Content Freshness": (
                "Establish a regular update schedule to keep content fresh and current with latest trends.",
                "Medium",
                "Medium"
            ),
            "Semantic Depth": (
                "Enhance semantic depth by expanding coverage of related concepts and entities.",
                "High",
                "Medium"
            ),
            "Entity Relationships": (
                "Clarify relationships between key entities to strengthen knowledge graph connections.",
                "Medium",
                "Medium"
            ),
            "Topical Authority": (
                "Develop additional supporting content to establish stronger topical authority in this subject area.",
                "High",
                "High"
            ),
            "E-A-T Signals": (
                "Strengthen expertise, authoritativeness, and trustworthiness signals through author credentials and references.",
                "High",
                "Medium"
            ),
            "Content Comprehensiveness": (
                "Expand content to cover additional subtopics identified in competitor analysis.",
                "High",
                "Medium"
            ),
            "Keyword Optimization": (
                "Refine keyword usage to better target high-opportunity terms identified in keyword analysis.",
                "Medium",
                "Low"
            ),
            "Content Structure": (
                "Improve content structure with more logical heading hierarchy and better section organization.",
                "Medium",
                "Low"
            ),
            "Readability": (
                "Enhance readability by simplifying language, shortening sentences, and adding more subheadings.",
                "Medium",
                "Low"
            ),
            "SERP Feature Optimization": (
                "Restructure content to better target featured snippets and other SERP features.",
                "High",
                "Medium"
            )
        }
        
        return suggestions.get(area, ("Improve this area to enhance overall performance.", "Medium", "Medium"))
