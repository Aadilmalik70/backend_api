# Filename: src/modules/insight_generator_enhanced.py
import asyncio
import os
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import numpy as np

logger = logging.getLogger("keyword_research.insight_generator")

async def invoke_with_retry(chain, payload, retries=5, delay=5):
    for attempt in range(retries):
        try:
            if asyncio.iscoroutinefunction(chain.invoke):
                return await chain.invoke(payload)
            else:
                return chain.invoke(payload)
        except Exception as e:
            if hasattr(e, "status_code") and e.status_code == 429:
                logger.warning(f"Rate limit hit (429). Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(delay)
            elif "ResourceExhausted" in str(e):
                logger.warning(f"Resource exhausted. Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(delay)
            else:
                logger.warning(f"Error in invoke_with_retry: {e}. Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(delay)
    raise RuntimeError(f"invoke_with_retry failed after {retries} attempts.")

# Enhanced models for more detailed content blueprints
class ContentBlueprintSectionKeypoint(BaseModel):
    """Represents a key point or detail to cover within a section."""
    point: str = Field(..., description="The specific point or detail to cover.")
    rationale: Optional[str] = Field(None, description="Why this point is important or relevant.")
    competitor_reference: Optional[str] = Field(None, description="Reference to competitor content that covers this point well.")

class ContentBlueprintSection(BaseModel):
    """Represents a section in a content outline blueprint."""
    level: int = Field(..., description="Heading level (e.g., 1 for H1, 2 for H2, 3 for H3).")
    title: str = Field(..., description="Proposed title for the section.")
    themes_to_cover: List[str] = Field(default_factory=list, description="Key themes or sub-topics to cover in this section.")
    notes: Optional[str] = Field(None, description="Optional notes or specific points for this section.")
    key_points: List[ContentBlueprintSectionKeypoint] = Field(default_factory=list, description="Specific key points to cover in this section.")
    keyword_placement: List[str] = Field(default_factory=list, description="Keywords to strategically place in this section.")
    sub_sections: List["ContentBlueprintSection"] = Field(default_factory=list)

ContentBlueprintSection.update_forward_refs()

class ContentBlueprint(BaseModel):
    """Represents a suggested content blueprint for a keyword."""
    target_keyword: str = Field(..., description="The primary keyword the blueprint is for.")
    recommended_content_type: str = Field(..., description="Recommended content format (e.g., Blog Post, Guide, Comparison).")
    recommended_word_count_range: str = Field(..., description="Suggested word count range (e.g., '1500-2000 words').")
    key_themes_overall: List[str] = Field(default_factory=list, description="Overall key themes identified for the topic.")
    suggested_outline: List[ContentBlueprintSection] = Field(default_factory=list, description="The structured content outline.")
    unique_angle_ideas: List[str] = Field(default_factory=list, description="Ideas for differentiating the content.")
    target_paa_questions: List[str] = Field(default_factory=list, description="Relevant People Also Ask questions to address.")
    competitor_gaps: List[str] = Field(default_factory=list, description="Content gaps identified in competitor content.")
    section_word_count_distribution: Dict[str, str] = Field(default_factory=dict, description="Suggested word count distribution for major sections.")
    serp_feature_targeting: Dict[str, str] = Field(default_factory=dict, description="SERP features to target and how to optimize for them.")

# Enhanced models for deeper competitor analysis
class CompetitorContentStructurePattern(BaseModel):
    """Represents a content structure pattern identified across competitors."""
    pattern_name: str = Field(..., description="Name of the identified pattern.")
    description: str = Field(..., description="Description of the pattern.")
    frequency: str = Field(..., description="How frequently this pattern appears (e.g., '80% of competitors').")
    effectiveness: str = Field(..., description="Assessment of the pattern's effectiveness.")

class CompetitiveStrategySummary(BaseModel):
    """Summarizes the competitive content strategy."""
    dominant_content_types: List[str] = Field(default_factory=list, description="Most common content formats among top competitors.")
    average_word_count: str = Field(..., description="Average word count of ranking content.")
    common_themes_and_angles: List[str] = Field(default_factory=list, description="Common themes, topics, and angles used by top competitors.")
    common_structure_patterns: List[CompetitorContentStructurePattern] = Field(default_factory=list, description="Common heading structures or content organization patterns.")
    common_media_types: List[str] = Field(default_factory=list, description="Most common media types used.")
    readability_analysis: Dict[str, Any] = Field(default_factory=dict, description="Analysis of readability scores across competitors.")
    content_freshness: Dict[str, Any] = Field(default_factory=dict, description="Analysis of content freshness and update patterns.")
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict, description="Available engagement metrics from competitor content.")
    winning_formula_summary: str = Field(..., description="A brief summary of the apparent 'winning formula' in the SERP.")

# Enhanced models for SERP feature optimization
class SerpFeatureOptimizationStep(BaseModel):
    """Represents a specific optimization step for a SERP feature."""
    step: str = Field(..., description="The specific optimization action to take.")
    implementation_details: str = Field(..., description="Details on how to implement this step.")
    priority: str = Field(..., description="Priority of this step (High, Medium, Low).")

class ActionableSerpFeatureInsight(BaseModel):
    """Provides actionable advice for a specific SERP feature."""
    feature: str = Field(..., description="The SERP feature (e.g., 'featured_snippet', 'people_also_ask').")
    description: str = Field(..., description="Brief description of the feature's presence.")
    strategy: str = Field(..., description="Specific, actionable steps to optimize for this feature.")
    optimization_steps: List[SerpFeatureOptimizationStep] = Field(default_factory=list, description="Detailed steps to optimize for this feature.")
    content_requirements: List[str] = Field(default_factory=list, description="Content requirements to target this feature.")
    technical_requirements: List[str] = Field(default_factory=list, description="Technical requirements to target this feature.")

class SerpFeatureInsightList(BaseModel):
    __root__: List[ActionableSerpFeatureInsight]

class IntentMatchedRecommendation(BaseModel):
    """Recommendation for content format based on intent and competition."""
    intent: str = Field(..., description="The primary intent analyzed.")
    recommendation_type: str = Field(..., description="Type of recommendation (e.g., 'content_format', 'intent_gap').")
    title: str = Field(..., description="Title of the recommendation.")
    description: str = Field(..., description="Detailed explanation of the recommendation.")

class ContentPerformancePrediction(BaseModel):
    """Prediction of content performance based on SERP and competitor analysis."""
    ranking_potential: int = Field(..., description="Predicted ranking potential (1-10).")
    traffic_potential: int = Field(..., description="Predicted traffic potential (1-10).")
    conversion_potential: int = Field(..., description="Predicted conversion potential (1-10).")
    time_to_rank: str = Field(..., description="Estimated time to achieve ranking (e.g., '2-3 months').")
    ranking_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Key factors influencing ranking potential.")
    performance_risks: List[str] = Field(default_factory=list, description="Potential risks to performance.")
    performance_opportunities: List[str] = Field(default_factory=list, description="Potential opportunities to improve performance.")

class InsightSummary(BaseModel):
    """Overall summary of the keyword research analysis."""
    overall_summary: str = Field(..., description="A concise summary highlighting key findings, opportunities, and recommendations.")
    key_opportunities_highlight: List[str] = Field(default_factory=list, description="A few top opportunities highlighted from the analysis.")

class InsightGenerator:
    """
    Generates insights from the collected keyword and competitor data using LLM.
    Enhanced version with more detailed blueprints and deeper competitor analysis.
    """

    def __init__(self):
        try:
            self.api_key = os.getenv("GOOGLE_API_KEY")
            self.model = "gemini-2.0-flash"
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=0.7
            )
            logger.info("ChatGoogleGenerativeAI (Gemini) initialized for InsightGenerator")
            self.llm_available = True
        except Exception as e:
            logger.error(f"Error initializing ChatGoogleGenerativeAI in InsightGenerator: {str(e)}")
            self.llm = None
            self.llm_available = False

        # Initialize output parsers for structured output
        if self.llm_available:
            self.blueprint_parser = JsonOutputParser(pydantic_object=ContentBlueprint)
            self.competitive_summary_parser = JsonOutputParser(pydantic_object=CompetitiveStrategySummary)
            self.serp_feature_parser = JsonOutputParser(pydantic_object=SerpFeatureInsightList)
            self.intent_recommendation_parser = JsonOutputParser(pydantic_object=List[IntentMatchedRecommendation])
            self.insight_summary_parser = JsonOutputParser(pydantic_object=InsightSummary)
            self.performance_prediction_parser = JsonOutputParser(pydantic_object=ContentPerformancePrediction)
        else:
            self.blueprint_parser = None
            self.competitive_summary_parser = None
            self.serp_feature_parser = None
            self.intent_recommendation_parser = None
            self.insight_summary_parser = None
            self.performance_prediction_parser = None

    async def generate_insights(self, input_data, keyword_analysis, serp_data, competitor_data):
        """
        Generate insights from the collected data using LLM.

        Args:
            input_data (dict): Processed user input (includes seed keyword)
            keyword_analysis (dict): Processed keyword data (intent, scores, clusters, questions)
            serp_data (dict): Comprehensive SerpAPI data for keywords (includes SV, KD, features, results)
            competitor_data (dict): Detailed Competitor content analysis

        Returns:
            dict: Generated insights
        """
        logger.info("Generating enhanced insights from the collected data")

        # Initialize insights structure with enhanced fields
        insights = {
            "content_opportunities": [],
            "serp_feature_insights": [],
            "competitive_landscape_summary": {},
            "keyword_recommendations": [],
            "topic_clusters": [],
            "intent_distribution": {},
            "content_blueprints": {},
            "content_performance_predictions": {},  # NEW: Performance predictions
            "summary": {}
        }

        # Extract data needed for insight generation
        keywords = input_data.get("keywords", [])
        seed_keyword = input_data.get("seed_keyword", "")
        intent_classification = keyword_analysis.get("intent_classification", {})
        keyword_scores = keyword_analysis.get("keyword_scores", {})
        question_keywords = keyword_analysis.get("question_keywords", [])
        topic_clusters = keyword_analysis.get("clusters", [])

        # Ensure SerpAPI data is available
        serp_api_serp_data = serp_data.get("serp_data", {})
        serp_api_features = serp_data.get("features", {})
        serp_api_paa = serp_data.get("paa_questions", {})
        serp_api_related = serp_data.get("related_searches", {})
        serp_api_sv = serp_data.get("search_volume", {})
        serp_api_kd = serp_data.get("keyword_difficulty", {})

        # Ensure detailed competitor data is available
        analyzed_urls = competitor_data.get("analyzed_urls", [])
        detailed_content_analysis = competitor_data.get("content_analysis", {})
        competitor_summary_data = competitor_data.get("summary", {})

        # Use LLM for sophisticated insights if available
        if self.llm_available:
            try:
                # 1. Generate Overall Summary (AI)
                logger.info("Generating overall insights summary using LLM.")
                insights["summary"] = await self._generate_summary_with_llm(
                    input_data, keyword_analysis, serp_data, competitor_data, insights
                )
                logger.info("Overall summary generated.")

                # 2. Analyze Competitive Landscape & Summarize Winning Formula (AI) - ENHANCED
                logger.info("Analyzing competitive landscape with enhanced metrics.")
                insights["competitive_landscape_summary"] = await self._summarize_competitive_content_strategy_enhanced(
                    analyzed_urls, detailed_content_analysis, competitor_summary_data, serp_api_features
                )
                logger.info("Enhanced competitive landscape summary generated.")

                # 3. Generate Actionable SERP Feature Insights (AI) - ENHANCED
                logger.info("Generating detailed SERP feature optimization strategies.")
                insights["serp_feature_insights"] = await self._generate_serp_feature_insights_enhanced(
                    serp_api_features, keywords, keyword_scores
                )
                if not isinstance(insights["serp_feature_insights"], list):
                    insights["serp_feature_insights"] = self._generate_serp_feature_insights_basic(serp_data)

                logger.info(f"Generated {len(insights['serp_feature_insights'])} enhanced SERP feature insights.")

                # 4. Generate Intent-Matched Content Format Recommendations (AI)
                logger.info("Generating intent-matched content recommendations.")
                ai_intent_recs = await self._generate_intent_matched_recommendations_ai(
                    intent_classification, competitor_summary_data, serp_api_features
                )
                if isinstance(ai_intent_recs, list):
                    insights["content_opportunities"].extend(ai_intent_recs)
                else:
                    logger.warning("AI intent recommendations did not return a list.")
                    insights["content_opportunities"].extend(self._generate_content_opportunities_basic(keyword_analysis, serp_data, competitor_data))

                logger.info(f"Generated {len(insights['content_opportunities'])} intent-matched recommendations.")

                # 5. Generate Enhanced Content Blueprints (AI)
                target_keywords_for_blueprint = [seed_keyword]
                high_opp_keywords = sorted(keyword_scores.items(), key=lambda item: item[1].get("score", 0), reverse=True)[:5]
                keywords_added = 0
                for kw, score_data in high_opp_keywords:
                    if kw != seed_keyword and kw in keywords and score_data.get("score", 0) > 60:
                        if keywords_added < 2:
                            target_keywords_for_blueprint.append(kw)
                            keywords_added += 1

                logger.info(f"Generating enhanced content blueprints for keywords: {target_keywords_for_blueprint}")
                for target_kw in target_keywords_for_blueprint:
                    blueprint = await self._generate_enhanced_content_blueprint(
                        target_kw,
                        serp_api_serp_data.get(target_kw, []),
                        detailed_content_analysis,
                        keyword_analysis,
                        insights.get("competitive_landscape_summary", {}),
                        serp_data,
                        insights.get("serp_feature_insights", [])
                    )
                    if blueprint:
                        insights["content_blueprints"][target_kw] = blueprint
                        logger.info(f"Generated enhanced blueprint for '{target_kw}'.")
                    else:
                        logger.warning(f"Failed to generate enhanced blueprint for '{target_kw}'.")

                # 6. Generate Content Performance Predictions (NEW)
                logger.info("Generating content performance predictions.")
                for target_kw in target_keywords_for_blueprint:
                    if target_kw in insights["content_blueprints"]:
                        prediction = await self._predict_content_performance(
                            target_kw,
                            serp_data,
                            competitor_data,
                            keyword_analysis,
                            insights["content_blueprints"][target_kw]
                        )
                        if prediction:
                            insights["content_performance_predictions"][target_kw] = prediction
                            logger.info(f"Generated performance prediction for '{target_kw}'.")
                        else:
                            logger.warning(f"Failed to generate performance prediction for '{target_kw}'.")

                # 7. Generate Keyword Recommendations (Enhanced)
                insights["keyword_recommendations"] = await self._generate_keyword_recommendations_enhanced(
                    keyword_analysis, serp_data
                )
                logger.info(f"Generated {len(insights['keyword_recommendations'])} enhanced keyword recommendations.")

            except Exception as e:
                logger.error(f"Error during enhanced insight generation: {str(e)}", exc_info=True)
                # Fallback to basic insights if enhanced generation fails
                return await self._generate_basic_insights(input_data, keyword_analysis, serp_data, competitor_data)

            # Add topic clusters and intent distribution
            insights["topic_clusters"] = topic_clusters
            insights["intent_distribution"] = self._calculate_intent_distribution_from_dict(intent_classification)

            return insights
        else:
            logger.warning("LLM not available. Generating basic insights only.")
            return await self._generate_basic_insights(input_data, keyword_analysis, serp_data, competitor_data)

    async def _generate_enhanced_content_blueprint(self, target_keyword, organic_results, detailed_content_analysis, keyword_analysis, competitive_summary, serp_data, serp_feature_insights):
        """
        Generate an enhanced content blueprint with more detailed outlines and competitor insights.
        
        Args:
            target_keyword (str): The keyword to generate a blueprint for
            organic_results (list): Organic search results for the keyword
            detailed_content_analysis (dict): Detailed competitor content analysis
            keyword_analysis (dict): Processed keyword data
            competitive_summary (dict): Summary of competitive landscape
            serp_data (dict): Comprehensive SerpAPI data
            serp_feature_insights (list): SERP feature insights
            
        Returns:
            dict: Enhanced content blueprint
        """
        if not self.llm_available or not self.blueprint_parser:
            logger.warning("LLM not available for enhanced blueprint generation.")
            return None

        try:
            # Sample relevant competitor content analysis data
            relevant_analysis_data = []
            
            # First, try to find content that specifically mentions the target keyword
            keyword_specific_content = []
            for url, analysis in detailed_content_analysis.items():
                if not analysis:
                    continue
                    
                # Check if target keyword appears in title, headings, or main points
                title = analysis.get("title", "").lower()
                headings = [h.lower() for h in analysis.get("headings", [])]
                main_points = analysis.get("main_points_summary", "").lower()
                
                if (target_keyword.lower() in title or 
                    any(target_keyword.lower() in h for h in headings) or
                    target_keyword.lower() in main_points):
                    keyword_specific_content.append((url, analysis))
            
            # If we found keyword-specific content, prioritize it
            if keyword_specific_content:
                # Sort by word count (assuming longer content is more comprehensive)
                keyword_specific_content.sort(key=lambda x: x[1].get("word_count", 0), reverse=True)
                # Take top 3 most comprehensive pieces
                for url, analysis in keyword_specific_content[:3]:
                    relevant_analysis_data.append({
                        "url": url,
                        "title": analysis.get("title"),
                        "content_type": analysis.get("content_type"),
                        "word_count": analysis.get("word_count"),
                        "readability_score": analysis.get("readability_score"),
                        "key_themes": analysis.get("key_themes", []),
                        "headings": analysis.get("headings", []),
                        "main_points_summary": analysis.get("main_points_summary"),
                        "calls_to_action": analysis.get("calls_to_action", []),
                        "media_types": analysis.get("media_types", [])
                    })
            
            # If we don't have enough keyword-specific content, add other high-quality content
            if len(relevant_analysis_data) < 3:
                # Sort all content by word count as a proxy for quality/comprehensiveness
                all_content = [(url, analysis) for url, analysis in detailed_content_analysis.items() if analysis]
                all_content.sort(key=lambda x: x[1].get("word_count", 0), reverse=True)
                
                # Add top content until we have at least 3 samples
                for url, analysis in all_content:
                    if len(relevant_analysis_data) >= 3:
                        break
                        
                    # Skip if already included
                    if any(item["url"] == url for item in relevant_analysis_data):
                        continue
                        
                    relevant_analysis_data.append({
                        "url": url,
                        "title": analysis.get("title"),
                        "content_type": analysis.get("content_type"),
                        "word_count": analysis.get("word_count"),
                        "readability_score": analysis.get("readability_score"),
                        "key_themes": analysis.get("key_themes", []),
                        "headings": analysis.get("headings", []),
                        "main_points_summary": analysis.get("main_points_summary"),
                        "calls_to_action": analysis.get("calls_to_action", []),
                        "media_types": analysis.get("media_types", [])
                    })

            # Get PAA and Related Searches for this keyword
            paa_for_kw_from_serp = serp_data.get("paa_questions", {}).get(target_keyword, [])
            related_for_kw_from_serp = serp_data.get("related_searches", {}).get(target_keyword, [])

            # Include relevant keyword clusters
            relevant_clusters = [cluster for cluster in keyword_analysis.get("clusters", []) if target_keyword in cluster.get("keywords", [])]
            related_cluster_keywords = []
            for cluster in relevant_clusters:
                related_cluster_keywords.extend(cluster.get("keywords", []))
            related_cluster_keywords = list(set(related_cluster_keywords))

            # Get SV and KD for the target keyword for context
            sv_for_kw = serp_data.get("search_volume", {}).get(target_keyword)
            kd_for_kw = serp_data.get("keyword_difficulty", {}).get(target_keyword)
            target_kw_score_data = keyword_analysis.get("keyword_scores", {}).get(target_keyword, {})
            
            # Extract relevant SERP features for this keyword
            relevant_serp_features = []
            for feature_insight in serp_feature_insights:
                if isinstance(feature_insight, dict) and "feature" in feature_insight:
                    feature_name = feature_insight["feature"]
                    keywords_with_feature = []
                    
                    # Check if this feature appears for our target keyword
                    for kw, features in serp_data.get("features", {}).items():
                        if feature_name in features:
                            keywords_with_feature.append(kw)
                    
                    if target_keyword in keywords_with_feature or len(keywords_with_feature) > 1:
                        relevant_serp_features.append({
                            "feature": feature_name,
                            "strategy": feature_insight.get("strategy", ""),
                            "optimization_steps": feature_insight.get("optimization_steps", []),
                            "content_requirements": feature_insight.get("content_requirements", [])
                        })

            # Prepare enhanced context for the LLM
            context = {
                "target_keyword": target_keyword,
                "keyword_metrics": {
                    "search_volume": sv_for_kw,
                    "keyword_difficulty": kd_for_kw,
                    "overall_score": target_kw_score_data.get("score")
                },
                "overall_intent": keyword_analysis.get("intent_classification", {}).get(target_keyword, "unknown"),
                "competitive_content_analysis_samples": relevant_analysis_data,
                "competitive_landscape_summary": competitive_summary,
                "relevant_paa_questions": paa_for_kw_from_serp,
                "relevant_related_searches": related_for_kw_from_serp,
                "related_cluster_keywords": related_cluster_keywords,
                "relevant_serp_features": relevant_serp_features
            }

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert content strategist and SEO professional. Your task is to analyze the provided data about a target keyword, competitive SERP results, and competitor content to generate a detailed, enhanced content blueprint. The blueprint should guide the creation of a high-ranking, user-focused piece of content.

                Analyze the 'competitive_content_analysis_samples' and 'competitive_landscape_summary' to understand common structures, themes, winning angles, and content types.
                Consider the 'target_keyword', 'keyword_metrics', 'overall_intent', 'relevant_paa_questions', and 'relevant_related_searches' to ensure the blueprint covers user needs and search intent.
                Use 'related_cluster_keywords' to identify related sub-topics.
                Incorporate 'relevant_serp_features' to optimize content for specific SERP features.

                Generate:
                1. A recommended content type and a realistic word count range based on competitor analysis.
                2. A structured outline (H1, H2, H3s) that incorporates common successful structures and addresses key themes and user questions.
                3. For each outline section:
                   - List specific sub-topics or themes to cover
                   - Provide 2-3 key points with rationale and competitor references
                   - Suggest keywords to place in that section
                4. Ideas for unique angles to make the content stand out from competitors.
                5. List the specific PAA questions that should be addressed in the content.
                6. Identify content gaps in competitor content that can be exploited.
                7. Suggest word count distribution for major sections.
                8. Provide SERP feature targeting recommendations for the content.

                Return the blueprint EXCLUSIVELY as a single, valid JSON object matching the ContentBlueprint Pydantic model schema. Ensure the JSON is perfectly formatted.
                {format_instructions}
                """),
                ("human", """Generate an enhanced content blueprint based on the following data:
                Data: {context}
                """)]
            )

            chain = prompt_template | self.llm | self.blueprint_parser

            # Use invoke directly for a single completion
            response = await invoke_with_retry(chain, {"context": json.dumps(context), "format_instructions": self.blueprint_parser.get_format_instructions()})
            return response.dict()

        except Exception as e:
            logger.error(f"Error generating enhanced content blueprint for '{target_keyword}': {str(e)}", exc_info=True)
            return None

    async def _summarize_competitive_content_strategy_enhanced(self, analyzed_urls, detailed_content_analysis, competitor_summary_data, serp_api_features):
        """
        Generate an enhanced summary of competitive content strategy with deeper analysis.
        
        Args:
            analyzed_urls (list): List of URLs that were analyzed
            detailed_content_analysis (dict): Detailed competitor content analysis
            competitor_summary_data (dict): Summary of competitor content
            serp_api_features (dict): SERP features by keyword
            
        Returns:
            dict: Enhanced competitive landscape summary
        """
        if not self.llm_available or not self.competitive_summary_parser or not analyzed_urls:
            logger.warning("LLM not available or no URLs analyzed for competitive summary.")
            return {}

        try:
            # Extract readability scores
            readability_scores = {}
            for url, analysis in detailed_content_analysis.items():
                if analysis and "readability_score" in analysis:
                    readability_scores[url] = analysis["readability_score"]
            
            # Calculate average readability if scores are available
            avg_readability = None
            if readability_scores:
                avg_readability = sum(readability_scores.values()) / len(readability_scores)
            
            # Extract content structure patterns
            heading_structures = {}
            for url, analysis in detailed_content_analysis.items():
                if analysis and "headings" in analysis:
                    headings = analysis.get("headings", [])
                    if headings:
                        # Create a simplified representation of the heading structure
                        structure = []
                        for heading in headings[:5]:  # Limit to first 5 headings for pattern analysis
                            # Try to determine if it's H1, H2, H3 based on position
                            if heading == headings[0]:
                                level = "H1"
                            elif len(structure) > 0 and structure[-1].startswith("H1"):
                                level = "H2"
                            elif len(structure) > 0 and structure[-1].startswith("H2"):
                                level = "H3"
                            else:
                                level = "H2"  # Default to H2
                            
                            structure.append(f"{level}: {heading}")
                        
                        heading_structures[url] = structure
            
            # Extract publication dates for freshness analysis
            publication_dates = {}
            for url, analysis in detailed_content_analysis.items():
                if analysis and "publication_date" in analysis:
                    pub_date = analysis.get("publication_date")
                    if pub_date and pub_date.lower() != "null" and pub_date != "None":
                        publication_dates[url] = pub_date
            
            # Prepare context for the LLM
            context = {
                "analyzed_urls_count": len(analyzed_urls),
                "competitor_content_summary_stats": competitor_summary_data,
                "common_themes_across_urls": competitor_summary_data.get("common_themes_summary", [])[:10],
                "serp_features_observed_keywords": list(serp_api_features.keys()),
                "unique_serp_features": list(set(sum(serp_api_features.values(), []))),
                "readability_scores": readability_scores,
                "average_readability": avg_readability,
                "heading_structures": heading_structures,
                "publication_dates": publication_dates,
                "sample_competitive_analysis": [{
                    "url": url,
                    "title": analysis.get("title"),
                    "content_type": analysis.get("content_type"),
                    "word_count": analysis.get("word_count"),
                    "readability_score": analysis.get("readability_score"),
                    "key_themes": analysis.get("key_themes", [])[:5],
                    "main_points_summary": analysis.get("main_points_summary"),
                    "headings": analysis.get("headings", [])[:7],
                    "calls_to_action": analysis.get("calls_to_action", []),
                    "media_types": analysis.get("media_types", [])
                } for url, analysis in list(detailed_content_analysis.items())[:5] if analysis]
            }

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert SEO analyst specializing in competitive content strategy. Your task is to analyze the provided data about top-ranking competitor content and provide a detailed analysis of the competitive landscape.

                Analyze the provided data to identify:
                1. Dominant content types and average length
                2. Readability patterns and optimal reading level
                3. Recurring themes, topics, and angles used by top competitors
                4. Common structural patterns in headings and content organization
                5. Media usage patterns and effectiveness
                6. Content freshness and update patterns
                7. Engagement signals where available
                8. How SERP features influence content strategy

                Based on these patterns, articulate the apparent "winning formula" for ranking in this search landscape in a brief narrative summary.

                Return the analysis EXCLUSIVELY as a single, valid JSON object matching the CompetitiveStrategySummary Pydantic model schema. Ensure the JSON is perfectly formatted.
                {format_instructions}
                """),
                ("human", """Analyze the following competitive data and provide a detailed content strategy analysis:
                Data: {context}
                """)]
            )

            chain = prompt_template | self.llm | self.competitive_summary_parser

            # Use invoke directly for a single completion
            response = await invoke_with_retry(chain, {"context": json.dumps(context), "format_instructions": self.competitive_summary_parser.get_format_instructions()})
            return response.dict()

        except Exception as e:
            logger.error(f"Error generating enhanced competitive summary: {str(e)}", exc_info=True)
            return {}

    async def _generate_serp_feature_insights_enhanced(self, serp_api_features, keywords, keyword_scores):
        """
        Generate enhanced actionable SERP feature insights with specific optimization strategies.
        
        Args:
            serp_api_features (dict): SERP features by keyword
            keywords (list): List of keywords
            keyword_scores (dict): Keyword scores
            
        Returns:
            list: Enhanced SERP feature insights
        """
        if not self.llm_available or not self.serp_feature_parser or not serp_api_features:
            logger.warning("LLM not available or no SERP features detected for insights.")
            return []

        try:
            # Prepare context for the LLM - List features and keywords where they appear
            feature_occurrence = {}
            for keyword, features in serp_api_features.items():
                if isinstance(features, list):
                    for feature in features:
                        if feature not in feature_occurrence:
                            feature_occurrence[feature] = {"count": 0, "keywords": []}
                        feature_occurrence[feature]["count"] += 1
                        feature_occurrence[feature]["keywords"].append(keyword)

            # Filter for features appearing for at least 1 keyword
            notable_features = {f: data for f, data in feature_occurrence.items() if data["count"] >= 1}

            # Add keyword scores for context
            features_context = {
                "notable_features": notable_features,
                "keyword_scores": keyword_scores
            }

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert SEO specialist focused on SERP features. Analyze the provided data about observed SERP features for a set of keywords.

                For each notable feature, provide:
                1. A brief description of its significance
                2. Specific, actionable strategies to optimize content for that feature
                3. Detailed optimization steps with implementation details and priority
                4. Content requirements to target this feature
                5. Technical requirements to target this feature

                Consider the keywords where the feature appears and their scores (opportunity/difficulty) when suggesting strategies.
                Be specific and practical in your recommendations.

                Return a JSON array of insights, where each object in the array matches the ActionableSerpFeatureInsight Pydantic model schema. Only include insights for the notable features provided.
                {format_instructions}
                """),
                ("human", """Analyze the following SERP feature data and provide detailed optimization insights:
                Data: {context}
                """)]
            )

            chain = prompt_template | self.llm | self.serp_feature_parser

            # Use invoke directly for a single completion
            response = await invoke_with_retry(chain, {"context": json.dumps(features_context), "format_instructions": self.serp_feature_parser.get_format_instructions()})

            # Validate that the response is indeed a list of dictionaries/objects
            if isinstance(response, list):
                return [item.dict() if hasattr(item, 'dict') else item for item in response]
            else:
                logger.warning("LLM did not return a list for enhanced SERP feature insights.")
                return []

        except Exception as e:
            logger.error(f"Error generating enhanced SERP feature insights: {str(e)}", exc_info=True)
            return []

    async def _predict_content_performance(self, target_keyword, serp_data, competitor_data, keyword_analysis, content_blueprint):
        """
        Predict content performance based on SERP and competitor analysis.
        
        Args:
            target_keyword (str): The keyword to predict performance for
            serp_data (dict): Comprehensive SerpAPI data
            competitor_data (dict): Detailed competitor content analysis
            keyword_analysis (dict): Processed keyword data
            content_blueprint (dict): Content blueprint for the keyword
            
        Returns:
            dict: Content performance prediction
        """
        if not self.llm_available or not self.performance_prediction_parser:
            logger.warning("LLM not available for content performance prediction.")
            return None

        try:
            # Extract relevant data for performance prediction
            keyword_metrics = {
                "search_volume": serp_data.get("search_volume", {}).get(target_keyword),
                "keyword_difficulty": serp_data.get("keyword_difficulty", {}).get(target_keyword),
                "score": keyword_analysis.get("keyword_scores", {}).get(target_keyword, {}).get("score")
            }
            
            intent = keyword_analysis.get("intent_classification", {}).get(target_keyword, "unknown")
            
            # Get SERP features for this keyword
            serp_features = serp_data.get("features", {}).get(target_keyword, [])
            
            # Get competitor summary data
            competitor_summary = competitor_data.get("summary", {})
            
            # Prepare context for the LLM
            context = {
                "target_keyword": target_keyword,
                "keyword_metrics": keyword_metrics,
                "intent": intent,
                "serp_features": serp_features,
                "competitor_summary": competitor_summary,
                "content_blueprint": content_blueprint
            }

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert SEO analyst specializing in content performance prediction. Your task is to analyze the provided data about a target keyword, SERP features, competitor content, and a content blueprint to predict the performance of content created using this blueprint.

                Consider:
                1. Keyword metrics (search volume, difficulty, overall score)
                2. Search intent and how well the blueprint addresses it
                3. SERP features present and how they might affect ranking
                4. Competitor content quality and the blueprint's ability to compete
                5. Content comprehensiveness and uniqueness in the blueprint

                Provide a prediction that includes:
                - Ranking potential on a scale of 1-10
                - Traffic potential on a scale of 1-10
                - Conversion potential on a scale of 1-10
                - Estimated time to achieve ranking
                - Key factors influencing ranking potential
                - Potential risks to performance
                - Potential opportunities to improve performance

                Return the prediction EXCLUSIVELY as a single, valid JSON object matching the ContentPerformancePrediction Pydantic model schema. Ensure the JSON is perfectly formatted.
                {format_instructions}
                """),
                ("human", """Predict content performance based on the following data:
                Data: {context}
                """)]
            )

            chain = prompt_template | self.llm | self.performance_prediction_parser

            # Use invoke directly for a single completion
            response = await invoke_with_retry(chain, {"context": json.dumps(context), "format_instructions": self.performance_prediction_parser.get_format_instructions()})
            return response.dict()

        except Exception as e:
            logger.error(f"Error generating content performance prediction for '{target_keyword}': {str(e)}", exc_info=True)
            return None

    async def _generate_keyword_recommendations_enhanced(self, keyword_analysis, serp_data):
        """
        Generate enhanced keyword recommendations with advanced metrics and trend analysis.
        
        Args:
            keyword_analysis (dict): Processed keyword data
            serp_data (dict): Comprehensive SerpAPI data
            
        Returns:
            list: Enhanced keyword recommendations
        """
        # Start with basic recommendations
        basic_recommendations = self._generate_keyword_recommendations_basic(keyword_analysis, serp_data)
        
        if not self.llm_available:
            return basic_recommendations
            
        try:
            # Extract PAA questions and related searches
            paa_questions = {}
            related_searches = {}
            
            for keyword, questions in serp_data.get("paa_questions", {}).items():
                if questions:
                    paa_questions[keyword] = questions
                    
            for keyword, related in serp_data.get("related_searches", {}).items():
                if related:
                    related_searches[keyword] = related
            
            # Extract keyword scores and metrics
            keyword_scores = keyword_analysis.get("keyword_scores", {})
            intent_classification = keyword_analysis.get("intent_classification", {})
            
            # Prepare context for the LLM
            context = {
                "basic_recommendations": basic_recommendations,
                "paa_questions": paa_questions,
                "related_searches": related_searches,
                "keyword_scores": keyword_scores,
                "intent_classification": intent_classification
            }
            
            # Enhance recommendations with LLM insights
            enhanced_recommendations = []
            
            for rec in basic_recommendations:
                # Add advanced metrics if available
                if "keyword" in rec:
                    keyword = rec["keyword"]
                    score_data = keyword_scores.get(keyword, {})
                    
                    # Add search volume and keyword difficulty
                    rec["search_volume"] = serp_data.get("search_volume", {}).get(keyword)
                    rec["keyword_difficulty"] = serp_data.get("keyword_difficulty", {}).get(keyword)
                    
                    # Add intent classification
                    rec["intent"] = intent_classification.get(keyword, "unknown")
                    
                    # Add related PAA questions
                    for kw, questions in paa_questions.items():
                        if keyword.lower() in kw.lower() or kw.lower() in keyword.lower():
                            rec["related_questions"] = questions[:3]  # Limit to top 3
                            break
                            
                enhanced_recommendations.append(rec)
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error enhancing keyword recommendations: {str(e)}", exc_info=True)
            return basic_recommendations

    def _generate_keyword_recommendations_basic(self, keyword_analysis, serp_data):
        """Basic keyword recommendation generation (fallback method)"""
        recommendations = []
        
        # Extract keyword scores
        keyword_scores = keyword_analysis.get("keyword_scores", {})
        
        # Sort keywords by score
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1].get("score", 0), reverse=True)
        
        # Add top scoring keywords
        for keyword, score_data in sorted_keywords[:5]:
            recommendations.append({
                "keyword": keyword,
                "score": score_data.get("score", 0),
                "opportunity": score_data.get("opportunity", 0),
                "difficulty": score_data.get("difficulty", 0),
                "type": "high_opportunity"
            })
            
        return recommendations

    async def _generate_basic_insights(self, input_data, keyword_analysis, serp_data, competitor_data):
        """Generate basic insights as a fallback when enhanced generation fails"""
        logger.info("Generating basic insights as fallback")
        
        insights = {
            "content_opportunities": [],
            "serp_feature_insights": [],
            "competitive_landscape_summary": {},
            "keyword_recommendations": [],
            "topic_clusters": keyword_analysis.get("clusters", []),
            "intent_distribution": self._calculate_intent_distribution_from_dict(keyword_analysis.get("intent_classification", {})),
            "content_blueprints": {},
            "summary": {"overall_summary": "Basic insights generated due to error in enhanced generation.", "key_opportunities_highlight": []}
        }
        
        # Add basic keyword recommendations
        insights["keyword_recommendations"] = self._generate_keyword_recommendations_basic(keyword_analysis, serp_data)
        
        # Add basic SERP feature insights
        insights["serp_feature_insights"] = self._generate_serp_feature_insights_basic(serp_data)
        
        return insights

    def _calculate_intent_distribution_from_dict(self, intent_classification):
        """Calculate intent distribution from intent classification dictionary"""
        intent_counts = {}
        
        for keyword, intent in intent_classification.items():
            if intent not in intent_counts:
                intent_counts[intent] = 0
            intent_counts[intent] += 1
            
        total = sum(intent_counts.values()) if intent_counts else 0
        
        if total > 0:
            return {intent: (count / total) * 100 for intent, count in intent_counts.items()}
        else:
            return {}

    def _generate_serp_feature_insights_basic(self, serp_data):
        """Generate basic SERP feature insights as a fallback"""
        insights = []
        
        if not serp_data:
            return insights
            
        # Extract unique features across all keywords
        all_features = set()
        for features in serp_data.get("features", {}).values():
            if isinstance(features, list):
                all_features.update(features)
                
        # Create basic insight for each feature
        for feature in all_features:
            insights.append({
                "feature": feature,
                "description": f"This SERP contains the {feature} feature.",
                "strategy": f"Optimize content to target the {feature} feature."
            })
            
        return insights
