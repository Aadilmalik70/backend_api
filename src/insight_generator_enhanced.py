import os
import json
import random
import re
from datetime import datetime

class InsightGenerator:
    """
    Enhanced class for generating content insights and blueprints based on
    keyword data, SERP analysis, and competitor analysis.
    """
    
    def __init__(self):
        """Initialize the InsightGenerator with default settings."""
        self.section_templates = [
            "Introduction to {topic}",
            "Understanding {topic}",
            "The Importance of {topic}",
            "Key Benefits of {topic}",
            "How to Implement {topic}",
            "Best Practices for {topic}",
            "Common Challenges with {topic}",
            "Advanced Strategies for {topic}",
            "Case Studies: {topic} in Action",
            "Future Trends in {topic}",
            "Tools and Resources for {topic}",
            "Measuring Success with {topic}",
            "{topic} vs. Traditional Approaches",
            "Expert Insights on {topic}",
            "Step-by-Step Guide to {topic}"
        ]
        
        self.subsection_templates = [
            "What is {subtopic}?",
            "Why {subtopic} Matters",
            "Key Components of {subtopic}",
            "How to Optimize {subtopic}",
            "Common Mistakes in {subtopic}",
            "Best Tools for {subtopic}",
            "Measuring {subtopic} Performance",
            "Expert Tips for {subtopic}",
            "Case Study: {subtopic}",
            "Future of {subtopic}",
            "Comparing {subtopic} Approaches",
            "Step-by-Step {subtopic} Implementation",
            "Frequently Asked Questions About {subtopic}",
            "Resources for Learning {subtopic}",
            "Key Metrics for {subtopic}"
        ]
    
    def generate_content_blueprint(self, input_text, keyword_data, competitor_data):
        """
        Generate a comprehensive content blueprint based on input and analysis data.
        
        Args:
            input_text (str): The original user input text
            keyword_data (dict): Keyword analysis data
            competitor_data (dict): Competitor analysis data
            
        Returns:
            dict: Content blueprint with title, description, sections, and subsections
        """
        # Extract main topic from input
        main_topic = self._extract_main_topic(input_text)
        
        # Generate title and description
        title = self._generate_title(main_topic)
        description = self._generate_description(main_topic)
        
        # Generate sections based on keyword data and competitor analysis
        sections = self._generate_sections(main_topic, keyword_data, competitor_data)
        
        return {
            "title": title,
            "description": description,
            "sections": sections
        }
    
    def _extract_main_topic(self, input_text):
        """Extract the main topic from input text."""
        # In a real implementation, this would use NLP to extract the main topic
        # For now, we'll use a simple approach
        
        # Remove common filler words
        cleaned_text = re.sub(r'\b(the|a|an|and|or|for|to|in|on|with|about)\b', '', input_text, flags=re.IGNORECASE)
        
        # If the input contains "content strategy" or similar, use that as the main topic
        if re.search(r'content\s+strategy', input_text, re.IGNORECASE):
            return "Content Strategy"
        elif re.search(r'serp\s+dominance', input_text, re.IGNORECASE):
            return "SERP Dominance"
        elif re.search(r'ai\s+content', input_text, re.IGNORECASE):
            return "AI Content Strategy"
        
        # Default to a generic topic if no specific one is found
        return "AI Content Strategy for SERP Dominance"
    
    def _generate_title(self, main_topic):
        """Generate a compelling title based on the main topic."""
        title_templates = [
            "The Ultimate Guide to {topic}",
            "Mastering {topic}: A Comprehensive Guide",
            "{topic}: Strategies for Success",
            "How to Dominate with {topic}",
            "The Complete {topic} Playbook",
            "{topic} Mastery: From Beginner to Expert",
            "Advanced {topic} Techniques That Drive Results",
            "The Science of {topic}: Data-Driven Approaches",
            "Revolutionize Your Approach to {topic}",
            "{topic}: The Definitive Guide"
        ]
        
        return random.choice(title_templates).format(topic=main_topic)
    
    def _generate_description(self, main_topic):
        """Generate a compelling description based on the main topic."""
        description_templates = [
            "A comprehensive guide to leveraging {topic} for maximum impact and results.",
            "Learn how to implement {topic} strategies that drive measurable business outcomes.",
            "Discover proven techniques and best practices for {topic} that outperform the competition.",
            "Master the art and science of {topic} with this data-driven, actionable guide.",
            "Transform your approach to {topic} with expert insights and step-by-step instructions.",
            "Unlock the full potential of {topic} with strategies used by industry leaders.",
            "A deep dive into {topic} methodologies that deliver consistent, scalable results.",
            "Everything you need to know about {topic}, from fundamental concepts to advanced techniques.",
            "Elevate your {topic} game with cutting-edge strategies and practical implementation tips.",
            "The definitive resource for {topic}, backed by research and real-world case studies."
        ]
        
        return random.choice(description_templates).format(topic=main_topic)
    
    def _generate_sections(self, main_topic, keyword_data, competitor_data):
        """Generate content sections based on topic, keywords, and competitor data."""
        # In a real implementation, this would analyze keyword data and competitor content
        # to identify important topics and gaps
        
        # For now, we'll generate 5-7 sections with 2-3 subsections each
        num_sections = random.randint(5, 7)
        
        # Get keywords to use as subtopics
        keywords = list(keyword_data.get("keyword_scores", {}).keys())
        if not keywords:
            # Fallback subtopics if no keywords are available
            keywords = [
                "content optimization",
                "keyword research",
                "SERP features",
                "competitor analysis",
                "content structure",
                "semantic SEO",
                "user intent",
                "performance tracking"
            ]
        
        sections = []
        used_templates = set()
        
        for i in range(num_sections):
            # Select a section template that hasn't been used yet
            available_templates = [t for t in self.section_templates if t not in used_templates]
            if not available_templates:
                available_templates = self.section_templates
            
            section_template = random.choice(available_templates)
            used_templates.add(section_template)
            
            # Generate section title
            section_title = section_template.format(topic=main_topic)
            
            # Generate section content
            section_content = self._generate_section_content(section_title)
            
            # Generate subsections
            num_subsections = random.randint(2, 3)
            subsections = []
            
            for j in range(num_subsections):
                # Select a subtopic (keyword or related term)
                subtopic = random.choice(keywords) if keywords else f"aspect {j+1}"
                
                # Select a subsection template
                subsection_template = random.choice(self.subsection_templates)
                
                # Generate subsection title and content
                subsection_title = subsection_template.format(subtopic=subtopic.title())
                subsection_content = self._generate_subsection_content(subsection_title)
                
                subsections.append({
                    "title": subsection_title,
                    "content": subsection_content
                })
            
            sections.append({
                "title": section_title,
                "content": section_content,
                "subsections": subsections
            })
        
        return sections
    
    def _generate_section_content(self, section_title):
        """Generate content for a section based on its title."""
        # In a real implementation, this would generate more contextual content
        # For now, we'll use templates based on the section type
        
        if "introduction" in section_title.lower() or "understanding" in section_title.lower():
            return "This section provides a foundational understanding of the topic, key concepts, and why it matters in today's digital landscape."
        
        elif "importance" in section_title.lower() or "benefits" in section_title.lower():
            return "Explore the significant advantages and strategic benefits that come from implementing these approaches in your content strategy."
        
        elif "how to" in section_title.lower() or "guide" in section_title.lower() or "implement" in section_title.lower():
            return "A practical walkthrough of implementation steps, with actionable advice and real-world examples to guide your process."
        
        elif "best practices" in section_title.lower() or "strategies" in section_title.lower():
            return "Learn the proven techniques and approaches that consistently deliver superior results, based on industry research and expert insights."
        
        elif "challenges" in section_title.lower() or "mistakes" in section_title.lower():
            return "Identify common pitfalls and obstacles, with practical solutions to overcome them and optimize your results."
        
        elif "case studies" in section_title.lower() or "examples" in section_title.lower():
            return "Real-world examples and success stories that demonstrate effective implementation and measurable outcomes."
        
        elif "tools" in section_title.lower() or "resources" in section_title.lower():
            return "A curated collection of the most effective tools, platforms, and resources to enhance your strategy and streamline your workflow."
        
        elif "future" in section_title.lower() or "trends" in section_title.lower():
            return "Insights into emerging developments and future directions, helping you stay ahead of the curve and prepare for upcoming changes."
        
        elif "measuring" in section_title.lower() or "metrics" in section_title.lower():
            return "Framework for tracking performance and measuring success, with key metrics and KPIs to monitor progress and demonstrate ROI."
        
        else:
            return "This section explores key aspects and considerations for optimizing your approach and achieving superior results."
    
    def _generate_subsection_content(self, subsection_title):
        """Generate content for a subsection based on its title."""
        # In a real implementation, this would generate more contextual content
        # For now, we'll use templates based on the subsection type
        
        if "what is" in subsection_title.lower():
            return "A clear definition and explanation of the concept, its components, and its role in the broader strategy."
        
        elif "why" in subsection_title.lower() and "matters" in subsection_title.lower():
            return "The strategic importance and specific benefits this aspect brings to your overall approach and results."
        
        elif "key components" in subsection_title.lower() or "elements" in subsection_title.lower():
            return "A breakdown of the essential parts and how they work together to create an effective system."
        
        elif "how to" in subsection_title.lower() or "optimize" in subsection_title.lower():
            return "Step-by-step guidance for implementation or improvement, with practical tips and best practices."
        
        elif "common mistakes" in subsection_title.lower():
            return "Pitfalls to avoid and how to recognize when your approach needs adjustment to improve outcomes."
        
        elif "tools" in subsection_title.lower():
            return "Recommended software, platforms, and resources that can enhance your capabilities in this area."
        
        elif "measuring" in subsection_title.lower() or "metrics" in subsection_title.lower():
            return "Specific KPIs and measurement approaches to track progress and evaluate success in this area."
        
        elif "expert tips" in subsection_title.lower():
            return "Advanced insights and recommendations from industry leaders to take your strategy to the next level."
        
        elif "case study" in subsection_title.lower():
            return "A detailed example showing successful implementation and the specific approaches that led to positive outcomes."
        
        elif "future" in subsection_title.lower():
            return "Emerging trends and developments to watch, with predictions about how this aspect will evolve."
        
        elif "comparing" in subsection_title.lower():
            return "Analysis of different methodologies and approaches, with guidance on selecting the most appropriate for your needs."
        
        elif "step-by-step" in subsection_title.lower():
            return "A detailed walkthrough of the implementation process, breaking complex tasks into manageable actions."
        
        elif "frequently asked questions" in subsection_title.lower() or "faq" in subsection_title.lower():
            return "Answers to common questions and concerns, addressing typical points of confusion or uncertainty."
        
        else:
            return "Detailed information and guidance on this specific aspect to enhance your understanding and implementation."
