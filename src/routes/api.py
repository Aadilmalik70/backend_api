from flask import Blueprint, request, jsonify
import sys
import os
import json
from datetime import datetime

# Import enhanced modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from content_analyzer_enhanced import ContentAnalyzer
from insight_generator_enhanced import InsightGenerator
from keyword_processor_enhanced import KeywordProcessor
from serp_feature_optimizer import SerpFeatureOptimizer
from content_performance_predictor import ContentPerformancePredictor
from export_integration import ExportIntegration

api_bp = Blueprint('api', __name__)

# Initialize modules
content_analyzer = ContentAnalyzer()
insight_generator = InsightGenerator()
keyword_processor = KeywordProcessor()
serp_optimizer = SerpFeatureOptimizer()
performance_predictor = ContentPerformancePredictor()
export_integration = ExportIntegration()

@api_bp.route('/process', methods=['POST'])
def process_input():
    """Process user input and generate content strategy"""
    try:
        data = request.json
        input_text = data.get('input', '')
        domain = data.get('domain', '')
        
        if not input_text:
            return jsonify({"error": "Input text is required"}), 400
            
        # Process the input through all modules
        keyword_data = keyword_processor.process(input_text)
        serp_data = content_analyzer.analyze_serp(input_text, domain)
        competitor_data = content_analyzer.analyze_competitors(serp_data)
        
        # Generate content blueprint
        content_blueprint = insight_generator.generate_content_blueprint(
            input_text, 
            keyword_data, 
            competitor_data
        )
        
        # Generate SERP optimization recommendations
        optimization_recommendations = serp_optimizer.generate_recommendations(
            input_text,
            serp_data,
            competitor_data
        )
        
        # Generate performance prediction
        performance_prediction = performance_predictor.predict_performance(
            input_text,
            keyword_data,
            serp_data,
            competitor_data,
            content_blueprint
        )
        
        # Get available export formats and CMS platforms
        export_formats = export_integration.get_export_formats()
        cms_platforms = export_integration.get_cms_platforms()
        
        # Compile results
        results = {
            "content_blueprint": content_blueprint,
            "keyword_data": keyword_data,
            "optimization_recommendations": optimization_recommendations,
            "performance_prediction": performance_prediction,
            "export_formats": export_formats,
            "cms_platforms": cms_platforms,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error processing input: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze a specific URL for content insights"""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
            
        # Analyze the URL
        analysis = content_analyzer.analyze_url(url)
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"Error analyzing URL: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/export', methods=['POST'])
def export_content():
    """Export content in specified format"""
    try:
        data = request.json
        content_type = data.get('content_type', '')
        format_id = data.get('format', '')
        content_data = data.get('content_data', {})
        
        if not all([content_type, format_id, content_data]):
            return jsonify({"error": "Content type, format, and content data are required"}), 400
            
        # Export the content
        result = export_integration.export_content(content_type, format_id, content_data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error exporting content: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/publish', methods=['POST'])
def publish_to_cms():
    """Publish content to CMS platform"""
    try:
        data = request.json
        content_type = data.get('content_type', '')
        platform = data.get('platform', '')
        content_data = data.get('content_data', {})
        credentials = data.get('credentials', {})
        
        if not all([content_type, platform, content_data, credentials]):
            return jsonify({"error": "Content type, platform, content data, and credentials are required"}), 400
            
        # Publish to CMS
        result = export_integration.publish_to_cms(content_type, platform, content_data, credentials)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error publishing to CMS: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/mock-data', methods=['GET'])
def get_mock_data():
    """Return mock data for frontend testing"""
    try:
        # Load mock data from file
        mock_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'mock_data.json')
        
        if os.path.exists(mock_data_path):
            with open(mock_data_path, 'r') as f:
                mock_data = json.load(f)
        else:
            # Generate mock data if file doesn't exist
            mock_data = generate_mock_data()
            
            # Save mock data for future use
            os.makedirs(os.path.dirname(mock_data_path), exist_ok=True)
            with open(mock_data_path, 'w') as f:
                json.dump(mock_data, f, indent=2)
        
        return jsonify(mock_data)
        
    except Exception as e:
        print(f"Error getting mock data: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def generate_mock_data():
    """Generate mock data for frontend testing"""
    return {
        "content_blueprint": {
            "title": "Ultimate Guide to AI Content Strategy for SERP Dominance",
            "description": "A comprehensive guide to leveraging AI for content strategy that dominates search engine results pages.",
            "sections": [
                {
                    "title": "Introduction to AI-Powered Content Strategy",
                    "content": "AI is revolutionizing how content strategies are developed and implemented. This section explores the fundamental concepts and benefits.",
                    "subsections": [
                        {
                            "title": "The Evolution of Content Strategy",
                            "content": "How content strategy has evolved from keyword stuffing to sophisticated AI-driven approaches."
                        },
                        {
                            "title": "Key Benefits of AI in Content Creation",
                            "content": "Explore the efficiency, scalability, and effectiveness gains from implementing AI in your content workflow."
                        }
                    ]
                },
                {
                    "title": "Understanding SERP Features and Opportunities",
                    "content": "Modern SERPs contain various features beyond traditional organic listings. Learn how to identify and target these opportunities.",
                    "subsections": [
                        {
                            "title": "Featured Snippets and Position Zero",
                            "content": "Strategies for optimizing content to capture featured snippets and achieve position zero in search results."
                        },
                        {
                            "title": "People Also Ask and Related Questions",
                            "content": "Techniques for identifying and addressing common questions to improve visibility in PAA boxes."
                        }
                    ]
                },
                {
                    "title": "Competitive Analysis for Content Gaps",
                    "content": "Learn how to analyze competitor content to identify gaps and opportunities in your content strategy.",
                    "subsections": [
                        {
                            "title": "Content Structure Analysis",
                            "content": "Examining how top-ranking content is structured and organized to inform your own content development."
                        },
                        {
                            "title": "Topic Coverage Comparison",
                            "content": "Identifying topics and subtopics that competitors are missing or inadequately covering."
                        }
                    ]
                },
                {
                    "title": "AI-Generated Content Frameworks",
                    "content": "Leverage AI to create comprehensive content frameworks that address user intent and search engine requirements.",
                    "subsections": [
                        {
                            "title": "Intent-Matched Content Structures",
                            "content": "How to align content structure with different types of search intent (informational, navigational, transactional)."
                        },
                        {
                            "title": "Semantic Richness and Entity Relationships",
                            "content": "Techniques for enhancing content with semantic entities and relationships to improve relevance."
                        }
                    ]
                },
                {
                    "title": "Implementation and Measurement",
                    "content": "Strategies for implementing AI-driven content and measuring its performance in search results.",
                    "subsections": [
                        {
                            "title": "Content Production Workflow Integration",
                            "content": "How to integrate AI tools into your existing content production workflow for maximum efficiency."
                        },
                        {
                            "title": "Performance Tracking and Iteration",
                            "content": "Setting up tracking systems to measure content performance and iteratively improve based on data."
                        }
                    ]
                }
            ]
        },
        "keyword_data": {
            "keyword_scores": {
                "ai content strategy": {"difficulty": 65, "opportunity": 78},
                "serp dominance": {"difficulty": 58, "opportunity": 82},
                "ai content optimization": {"difficulty": 62, "opportunity": 75},
                "content strategy tools": {"difficulty": 70, "opportunity": 68},
                "ai for seo": {"difficulty": 67, "opportunity": 73},
                "content gap analysis": {"difficulty": 55, "opportunity": 80},
                "featured snippet optimization": {"difficulty": 60, "opportunity": 85}
            },
            "enhanced_metrics": {
                "ai content strategy": {"search_volume": 2400, "cpc": 4.25, "competition": 0.75},
                "serp dominance": {"search_volume": 1200, "cpc": 3.80, "competition": 0.68},
                "ai content optimization": {"search_volume": 1800, "cpc": 4.10, "competition": 0.72},
                "content strategy tools": {"search_volume": 3600, "cpc": 5.20, "competition": 0.82},
                "ai for seo": {"search_volume": 2900, "cpc": 4.75, "competition": 0.78},
                "content gap analysis": {"search_volume": 1500, "cpc": 3.50, "competition": 0.65},
                "featured snippet optimization": {"search_volume": 1100, "cpc": 3.90, "competition": 0.70}
            },
            "trend_analysis": {
                "ai content strategy": {"trend_direction": "up", "trend_strength": "strong", "seasonal_pattern": "steady"},
                "serp dominance": {"trend_direction": "up", "trend_strength": "moderate", "seasonal_pattern": "steady"},
                "ai content optimization": {"trend_direction": "up", "trend_strength": "strong", "seasonal_pattern": "steady"},
                "content strategy tools": {"trend_direction": "up", "trend_strength": "moderate", "seasonal_pattern": "higher in Q1/Q3"},
                "ai for seo": {"trend_direction": "up", "trend_strength": "strong", "seasonal_pattern": "steady"},
                "content gap analysis": {"trend_direction": "up", "trend_strength": "moderate", "seasonal_pattern": "steady"},
                "featured snippet optimization": {"trend_direction": "up", "trend_strength": "strong", "seasonal_pattern": "steady"}
            }
        },
        "optimization_recommendations": {
            "featured_snippets": {
                "opportunity": "high",
                "recommendations": [
                    "Structure content with clear question-answer format for targeted queries",
                    "Use concise paragraphs of 40-60 words that directly answer the question",
                    "Include supporting bullet points or numbered lists where appropriate",
                    "Use schema markup to help search engines understand your content structure",
                    "Target questions with high search volume but low competition"
                ]
            },
            "people_also_ask": {
                "opportunity": "high",
                "recommendations": [
                    "Research and include related questions throughout your content",
                    "Provide clear, concise answers to each question (50-60 words ideal)",
                    "Group related questions into dedicated sections with proper H2/H3 headings",
                    "Use FAQ schema markup to enhance visibility",
                    "Update content regularly with new questions as they appear in SERPs"
                ]
            },
            "knowledge_panels": {
                "opportunity": "medium",
                "recommendations": [
                    "Create comprehensive entity-focused content that establishes topical authority",
                    "Implement schema markup for your organization, products, or key concepts",
                    "Build authoritative backlinks from industry sources",
                    "Ensure consistent NAP (Name, Address, Phone) information across the web",
                    "Create and optimize Google Business Profile if applicable"
                ]
            },
            "image_packs": {
                "opportunity": "medium",
                "recommendations": [
                    "Create original, high-quality images relevant to your target keywords",
                    "Optimize image file names with descriptive, keyword-rich text",
                    "Add comprehensive alt text that includes target keywords naturally",
                    "Compress images for faster loading without sacrificing quality",
                    "Use schema markup for images when appropriate"
                ]
            },
            "video_results": {
                "opportunity": "low",
                "recommendations": [
                    "Create video content that addresses key questions in your niche",
                    "Optimize video titles, descriptions, and tags with target keywords",
                    "Create comprehensive video transcripts for better indexing",
                    "Embed videos in relevant blog posts to increase visibility",
                    "Use video schema markup to enhance SERP appearance"
                ]
            },
            "local_pack": {
                "opportunity": "low",
                "recommendations": [
                    "Optimize Google Business Profile with complete, accurate information",
                    "Encourage and respond to customer reviews",
                    "Ensure NAP consistency across all online directories",
                    "Create location-specific content pages if relevant",
                    "Build local citations and backlinks from local sources"
                ]
            },
            "top_stories": {
                "opportunity": "medium",
                "recommendations": [
                    "Publish timely, newsworthy content related to your industry",
                    "Implement news schema markup on appropriate pages",
                    "Ensure fast page loading speeds and mobile optimization",
                    "Build relationships with news aggregators and industry publications",
                    "Maintain regular publishing schedule for fresh content"
                ]
            }
        },
        "performance_prediction": {
            "estimated_serp_position": 3.2,
            "ranking_probability": 0.78,
            "estimated_traffic": 1450,
            "estimated_ctr": 8.2,
            "confidence_score": 82,
            "ranking_factors": [
                {
                    "factor_name": "Content Comprehensiveness",
                    "score": 0.85,
                    "description": "Your content covers the topic thoroughly with appropriate depth and breadth.",
                    "details": "Content includes all major subtopics and addresses key questions identified in SERPs."
                },
                {
                    "factor_name": "Keyword Optimization",
                    "score": 0.78,
                    "description": "Content is well-optimized for target keywords without over-optimization.",
                    "details": "Primary and secondary keywords are naturally distributed throughout the content."
                },
                {
                    "factor_name": "Content Structure",
                    "score": 0.82,
                    "description": "Content is well-structured with appropriate headings and organization.",
                    "details": "Logical hierarchy of H1-H4 tags that helps both users and search engines navigate the content."
                },
                {
                    "factor_name": "Readability",
                    "score": 0.75,
                    "description": "Content is readable and accessible to the target audience.",
                    "details": "Reading level is appropriate, with clear language and well-structured paragraphs."
                },
                {
                    "factor_name": "SERP Feature Optimization",
                    "score": 0.80,
                    "description": "Content is optimized for relevant SERP features.",
                    "details": "Structured for featured snippets and includes FAQ sections for People Also Ask boxes."
                }
            ],
            "improvement_suggestions": [
                {
                    "area": "Multimedia Enhancement",
                    "suggestion": "Add more visual elements such as infographics, charts, and videos to improve engagement and time on page.",
                    "impact": "Medium",
                    "effort": "Medium"
                },
                {
                    "area": "Schema Markup",
                    "suggestion": "Implement additional schema markup types to enhance SERP appearance and click-through rates.",
                    "impact": "Medium",
                    "effort": "Low"
                },
                {
                    "area": "Internal Linking",
                    "suggestion": "Strengthen internal linking structure to better distribute page authority and improve crawlability.",
                    "impact": "Medium",
                    "effort": "Low"
                },
                {
                    "area": "Mobile Optimization",
                    "suggestion": "Further optimize for mobile experience, focusing on Core Web Vitals metrics.",
                    "impact": "High",
                    "effort": "Medium"
                },
                {
                    "area": "User Experience",
                    "suggestion": "Improve page load speed and interactive elements to reduce bounce rate and increase engagement.",
                    "impact": "High",
                    "effort": "Medium"
                },
                {
                    "area": "Content Freshness",
                    "suggestion": "Establish a regular update schedule to keep content fresh and current with latest trends.",
                    "impact": "Medium",
                    "effort": "Medium"
                }
            ]
        },
        "export_formats": [
            {
                "id": "pdf",
                "name": "PDF Document",
                "description": "Export as a professionally formatted PDF document",
                "extension": "PDF"
            },
            {
                "id": "docx",
                "name": "Word Document",
                "description": "Export as an editable Microsoft Word document",
                "extension": "DOCX"
            },
            {
                "id": "html",
                "name": "HTML Document",
                "description": "Export as an HTML document ready for web publishing",
                "extension": "HTML"
            },
            {
                "id": "md",
                "name": "Markdown",
                "description": "Export as a Markdown file for easy editing",
                "extension": "MD"
            },
            {
                "id": "csv",
                "name": "CSV Spreadsheet",
                "description": "Export data as a CSV spreadsheet",
                "extension": "CSV"
            },
            {
                "id": "json",
                "name": "JSON Data",
                "description": "Export raw data in JSON format",
                "extension": "JSON"
            }
        ],
        "cms_platforms": [
            {
                "id": "wordpress",
                "name": "WordPress",
                "description": "Publish directly to your WordPress site",
                "icon": "wordpress-icon.svg"
            },
            {
                "id": "webflow",
                "name": "Webflow",
                "description": "Export to your Webflow CMS",
                "icon": "webflow-icon.svg"
            },
            {
                "id": "contentful",
                "name": "Contentful",
                "description": "Publish to your Contentful workspace",
                "icon": "contentful-icon.svg"
            },
            {
                "id": "shopify",
                "name": "Shopify",
                "description": "Export to your Shopify blog",
                "icon": "shopify-icon.svg"
            },
            {
                "id": "hubspot",
                "name": "HubSpot",
                "description": "Publish to your HubSpot CMS",
                "icon": "hubspot-icon.svg"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }
