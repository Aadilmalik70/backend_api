# Filename: src/modules/content_analyzer_enhanced.py
import asyncio
import os
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import statistics
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

logger = logging.getLogger("keyword_research.content_analyzer_enhanced")

# Enhanced models for deeper content analysis
class ReadabilityMetrics(BaseModel):
    """Detailed readability metrics for content."""
    flesch_kincaid_score: Optional[float] = Field(None, description="Flesch-Kincaid readability score (0-100, higher is easier to read).")
    flesch_kincaid_grade: Optional[float] = Field(None, description="Flesch-Kincaid grade level.")
    gunning_fog_index: Optional[float] = Field(None, description="Gunning Fog Index (years of education needed to understand).")
    smog_index: Optional[float] = Field(None, description="SMOG Index (years of education needed to understand).")
    automated_readability_index: Optional[float] = Field(None, description="Automated Readability Index.")
    coleman_liau_index: Optional[float] = Field(None, description="Coleman-Liau Index.")
    reading_time_minutes: Optional[float] = Field(None, description="Estimated reading time in minutes.")
    average_sentence_length: Optional[float] = Field(None, description="Average sentence length in words.")
    average_word_length: Optional[float] = Field(None, description="Average word length in characters.")
    complex_word_percentage: Optional[float] = Field(None, description="Percentage of complex words (3+ syllables).")

class ContentStructurePattern(BaseModel):
    """Content structure pattern identified in the content."""
    pattern_type: str = Field(..., description="Type of pattern (e.g., 'heading_structure', 'content_blocks', 'list_usage').")
    description: str = Field(..., description="Description of the pattern.")
    frequency: Optional[str] = Field(None, description="Frequency of the pattern in the content.")
    examples: List[str] = Field(default_factory=list, description="Examples of the pattern from the content.")

class ContentEngagementMetrics(BaseModel):
    """Engagement metrics extracted or estimated from the content."""
    estimated_engagement_score: Optional[int] = Field(None, description="Estimated engagement score (1-10).")
    call_to_action_count: Optional[int] = Field(None, description="Number of calls to action in the content.")
    call_to_action_types: List[str] = Field(default_factory=list, description="Types of calls to action found.")
    interactive_elements: List[str] = Field(default_factory=list, description="Interactive elements found in the content.")
    social_proof_elements: List[str] = Field(default_factory=list, description="Social proof elements found in the content.")
    engagement_factors: List[str] = Field(default_factory=list, description="Factors that may influence engagement.")

class EnhancedContentAnalysis(BaseModel):
    """Enhanced content analysis with deeper metrics."""
    url: str = Field(..., description="URL of the analyzed content.")
    title: str = Field(..., description="Title of the content.")
    content_type: str = Field(..., description="Type of content (e.g., blog post, guide, product page).")
    word_count: int = Field(..., description="Word count of the content.")
    publication_date: Optional[str] = Field(None, description="Publication or last updated date of the content.")
    readability_metrics: ReadabilityMetrics = Field(default_factory=ReadabilityMetrics, description="Detailed readability metrics.")
    content_structure_patterns: List[ContentStructurePattern] = Field(default_factory=list, description="Content structure patterns identified.")
    key_themes: List[str] = Field(default_factory=list, description="Key themes identified in the content.")
    headings: List[str] = Field(default_factory=list, description="Headings found in the content.")
    main_points_summary: str = Field(..., description="Summary of the main points in the content.")
    engagement_metrics: ContentEngagementMetrics = Field(default_factory=ContentEngagementMetrics, description="Engagement metrics.")
    media_types: List[str] = Field(default_factory=list, description="Types of media found in the content.")
    calls_to_action: List[str] = Field(default_factory=list, description="Calls to action found in the content.")
    content_gaps: List[str] = Field(default_factory=list, description="Potential content gaps identified.")
    unique_selling_points: List[str] = Field(default_factory=list, description="Unique selling points or differentiators.")

class ContentAnalyzerEnhanced:
    """
    Enhanced content analyzer with deeper analysis of readability, structure patterns, and engagement metrics.
    """
    
    def __init__(self):
        try:
            self.api_key = os.getenv("GOOGLE_API_KEY")
            self.model = "gemini-2.0-flash"
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=0.2  # Lower temperature for more consistent analysis
            )
            logger.info("ChatGoogleGenerativeAI (Gemini) initialized for ContentAnalyzerEnhanced")
            self.llm_available = True
            self.content_analysis_parser = JsonOutputParser(pydantic_object=EnhancedContentAnalysis)
        except Exception as e:
            logger.error(f"Error initializing ChatGoogleGenerativeAI in ContentAnalyzerEnhanced: {str(e)}")
            self.llm = None
            self.llm_available = False
            self.content_analysis_parser = None
    
    async def analyze_content(self, url, html_content, extracted_text):
        """
        Perform enhanced analysis of content with deeper metrics.
        
        Args:
            url (str): URL of the content
            html_content (str): Raw HTML content
            extracted_text (str): Extracted text content
            
        Returns:
            dict: Enhanced content analysis
        """
        logger.info(f"Performing enhanced content analysis for {url}")
        
        if not self.llm_available or not extracted_text:
            logger.warning(f"LLM not available or no extracted text for {url}")
            return None
            
        try:
            # Calculate basic metrics
            word_count = self._calculate_word_count(extracted_text)
            readability_metrics = self._calculate_readability_metrics(extracted_text)
            headings = self._extract_headings(html_content)
            media_types = self._identify_media_types(html_content)
            publication_date = self._extract_publication_date(html_content, extracted_text)
            calls_to_action = self._extract_calls_to_action(html_content, extracted_text)
            
            # Prepare context for LLM analysis
            context = {
                "url": url,
                "extracted_text_sample": extracted_text[:5000],  # Limit text sample for LLM
                "word_count": word_count,
                "readability_metrics": readability_metrics,
                "headings": headings,
                "media_types": media_types,
                "publication_date": publication_date,
                "calls_to_action": calls_to_action
            }
            
            # Use LLM for deeper analysis
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert content analyst specializing in SEO and content strategy. Your task is to analyze the provided content and extract detailed insights about its structure, themes, engagement factors, and potential gaps.

                Analyze the content to identify:
                1. The content type (blog post, guide, product page, etc.)
                2. Key themes and topics covered
                3. Content structure patterns (heading hierarchy, content blocks, list usage, etc.)
                4. Main points and arguments
                5. Engagement factors (calls to action, interactive elements, social proof, etc.)
                6. Potential content gaps or missing information
                7. Unique selling points or differentiators

                Use the provided metrics (word count, readability, headings, etc.) to inform your analysis.

                Return your analysis EXCLUSIVELY as a single, valid JSON object matching the EnhancedContentAnalysis Pydantic model schema. Ensure the JSON is perfectly formatted.
                {format_instructions}
                """),
                ("human", """Analyze the following content:
                Content Data: {context}
                """)]
            )
            
            chain = prompt_template | self.llm | self.content_analysis_parser
            
            # Use invoke with retry for reliability
            response = await self._invoke_with_retry(chain, {"context": json.dumps(context), "format_instructions": self.content_analysis_parser.get_format_instructions()})
            
            # Combine LLM analysis with calculated metrics
            analysis = response.dict()
            
            # Ensure readability metrics are included
            if not analysis.get("readability_metrics") or not isinstance(analysis.get("readability_metrics"), dict):
                analysis["readability_metrics"] = readability_metrics
                
            # Ensure word count is accurate
            analysis["word_count"] = word_count
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in enhanced content analysis for {url}: {str(e)}", exc_info=True)
            return None
    
    def _calculate_word_count(self, text):
        """Calculate word count from text."""
        if not text:
            return 0
        return len(text.split())
    
    def _calculate_readability_metrics(self, text):
        """Calculate detailed readability metrics."""
        if not text:
            return {}
            
        try:
            # Split text into sentences and words
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            words = text.split()
            
            # Calculate basic metrics
            word_count = len(words)
            sentence_count = len(sentences)
            
            if sentence_count == 0 or word_count == 0:
                return {}
                
            # Calculate average sentence length
            avg_sentence_length = word_count / sentence_count
            
            # Calculate average word length
            avg_word_length = sum(len(word) for word in words) / word_count
            
            # Estimate syllable count (simplified)
            def count_syllables(word):
                word = word.lower()
                if len(word) <= 3:
                    return 1
                count = 0
                vowels = "aeiouy"
                if word[0] in vowels:
                    count += 1
                for i in range(1, len(word)):
                    if word[i] in vowels and word[i-1] not in vowels:
                        count += 1
                if word.endswith("e"):
                    count -= 1
                if count == 0:
                    count = 1
                return count
                
            syllable_count = sum(count_syllables(word) for word in words)
            
            # Calculate complex words (3+ syllables)
            complex_words = [word for word in words if count_syllables(word) >= 3]
            complex_word_count = len(complex_words)
            complex_word_percentage = (complex_word_count / word_count) * 100 if word_count > 0 else 0
            
            # Calculate Flesch-Kincaid Reading Ease
            flesch_kincaid_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (syllable_count / word_count))
            
            # Calculate Flesch-Kincaid Grade Level
            flesch_kincaid_grade = 0.39 * avg_sentence_length + 11.8 * (syllable_count / word_count) - 15.59
            
            # Calculate Gunning Fog Index
            gunning_fog_index = 0.4 * (avg_sentence_length + complex_word_percentage)
            
            # Calculate SMOG Index (simplified)
            smog_index = 1.043 * ((complex_word_count * (30 / sentence_count)) ** 0.5) + 3.1291
            
            # Calculate Automated Readability Index
            automated_readability_index = 4.71 * avg_word_length + 0.5 * avg_sentence_length - 21.43
            
            # Calculate Coleman-Liau Index
            l = (avg_word_length * 100) / word_count
            s = (sentence_count * 100) / word_count
            coleman_liau_index = 0.0588 * l - 0.296 * s - 15.8
            
            # Calculate reading time (assuming 200-250 words per minute)
            reading_time_minutes = word_count / 225
            
            return {
                "flesch_kincaid_score": round(flesch_kincaid_score, 2),
                "flesch_kincaid_grade": round(flesch_kincaid_grade, 2),
                "gunning_fog_index": round(gunning_fog_index, 2),
                "smog_index": round(smog_index, 2),
                "automated_readability_index": round(automated_readability_index, 2),
                "coleman_liau_index": round(coleman_liau_index, 2),
                "reading_time_minutes": round(reading_time_minutes, 2),
                "average_sentence_length": round(avg_sentence_length, 2),
                "average_word_length": round(avg_word_length, 2),
                "complex_word_percentage": round(complex_word_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating readability metrics: {str(e)}", exc_info=True)
            return {}
    
    def _extract_headings(self, html_content):
        """Extract headings from HTML content."""
        if not html_content:
            return []
            
        try:
            # Simple regex to extract headings
            heading_pattern = re.compile(r'<h([1-6])[^>]*>(.*?)</h\1>', re.DOTALL | re.IGNORECASE)
            headings = []
            
            for match in heading_pattern.finditer(html_content):
                heading_level = match.group(1)
                heading_text = match.group(2)
                
                # Clean heading text (remove HTML tags)
                clean_heading = re.sub(r'<[^>]+>', '', heading_text).strip()
                if clean_heading:
                    headings.append(clean_heading)
                    
            return headings
            
        except Exception as e:
            logger.error(f"Error extracting headings: {str(e)}", exc_info=True)
            return []
    
    def _identify_media_types(self, html_content):
        """Identify types of media in the content."""
        if not html_content:
            return []
            
        media_types = []
        
        try:
            # Check for images
            if re.search(r'<img[^>]+>', html_content, re.IGNORECASE):
                media_types.append("images")
                
            # Check for videos
            if re.search(r'<video[^>]*>|<iframe[^>]*(youtube|vimeo|wistia)[^>]*>', html_content, re.IGNORECASE):
                media_types.append("videos")
                
            # Check for audio
            if re.search(r'<audio[^>]*>', html_content, re.IGNORECASE):
                media_types.append("audio")
                
            # Check for tables
            if re.search(r'<table[^>]*>', html_content, re.IGNORECASE):
                media_types.append("tables")
                
            # Check for infographics (approximation)
            if re.search(r'<img[^>]*(infographic|diagram|chart)[^>]*>', html_content, re.IGNORECASE):
                media_types.append("infographics")
                
            # Check for interactive elements
            if re.search(r'<(button|input|select|textarea)[^>]*>', html_content, re.IGNORECASE):
                media_types.append("interactive_elements")
                
            return media_types
            
        except Exception as e:
            logger.error(f"Error identifying media types: {str(e)}", exc_info=True)
            return []
    
    def _extract_publication_date(self, html_content, text_content):
        """Extract publication or last updated date."""
        if not html_content:
            return None
            
        try:
            # Look for common date patterns in meta tags
            meta_date_pattern = re.compile(r'<meta[^>]*(published_time|modified_time|date|pubdate)[^>]*content=["\']([^"\']+)["\']', re.IGNORECASE)
            meta_match = meta_date_pattern.search(html_content)
            
            if meta_match:
                return meta_match.group(2)
                
            # Look for schema.org date patterns
            schema_date_pattern = re.compile(r'(datePublished|dateModified)["\']?\s*:\s*["\']([^"\']+)["\']', re.IGNORECASE)
            schema_match = schema_date_pattern.search(html_content)
            
            if schema_match:
                return schema_match.group(2)
                
            # Look for common date patterns in text
            text_date_patterns = [
                r'(published|posted|updated)(\s+on)?\s+([A-Z][a-z]+ \d{1,2},? \d{4})',
                r'(published|posted|updated)(\s+on)?\s+(\d{1,2}/\d{1,2}/\d{2,4})',
                r'(published|posted|updated)(\s+on)?\s+(\d{1,2}-\d{1,2}-\d{2,4})'
            ]
            
            for pattern in text_date_patterns:
                date_match = re.search(pattern, text_content, re.IGNORECASE)
                if date_match:
                    return date_match.group(3)
                    
            return None
            
        except Exception as e:
            logger.error(f"Error extracting publication date: {str(e)}", exc_info=True)
            return None
    
    def _extract_calls_to_action(self, html_content, text_content):
        """Extract calls to action from content."""
        if not html_content:
            return []
            
        ctas = []
        
        try:
            # Look for button CTAs
            button_pattern = re.compile(r'<button[^>]*>(.*?)</button>', re.DOTALL | re.IGNORECASE)
            for match in button_pattern.finditer(html_content):
                button_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if button_text:
                    ctas.append(button_text)
                    
            # Look for link CTAs
            link_cta_patterns = [
                r'<a[^>]*(btn|button|cta)[^>]*>(.*?)</a>',
                r'<a[^>]*>(.*?(sign up|subscribe|download|get started|learn more|buy now|shop now|contact us|request|try|join).*?)</a>'
            ]
            
            for pattern in link_cta_patterns:
                link_pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                for match in link_pattern.finditer(html_content):
                    link_text = re.sub(r'<[^>]+>', '', match.group(2) if pattern.count('(') > 1 else match.group(1)).strip()
                    if link_text and len(link_text) < 50:  # Avoid capturing entire paragraphs
                        ctas.append(link_text)
                        
            # Look for form CTAs
            form_pattern = re.compile(r'<input[^>]*type=["\']submit["\'][^>]*value=["\']([^"\']+)["\']', re.IGNORECASE)
            for match in form_pattern.finditer(html_content):
                ctas.append(match.group(1))
                
            # Look for text CTAs
            text_cta_patterns = [
                r'(sign up|subscribe|download|get started|learn more|buy now|shop now|contact us|request|try|join)(\s+now|\s+today|\s+for\s+free)?',
                r'(click|tap)(\s+here|\s+below|\s+now)(\s+to\s+[a-z]+)?'
            ]
            
            for pattern in text_cta_patterns:
                text_pattern = re.compile(pattern, re.IGNORECASE)
                for match in text_pattern.finditer(text_content):
                    full_match = match.group(0)
                    if full_match:
                        ctas.append(full_match)
                        
            # Remove duplicates and limit to reasonable number
            unique_ctas = list(set(ctas))
            return unique_ctas[:10]  # Limit to top 10 CTAs
            
        except Exception as e:
            logger.error(f"Error extracting calls to action: {str(e)}", exc_info=True)
            return []
    
    async def _invoke_with_retry(self, chain, payload, retries=3, delay=2):
        """Invoke LLM with retry logic."""
        for attempt in range(retries):
            try:
                if asyncio.iscoroutinefunction(chain.invoke):
                    return await chain.invoke(payload)
                else:
                    return chain.invoke(payload)
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"LLM invoke error (attempt {attempt+1}/{retries}): {str(e)}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"LLM invoke failed after {retries} attempts: {str(e)}")
                    raise
    
    async def analyze_competitor_content_structure(self, content_analyses):
        """
        Analyze content structure patterns across multiple competitor content pieces.
        
        Args:
            content_analyses (dict): Dictionary of URL to content analysis
            
        Returns:
            dict: Structure pattern analysis
        """
        if not content_analyses:
            return {}
            
        try:
            # Extract headings from all content
            all_headings = {}
            for url, analysis in content_analyses.items():
                if analysis and "headings" in analysis:
                    all_headings[url] = analysis.get("headings", [])
                    
            # Analyze heading structures
            heading_structures = {}
            for url, headings in all_headings.items():
                if not headings:
                    continue
                    
                # Create a simplified representation of the heading structure
                structure = []
                for i, heading in enumerate(headings):
                    # Try to determine if it's H1, H2, H3 based on position and content
                    if i == 0:
                        level = "H1"
                    elif len(heading) < 30 and any(word in heading.lower() for word in ["how", "why", "what", "when", "where", "who"]):
                        level = "H2"
                    elif len(heading) < 20:
                        level = "H3"
                    else:
                        level = "H2"  # Default to H2
                        
                    structure.append(f"{level}: {heading}")
                    
                heading_structures[url] = structure
                
            # Identify common patterns
            patterns = []
            
            # Pattern 1: Question-based headings
            question_headings_count = 0
            question_heading_examples = []
            for url, headings in all_headings.items():
                for heading in headings:
                    if heading.endswith("?") or heading.lower().startswith(("how", "why", "what", "when", "where", "who")):
                        question_headings_count += 1
                        if len(question_heading_examples) < 3:
                            question_heading_examples.append(heading)
                            
            if question_headings_count > 0:
                patterns.append({
                    "pattern_type": "question_headings",
                    "description": "Headings phrased as questions to engage readers and address specific queries",
                    "frequency": f"Found in {question_headings_count} headings across all content",
                    "examples": question_heading_examples
                })
                
            # Pattern 2: Listicle format
            listicle_count = 0
            listicle_examples = []
            for url, headings in all_headings.items():
                for heading in headings:
                    if re.match(r'^\d+[\.\)]\s+', heading) or re.match(r'^(top|best)\s+\d+', heading.lower()):
                        listicle_count += 1
                        if len(listicle_examples) < 3:
                            listicle_examples.append(heading)
                            
            if listicle_count > 0:
                patterns.append({
                    "pattern_type": "listicle_format",
                    "description": "Content structured as a numbered list or 'Top X' format",
                    "frequency": f"Found in {listicle_count} headings across all content",
                    "examples": listicle_examples
                })
                
            # Pattern 3: How-to format
            howto_count = 0
            howto_examples = []
            for url, headings in all_headings.items():
                if headings and "how to" in headings[0].lower():
                    howto_count += 1
                    if len(howto_examples) < 3:
                        howto_examples.append(headings[0])
                        
            if howto_count > 0:
                patterns.append({
                    "pattern_type": "how_to_format",
                    "description": "Content structured as a step-by-step guide or tutorial",
                    "frequency": f"Found in {howto_count} content pieces",
                    "examples": howto_examples
                })
                
            # Pattern 4: Comparison format
            comparison_count = 0
            comparison_examples = []
            comparison_keywords = ["vs", "versus", "compared to", "comparison", "differences", "similarities"]
            for url, headings in all_headings.items():
                for heading in headings:
                    if any(keyword in heading.lower() for keyword in comparison_keywords):
                        comparison_count += 1
                        if len(comparison_examples) < 3:
                            comparison_examples.append(heading)
                            
            if comparison_count > 0:
                patterns.append({
                    "pattern_type": "comparison_format",
                    "description": "Content structured to compare different options or alternatives",
                    "frequency": f"Found in {comparison_count} headings across all content",
                    "examples": comparison_examples
                })
                
            return {
                "heading_structures": heading_structures,
                "content_structure_patterns": patterns
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitor content structure: {str(e)}", exc_info=True)
            return {}
    
    async def analyze_readability_trends(self, content_analyses):
        """
        Analyze readability trends across competitor content.
        
        Args:
            content_analyses (dict): Dictionary of URL to content analysis
            
        Returns:
            dict: Readability trend analysis
        """
        if not content_analyses:
            return {}
            
        try:
            # Extract readability metrics from all content
            readability_scores = {}
            grade_levels = {}
            reading_times = {}
            sentence_lengths = {}
            word_lengths = {}
            
            for url, analysis in content_analyses.items():
                if not analysis or "readability_metrics" not in analysis:
                    continue
                    
                metrics = analysis.get("readability_metrics", {})
                
                if "flesch_kincaid_score" in metrics:
                    readability_scores[url] = metrics["flesch_kincaid_score"]
                    
                if "flesch_kincaid_grade" in metrics:
                    grade_levels[url] = metrics["flesch_kincaid_grade"]
                    
                if "reading_time_minutes" in metrics:
                    reading_times[url] = metrics["reading_time_minutes"]
                    
                if "average_sentence_length" in metrics:
                    sentence_lengths[url] = metrics["average_sentence_length"]
                    
                if "average_word_length" in metrics:
                    word_lengths[url] = metrics["average_word_length"]
                    
            # Calculate averages and ranges
            avg_readability = statistics.mean(readability_scores.values()) if readability_scores else None
            avg_grade_level = statistics.mean(grade_levels.values()) if grade_levels else None
            avg_reading_time = statistics.mean(reading_times.values()) if reading_times else None
            avg_sentence_length = statistics.mean(sentence_lengths.values()) if sentence_lengths else None
            avg_word_length = statistics.mean(word_lengths.values()) if word_lengths else None
            
            # Determine readability level category
            readability_category = "Unknown"
            if avg_readability is not None:
                if avg_readability >= 90:
                    readability_category = "Very Easy"
                elif avg_readability >= 80:
                    readability_category = "Easy"
                elif avg_readability >= 70:
                    readability_category = "Fairly Easy"
                elif avg_readability >= 60:
                    readability_category = "Standard"
                elif avg_readability >= 50:
                    readability_category = "Fairly Difficult"
                elif avg_readability >= 30:
                    readability_category = "Difficult"
                else:
                    readability_category = "Very Difficult"
                    
            return {
                "average_readability_score": round(avg_readability, 2) if avg_readability is not None else None,
                "average_grade_level": round(avg_grade_level, 2) if avg_grade_level is not None else None,
                "average_reading_time_minutes": round(avg_reading_time, 2) if avg_reading_time is not None else None,
                "average_sentence_length": round(avg_sentence_length, 2) if avg_sentence_length is not None else None,
                "average_word_length": round(avg_word_length, 2) if avg_word_length is not None else None,
                "readability_category": readability_category,
                "readability_recommendation": self._generate_readability_recommendation(avg_readability, avg_grade_level)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing readability trends: {str(e)}", exc_info=True)
            return {}
    
    def _generate_readability_recommendation(self, readability_score, grade_level):
        """Generate readability recommendation based on competitor averages."""
        if readability_score is None or grade_level is None:
            return "Insufficient data to generate readability recommendation."
            
        recommendation = f"Competitor content has an average readability score of {round(readability_score, 2)} "
        recommendation += f"(grade level {round(grade_level, 1)}). "
        
        if readability_score >= 70:
            recommendation += "Content is relatively easy to read. Consider maintaining this accessible style while ensuring depth of information."
        elif readability_score >= 50:
            recommendation += "Content has moderate complexity. This balance of readability and sophistication appears to work well for this topic."
        else:
            recommendation += "Content is relatively complex. Consider whether simplifying language would better serve your audience, or if this complexity is necessary for the subject matter."
            
        return recommendation
