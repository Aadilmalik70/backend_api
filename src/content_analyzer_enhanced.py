import os
import json
import random
import re
from datetime import datetime

class ContentAnalyzer:
    """
    Enhanced class for analyzing SERP data and competitor content to extract insights.
    """
    
    def __init__(self):
        """Initialize the ContentAnalyzer with default settings."""
        self.readability_metrics = [
            "Flesch Reading Ease",
            "Flesch-Kincaid Grade Level",
            "Gunning Fog Index",
            "SMOG Index",
            "Coleman-Liau Index",
            "Automated Readability Index"
        ]
        
        self.content_structure_elements = [
            "Title",
            "Meta Description",
            "H1",
            "H2",
            "H3",
            "H4",
            "Paragraphs",
            "Lists",
            "Images",
            "Videos",
            "Tables",
            "Internal Links",
            "External Links",
            "Schema Markup"
        ]
        
        self.engagement_metrics = [
            "Estimated Word Count",
            "Content Depth Score",
            "Multimedia Richness",
            "Interactive Elements",
            "Social Sharing",
            "Comments/Discussion",
            "Updated Frequency"
        ]
    
    def analyze_serp(self, query, domain=None):
        """
        Analyze SERP data for a given query.
        
        Args:
            query (str): The search query to analyze
            domain (str, optional): Domain to check for in SERP results
            
        Returns:
            dict: SERP analysis data
        """
        # In a real implementation, this would fetch and analyze actual SERP data
        # For now, we'll generate mock SERP data
        
        # Generate 10 mock SERP results
        results = []
        for i in range(10):
            position = i + 1
            is_own_domain = domain and random.random() < 0.2  # 20% chance of own domain if provided
            
            result = {
                "position": position,
                "title": f"{'Your ' if is_own_domain else ''}Result {position}: {query.title()} Guide",
                "url": f"https://{'your-domain' if is_own_domain else f'competitor-{position}'}.com/{self._slugify(query)}",
                "description": f"{'Your ' if is_own_domain else ''}Comprehensive guide to {query.lower()}. Learn about the best practices, strategies, and tools.",
                "is_own_domain": is_own_domain
            }
            
            results.append(result)
        
        # Generate mock SERP features
        serp_features = self._generate_mock_serp_features(query)
        
        # Compile SERP data
        serp_data = {
            "query": query,
            "results": results,
            "features": serp_features,
            "own_domain_positions": [r["position"] for r in results if r.get("is_own_domain", False)],
            "timestamp": datetime.now().isoformat()
        }
        
        return serp_data
    
    def analyze_competitors(self, serp_data):
        """
        Analyze competitor content based on SERP data.
        
        Args:
            serp_data (dict): SERP analysis data
            
        Returns:
            dict: Competitor analysis data
        """
        # In a real implementation, this would fetch and analyze actual competitor content
        # For now, we'll generate mock competitor analysis data
        
        # Extract competitor URLs from SERP data
        competitor_urls = [
            result["url"] for result in serp_data.get("results", [])
            if not result.get("is_own_domain", False)
        ][:5]  # Analyze top 5 competitors
        
        # Generate mock competitor analysis for each URL
        competitor_analyses = {}
        for url in competitor_urls:
            competitor_analyses[url] = self._generate_mock_competitor_analysis(url, serp_data["query"])
        
        # Compile competitor data
        competitor_data = {
            "query": serp_data["query"],
            "competitor_analyses": competitor_analyses,
            "common_topics": self._generate_mock_common_topics(serp_data["query"]),
            "content_gaps": self._generate_mock_content_gaps(serp_data["query"]),
            "timestamp": datetime.now().isoformat()
        }
        
        return competitor_data
    
    def analyze_url(self, url):
        """
        Analyze content from a specific URL.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            dict: Content analysis data
        """
        # In a real implementation, this would fetch and analyze actual content
        # For now, we'll generate mock content analysis data
        
        # Extract domain and path for more realistic mock data
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        domain = domain_match.group(1) if domain_match else "example.com"
        
        path_match = re.search(r'https?://(?:www\.)?[^/]+(/.*)', url)
        path = path_match.group(1) if path_match else "/"
        
        # Generate topic from path
        topic = path.replace("-", " ").replace("/", " ").strip()
        if not topic:
            topic = "Content Strategy"
        
        # Generate mock content analysis
        analysis = {
            "url": url,
            "domain": domain,
            "title": f"{topic.title()} - {domain}",
            "meta_description": f"Learn about {topic.lower()} with our comprehensive guide. Discover strategies, tips, and best practices.",
            "word_count": random.randint(1200, 5000),
            "readability": self._generate_mock_readability_scores(),
            "content_structure": self._generate_mock_content_structure(),
            "keyword_usage": self._generate_mock_keyword_usage(topic),
            "topics_covered": self._generate_mock_topics_covered(topic),
            "engagement_metrics": self._generate_mock_engagement_metrics(),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
    
    def _slugify(self, text):
        """Convert text to URL-friendly slug."""
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove non-alphanumeric characters
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Remove duplicate hyphens
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    def _generate_mock_serp_features(self, query):
        """Generate mock SERP features based on query."""
        features = {}
        
        # Featured snippet (50% chance)
        if random.random() < 0.5:
            features["featured_snippet"] = {
                "type": random.choice(["paragraph", "list", "table"]),
                "content": f"A featured snippet about {query.lower()}.",
                "source_url": f"https://example.com/{self._slugify(query)}"
            }
        
        # People also ask (70% chance)
        if random.random() < 0.7:
            features["people_also_ask"] = [
                f"What is {query}?",
                f"How does {query} work?",
                f"Why is {query} important?",
                f"What are the benefits of {query}?"
            ]
        
        # Knowledge panel (30% chance)
        if random.random() < 0.3:
            features["knowledge_panel"] = {
                "title": query.title(),
                "description": f"Information about {query.lower()}.",
                "attributes": {
                    "Type": random.choice(["Strategy", "Methodology", "Concept", "Tool"]),
                    "Related to": random.choice(["SEO", "Content Marketing", "Digital Marketing", "Web Development"])
                }
            }
        
        # Image pack (40% chance)
        if random.random() < 0.4:
            features["image_pack"] = {
                "present": True,
                "position": random.randint(1, 5)
            }
        
        # Video results (35% chance)
        if random.random() < 0.35:
            features["video_results"] = {
                "present": True,
                "position": random.randint(1, 5)
            }
        
        # Local pack (20% chance)
        if random.random() < 0.2:
            features["local_pack"] = {
                "present": True,
                "position": random.randint(1, 3)
            }
        
        # Top stories (25% chance)
        if random.random() < 0.25:
            features["top_stories"] = {
                "present": True,
                "position": random.randint(1, 3)
            }
        
        return features
    
    def _generate_mock_competitor_analysis(self, url, query):
        """Generate mock competitor analysis for a URL."""
        # Extract domain for more realistic mock data
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        domain = domain_match.group(1) if domain_match else "competitor.com"
        
        return {
            "url": url,
            "domain": domain,
            "title": f"{query.title()} Guide - {domain}",
            "word_count": random.randint(1200, 5000),
            "readability": self._generate_mock_readability_scores(),
            "content_structure": self._generate_mock_content_structure(),
            "keyword_usage": self._generate_mock_keyword_usage(query),
            "topics_covered": self._generate_mock_topics_covered(query),
            "engagement_metrics": self._generate_mock_engagement_metrics(),
            "strengths": self._generate_mock_strengths(),
            "weaknesses": self._generate_mock_weaknesses()
        }
    
    def _generate_mock_readability_scores(self):
        """Generate mock readability scores."""
        return {
            "Flesch Reading Ease": round(random.uniform(50, 70), 1),
            "Flesch-Kincaid Grade Level": round(random.uniform(7, 12), 1),
            "Gunning Fog Index": round(random.uniform(10, 15), 1),
            "SMOG Index": round(random.uniform(8, 13), 1),
            "Coleman-Liau Index": round(random.uniform(9, 14), 1),
            "Automated Readability Index": round(random.uniform(9, 14), 1),
            "overall_readability": random.choice(["Easy", "Moderate", "Difficult"])
        }
    
    def _generate_mock_content_structure(self):
        """Generate mock content structure analysis."""
        return {
            "title_length": random.randint(30, 70),
            "meta_description_length": random.randint(120, 160),
            "h1_count": random.randint(1, 2),
            "h2_count": random.randint(3, 8),
            "h3_count": random.randint(5, 15),
            "h4_count": random.randint(0, 10),
            "paragraph_count": random.randint(15, 40),
            "list_count": random.randint(2, 8),
            "image_count": random.randint(2, 10),
            "video_count": random.randint(0, 3),
            "table_count": random.randint(0, 3),
            "internal_link_count": random.randint(5, 20),
            "external_link_count": random.randint(3, 15),
            "schema_markup_types": random.sample(["Article", "FAQPage", "HowTo", "Product", "Review"], random.randint(0, 3))
        }
    
    def _generate_mock_keyword_usage(self, topic):
        """Generate mock keyword usage analysis."""
        # Generate primary and secondary keywords based on topic
        words = re.findall(r'\w+', topic.lower())
        primary_keyword = topic.lower()
        
        secondary_keywords = []
        for word in words:
            if len(word) > 3:  # Only use meaningful words
                secondary_keywords.append(f"{word} strategy")
                secondary_keywords.append(f"{word} techniques")
                secondary_keywords.append(f"{word} best practices")
        
        # Ensure we have at least some secondary keywords
        if not secondary_keywords:
            secondary_keywords = [
                "content strategy",
                "content optimization",
                "SEO techniques",
                "keyword research",
                "content marketing"
            ]
        
        # Select a random subset of secondary keywords
        secondary_keywords = random.sample(secondary_keywords, min(5, len(secondary_keywords)))
        
        # Generate usage data
        keyword_usage = {
            "primary_keyword": {
                "keyword": primary_keyword,
                "count": random.randint(5, 15),
                "density": round(random.uniform(0.5, 2.5), 1),
                "in_title": random.choice([True, False]),
                "in_meta_description": random.choice([True, False]),
                "in_h1": random.choice([True, False]),
                "in_h2": random.choice([True, True, False]),  # 2/3 chance of True
                "in_url": random.choice([True, True, False])  # 2/3 chance of True
            },
            "secondary_keywords": {}
        }
        
        for keyword in secondary_keywords:
            keyword_usage["secondary_keywords"][keyword] = {
                "count": random.randint(2, 8),
                "density": round(random.uniform(0.2, 1.5), 1),
                "in_headings": random.choice([True, False])
            }
        
        return keyword_usage
    
    def _generate_mock_topics_covered(self, main_topic):
        """Generate mock topics covered in the content."""
        # Base topics on the main topic
        base_topics = [
            f"{main_topic} basics",
            f"{main_topic} strategies",
            f"{main_topic} best practices",
            f"{main_topic} tools",
            f"{main_topic} examples",
            f"{main_topic} metrics",
            f"{main_topic} challenges",
            f"{main_topic} future trends"
        ]
        
        # Select a random subset of topics
        num_topics = random.randint(4, 8)
        selected_topics = random.sample(base_topics, min(num_topics, len(base_topics)))
        
        # Generate coverage score for each topic
        topics_covered = {}
        for topic in selected_topics:
            topics_covered[topic] = {
                "coverage_score": random.randint(1, 5),  # 1-5 scale
                "word_count": random.randint(100, 800)
            }
        
        return topics_covered
    
    def _generate_mock_engagement_metrics(self):
        """Generate mock engagement metrics."""
        return {
            "estimated_word_count": random.randint(1200, 5000),
            "content_depth_score": random.randint(1, 10),  # 1-10 scale
            "multimedia_richness": random.randint(1, 10),  # 1-10 scale
            "interactive_elements": random.randint(0, 5),
            "social_sharing_buttons": random.choice([True, False]),
            "comments_enabled": random.choice([True, False]),
            "last_updated": (datetime.now().replace(
                day=random.randint(1, 28),
                month=random.randint(1, 12),
                year=random.randint(2023, 2025)
            )).isoformat()
        }
    
    def _generate_mock_strengths(self):
        """Generate mock content strengths."""
        all_strengths = [
            "Comprehensive topic coverage",
            "Well-structured content with clear headings",
            "Excellent use of multimedia elements",
            "Strong keyword optimization without over-optimization",
            "Good balance of internal and external links",
            "Effective use of lists and tables for scannable content",
            "Clear and concise writing style",
            "Appropriate reading level for target audience",
            "Strong meta description with clear value proposition",
            "Effective use of schema markup",
            "Recent content updates",
            "Good coverage of related topics",
            "Effective use of examples and case studies",
            "Strong call-to-action elements",
            "Good mobile optimization"
        ]
        
        # Select 3-5 random strengths
        num_strengths = random.randint(3, 5)
        return random.sample(all_strengths, num_strengths)
    
    def _generate_mock_weaknesses(self):
        """Generate mock content weaknesses."""
        all_weaknesses = [
            "Limited depth on some key subtopics",
            "Missing or incomplete schema markup",
            "Keyword density too low for some secondary terms",
            "Limited use of multimedia content",
            "Content may be too technical for general audience",
            "Older content without recent updates",
            "Limited internal linking to related content",
            "Missing FAQ section for featured snippet opportunities",
            "Weak meta description that doesn't encourage clicks",
            "Missing or weak call-to-action elements",
            "Limited coverage of emerging trends",
            "Too few headings for content length",
            "Limited use of data and statistics",
            "Missing comparison tables for related concepts",
            "Poor mobile optimization"
        ]
        
        # Select 2-4 random weaknesses
        num_weaknesses = random.randint(2, 4)
        return random.sample(all_weaknesses, num_weaknesses)
    
    def _generate_mock_common_topics(self, query):
        """Generate mock common topics covered by competitors."""
        # Base topics on the query
        base_topics = [
            f"{query} overview",
            f"{query} benefits",
            f"{query} implementation",
            f"{query} best practices",
            f"{query} tools",
            f"{query} examples",
            f"{query} case studies",
            f"{query} metrics",
            f"{query} challenges",
            f"{query} vs traditional approaches",
            f"{query} future trends"
        ]
        
        # Select a random subset of topics
        num_topics = random.randint(5, 9)
        selected_topics = random.sample(base_topics, min(num_topics, len(base_topics)))
        
        # Generate coverage data for each topic
        common_topics = {}
        for topic in selected_topics:
            common_topics[topic] = {
                "coverage_percentage": random.randint(40, 100),  # % of competitors covering this
                "average_depth": random.randint(1, 5)  # 1-5 scale
            }
        
        return common_topics
    
    def _generate_mock_content_gaps(self, query):
        """Generate mock content gaps not covered well by competitors."""
        # Base gaps on the query
        base_gaps = [
            f"{query} for beginners",
            f"Advanced {query} techniques",
            f"{query} ROI calculation",
            f"{query} failure cases",
            f"Integrating {query} with existing systems",
            f"{query} compliance and regulations",
            f"{query} for specific industries",
            f"Budget-friendly {query} approaches",
            f"DIY {query} methods",
            f"{query} automation",
            f"International aspects of {query}",
            f"{query} training and skill development"
        ]
        
        # Select a random subset of gaps
        num_gaps = random.randint(3, 6)
        selected_gaps = random.sample(base_gaps, min(num_gaps, len(base_gaps)))
        
        # Generate opportunity data for each gap
        content_gaps = {}
        for gap in selected_gaps:
            content_gaps[gap] = {
                "coverage_percentage": random.randint(0, 30),  # % of competitors covering this
                "opportunity_score": random.randint(7, 10),  # 1-10 scale
                "search_volume_estimate": random.choice(["Low", "Medium", "High"])
            }
        
        return content_gaps
