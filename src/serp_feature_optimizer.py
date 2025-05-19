# Filename: src/modules/serp_feature_optimizer.py
import logging
import json
from typing import List, Dict, Any, Optional
from langchain_core.pydantic_v1 import BaseModel, Field

logger = logging.getLogger("keyword_research.serp_feature_optimizer")

class OptimizationStep(BaseModel):
    """A specific step to optimize for a SERP feature."""
    step_description: str = Field(..., description="Description of the optimization step.")
    implementation_details: str = Field(..., description="Details on how to implement this step.")
    priority: str = Field(..., description="Priority of this step (High, Medium, Low).")
    technical_complexity: str = Field(..., description="Technical complexity of implementation (Simple, Moderate, Complex).")

class ContentRequirement(BaseModel):
    """Content requirement for a SERP feature."""
    requirement: str = Field(..., description="Description of the content requirement.")
    examples: List[str] = Field(default_factory=list, description="Examples of the requirement in practice.")

class TechnicalRequirement(BaseModel):
    """Technical requirement for a SERP feature."""
    requirement: str = Field(..., description="Description of the technical requirement.")
    implementation: str = Field(..., description="How to implement this requirement.")
    code_example: Optional[str] = Field(None, description="Example code snippet if applicable.")

class SerpFeatureOptimizationStrategy(BaseModel):
    """Detailed optimization strategy for a specific SERP feature."""
    feature_name: str = Field(..., description="Name of the SERP feature.")
    description: str = Field(..., description="Description of the SERP feature.")
    optimization_goal: str = Field(..., description="Goal of optimizing for this feature.")
    optimization_steps: List[OptimizationStep] = Field(default_factory=list, description="Steps to optimize for this feature.")
    content_requirements: List[ContentRequirement] = Field(default_factory=list, description="Content requirements for this feature.")
    technical_requirements: List[TechnicalRequirement] = Field(default_factory=list, description="Technical requirements for this feature.")
    examples: List[str] = Field(default_factory=list, description="Examples of this feature in action.")
    best_practices: List[str] = Field(default_factory=list, description="Best practices for this feature.")

class SerpFeatureOptimizer:
    """
    Provides detailed optimization strategies for different SERP features.
    """
    
    def __init__(self):
        # Initialize optimization strategies for common SERP features
        self.optimization_strategies = self._initialize_optimization_strategies()
        
    def _initialize_optimization_strategies(self) -> Dict[str, SerpFeatureOptimizationStrategy]:
        """Initialize optimization strategies for common SERP features."""
        strategies = {}
        
        # Featured Snippet Optimization Strategy
        strategies["featured_snippet"] = SerpFeatureOptimizationStrategy(
            feature_name="Featured Snippet",
            description="A selected search result that appears in a box at the top of search results, providing a direct answer to a user's query.",
            optimization_goal="Get your content selected as the featured snippet to gain maximum visibility and authority.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Identify question-based queries your content can answer",
                    implementation_details="Research 'People Also Ask' questions and related queries that align with your target keyword. Focus on who, what, when, where, why, and how questions.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Structure content with clear question-answer format",
                    implementation_details="Include the target question as an H2 or H3 heading, followed immediately by a concise, direct answer (40-60 words) in the first paragraph after the heading.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Use structured data markup",
                    implementation_details="Implement FAQ, HowTo, or Q&A schema markup to help search engines understand your content structure.",
                    priority="Medium",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Format content for different snippet types",
                    implementation_details="For paragraph snippets: provide clear 40-60 word definitions or answers. For list snippets: use ordered or unordered HTML lists with clear headings. For table snippets: create well-structured HTML tables with headers.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Optimize for voice search compatibility",
                    implementation_details="Use natural language and conversational tone in questions and answers, as featured snippets are often used for voice search results.",
                    priority="Medium",
                    technical_complexity="Simple"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="Clear, concise answers to specific questions",
                    examples=[
                        "Q: How do featured snippets work? A: Featured snippets are selected search results that appear at the top of Google's search results in a box. They provide users with a direct answer to their query without requiring them to click through to a website.",
                        "Q: What is the ideal word count for a featured snippet? A: The ideal word count for a featured snippet paragraph is between 40-60 words, providing a concise answer that fits within Google's display parameters."
                    ]
                ),
                ContentRequirement(
                    requirement="Well-structured content with appropriate HTML formatting",
                    examples=[
                        "Use <h2> or <h3> tags for questions, followed by <p> tags for answers",
                        "Use <ol> or <ul> tags for list-based content",
                        "Use proper <table>, <th>, <tr>, and <td> tags for tabular data"
                    ]
                ),
                ContentRequirement(
                    requirement="Comprehensive content that expands on the snippet answer",
                    examples=[
                        "Provide the concise answer first, then expand with details, examples, and supporting information",
                        "Include related questions and answers within the same content piece"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement FAQ Schema Markup",
                    implementation="Add structured data to your page using JSON-LD format",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is a featured snippet?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "A featured snippet is a selected search result that appears at the top of Google's search results in a box, providing users with a direct answer to their query."
    }
  }]
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Optimize page load speed",
                    implementation="Ensure fast page loading as this is a ranking factor that affects featured snippet selection",
                    code_example=None
                ),
                TechnicalRequirement(
                    requirement="Ensure mobile-friendly design",
                    implementation="Use responsive design principles as mobile-friendliness impacts ranking and snippet selection",
                    code_example=None
                )
            ],
            examples=[
                "Definition snippet: 'What is a featured snippet?'",
                "List snippet: 'Steps to optimize for featured snippets'",
                "Table snippet: 'Featured snippet types comparison'"
            ],
            best_practices=[
                "Focus on one specific question per section to increase chances of snippet selection",
                "Use high-quality, factually accurate information to maintain snippet position",
                "Monitor featured snippet ownership and adjust content if you lose the position",
                "Include relevant images near your potential snippet content to enhance visual appeal",
                "Update content regularly to maintain freshness and accuracy"
            ]
        )
        
        # People Also Ask Optimization Strategy
        strategies["people_also_ask"] = SerpFeatureOptimizationStrategy(
            feature_name="People Also Ask",
            description="An expandable list of related questions that appears in search results, allowing users to explore topics related to their original query.",
            optimization_goal="Get your content featured in PAA boxes to increase visibility and capture users exploring related questions.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Research related questions for your target keyword",
                    implementation_details="Use tools like AnswerThePublic, AlsoAsked.com, or directly observe PAA boxes in search results for your target keywords.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Create dedicated Q&A sections in your content",
                    implementation_details="Include a specific FAQ or Q&A section that directly addresses the most common related questions.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Structure questions and answers properly",
                    implementation_details="Format questions as H2/H3/H4 headings and provide concise answers (50-60 words) immediately after each question.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Implement FAQ schema markup",
                    implementation_details="Add structured data using FAQ schema to explicitly identify questions and answers for search engines.",
                    priority="Medium",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Interlink related questions within your content",
                    implementation_details="Create internal links between related questions on your site to build a topic cluster and demonstrate topical authority.",
                    priority="Medium",
                    technical_complexity="Simple"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="Direct question-answer format",
                    examples=[
                        "Q: How do I optimize for People Also Ask boxes? A: To optimize for People Also Ask boxes, create dedicated Q&A sections in your content that directly address common related questions, format questions as headings, provide concise answers, and implement FAQ schema markup.",
                        "Q: Are People Also Ask boxes the same as featured snippets? A: No, People Also Ask boxes are expandable question boxes that appear in search results, while featured snippets are single answer boxes that appear at the top of search results."
                    ]
                ),
                ContentRequirement(
                    requirement="Comprehensive coverage of related questions",
                    examples=[
                        "Include 4-6 closely related questions in your FAQ section",
                        "Cover questions that represent different aspects of the topic (what, why, how, when, etc.)"
                    ]
                ),
                ContentRequirement(
                    requirement="Concise yet complete answers",
                    examples=[
                        "Keep answers to 50-60 words for optimal PAA inclusion",
                        "Ensure each answer stands alone as a complete response to the question"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement FAQ Schema Markup",
                    implementation="Add structured data to your page using JSON-LD format",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "How do I optimize for People Also Ask boxes?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "To optimize for People Also Ask boxes, create dedicated Q&A sections in your content that directly address common related questions, format questions as headings, provide concise answers, and implement FAQ schema markup."
    }
  }]
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Use proper HTML heading structure",
                    implementation="Format questions as H2, H3, or H4 headings followed by paragraph answers",
                    code_example="""<h3>How do I optimize for People Also Ask boxes?</h3>
<p>To optimize for People Also Ask boxes, create dedicated Q&A sections in your content that directly address common related questions, format questions as headings, provide concise answers, and implement FAQ schema markup.</p>"""
                ),
                TechnicalRequirement(
                    requirement="Implement proper internal linking",
                    implementation="Link between related questions on your site to build topical authority",
                    code_example=None
                )
            ],
            examples=[
                "Question cluster: 'What is keyword research?' with PAA questions like 'Why is keyword research important?', 'How do you do keyword research?', etc.",
                "Question cluster: 'How to optimize for featured snippets?' with PAA questions about different snippet types"
            ],
            best_practices=[
                "Update your Q&A content regularly as PAA questions change over time",
                "Monitor which of your pages appear in PAA results and optimize underperforming content",
                "Focus on questions with high search volume or commercial intent",
                "Ensure answers are factually accurate and authoritative",
                "Consider creating dedicated FAQ pages for topics with many related questions"
            ]
        )
        
        # Knowledge Panel Optimization Strategy
        strategies["knowledge_panel"] = SerpFeatureOptimizationStrategy(
            feature_name="Knowledge Panel",
            description="An information box that appears on the right side of search results, providing key facts about entities (people, organizations, places, etc.).",
            optimization_goal="Establish your brand or organization as an entity worthy of a knowledge panel and ensure the information displayed is accurate and favorable.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Establish entity status through structured data",
                    implementation_details="Implement Organization, Person, or LocalBusiness schema markup on your website to clearly identify your entity to search engines.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Create or claim your Google Business Profile",
                    implementation_details="Set up and verify a Google Business Profile (formerly Google My Business) with complete and accurate information.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Build authoritative citations and references",
                    implementation_details="Ensure your entity is mentioned on authoritative websites, industry directories, Wikipedia, Wikidata, and other trusted sources.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Maintain consistent NAP information",
                    implementation_details="Ensure your Name, Address, and Phone number are consistent across all online mentions and listings.",
                    priority="Medium",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Create a Wikipedia page (if appropriate)",
                    implementation_details="For notable entities, create a Wikipedia page following their guidelines for notability and neutral point of view.",
                    priority="Medium",
                    technical_complexity="Complex"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="Clear entity definition on your website",
                    examples=[
                        "About page with comprehensive information about your organization, history, leadership, etc.",
                        "Founder or key personnel biographies with notable achievements and background"
                    ]
                ),
                ContentRequirement(
                    requirement="Consistent brand information across the web",
                    examples=[
                        "Consistent company description used across all platforms and directories",
                        "Uniform presentation of logo, founding date, headquarters location, etc."
                    ]
                ),
                ContentRequirement(
                    requirement="Newsworthy content that establishes authority",
                    examples=[
                        "Press releases about significant company milestones or achievements",
                        "Media coverage from reputable publications"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement Organization Schema Markup",
                    implementation="Add structured data to your homepage using JSON-LD format",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Company Name",
  "url": "https://www.yourcompany.com",
  "logo": "https://www.yourcompany.com/images/logo.png",
  "foundingDate": "2010",
  "founders": [{
    "@type": "Person",
    "name": "Founder Name"
  }],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-555-555-5555",
    "contactType": "customer service"
  },
  "sameAs": [
    "https://www.facebook.com/yourcompany",
    "https://www.twitter.com/yourcompany",
    "https://www.linkedin.com/company/yourcompany"
  ]
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Create a Google Business Profile",
                    implementation="Set up and verify your business listing on Google Business Profile",
                    code_example=None
                ),
                TechnicalRequirement(
                    requirement="Establish Wikidata entry",
                    implementation="Create or update your entity's Wikidata entry with accurate information",
                    code_example=None
                )
            ],
            examples=[
                "Brand knowledge panel: 'Company Name' search showing key information about the organization",
                "Personal knowledge panel: 'Person Name' search showing biographical information",
                "Local business knowledge panel: 'Business Name' search showing location, hours, reviews, etc."
            ],
            best_practices=[
                "Monitor your knowledge panel regularly for accuracy and completeness",
                "Use Google's feedback mechanism to suggest changes to incorrect information",
                "Build a strong social media presence on major platforms",
                "Secure mentions and citations from high-authority websites",
                "Create content that clearly establishes your entity's key attributes and relationships"
            ]
        )
        
        # Local Pack Optimization Strategy
        strategies["local_pack"] = SerpFeatureOptimizationStrategy(
            feature_name="Local Pack (Map Pack)",
            description="A group of three local business listings with a map that appears for queries with local intent.",
            optimization_goal="Get your business listed in the local pack to capture local search traffic and drive foot traffic or local conversions.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Create and optimize Google Business Profile",
                    implementation_details="Set up, verify, and completely fill out your Google Business Profile with accurate business information, categories, attributes, and high-quality photos.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Implement local business schema markup",
                    implementation_details="Add LocalBusiness schema markup to your website to provide search engines with structured data about your business location and services.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Build and manage local citations",
                    implementation_details="Ensure your business is listed with consistent NAP (Name, Address, Phone) information across major directories and citation sources.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Generate and manage reviews",
                    implementation_details="Actively encourage satisfied customers to leave positive reviews on your Google Business Profile and respond professionally to all reviews.",
                    priority="Medium",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Create local content",
                    implementation_details="Develop content specifically targeting local keywords and addressing local customer needs or interests.",
                    priority="Medium",
                    technical_complexity="Simple"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="Locally optimized website content",
                    examples=[
                        "Location-specific service pages (e.g., 'Plumbing Services in [City Name]')",
                        "Local case studies or customer success stories"
                    ]
                ),
                ContentRequirement(
                    requirement="Complete and accurate business information",
                    examples=[
                        "Detailed 'About Us' page with company history and local connections",
                        "Clear 'Contact' and 'Directions' pages with embedded Google Map"
                    ]
                ),
                ContentRequirement(
                    requirement="Local keyword optimization",
                    examples=[
                        "Content naturally incorporating city names, neighborhoods, and local landmarks",
                        "FAQs addressing location-specific questions"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement LocalBusiness Schema Markup",
                    implementation="Add structured data to your contact or location pages using JSON-LD format",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Your Business Name",
  "image": "https://www.yourbusiness.com/images/logo.png",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "City Name",
    "addressRegion": "State",
    "postalCode": "12345",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "40.7128",
    "longitude": "-74.0060"
  },
  "url": "https://www.yourbusiness.com",
  "telephone": "+1-555-555-5555",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ]
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Optimize for mobile users",
                    implementation="Ensure your website is fully responsive and mobile-friendly",
                    code_example=None
                ),
                TechnicalRequirement(
                    requirement="Implement location-based structured data",
                    implementation="Add appropriate schema for service areas, departments, or multiple locations if applicable",
                    code_example=None
                )
            ],
            examples=[
                "Local service search: 'plumber near me' showing three local plumbing businesses",
                "Local product search: 'coffee shop downtown' showing three nearby coffee shops",
                "Local professional search: 'dentist in [city name]' showing three local dental practices"
            ],
            best_practices=[
                "Keep your Google Business Profile updated with current hours, photos, and posts",
                "Respond promptly to all customer reviews, both positive and negative",
                "Ensure NAP consistency across all online mentions of your business",
                "Use local phone numbers rather than toll-free numbers",
                "Include city and region names in title tags, meta descriptions, and H1 headings where appropriate"
            ]
        )
        
        # Image Pack Optimization Strategy
        strategies["image_pack"] = SerpFeatureOptimizationStrategy(
            feature_name="Image Pack",
            description="A horizontal row of images that appears in search results for queries that have visual intent.",
            optimization_goal="Get your images featured in image packs to increase visibility and drive traffic through image clicks.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Create high-quality, relevant images",
                    implementation_details="Develop original, high-resolution images that directly relate to your target keywords and provide visual value to users.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Optimize image file names",
                    implementation_details="Use descriptive, keyword-rich file names separated by hyphens (e.g., 'seo-image-optimization-guide.jpg' instead of 'IMG12345.jpg').",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Add comprehensive alt text",
                    implementation_details="Write descriptive alt text that includes target keywords while accurately describing the image for accessibility.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Implement image schema markup",
                    implementation_details="Add ImageObject schema to provide search engines with additional context about your images.",
                    priority="Medium",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Optimize image loading performance",
                    implementation_details="Compress images appropriately, use responsive image techniques, and implement lazy loading for better user experience and SEO.",
                    priority="Medium",
                    technical_complexity="Moderate"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="Original, high-quality images",
                    examples=[
                        "Custom photography or illustrations rather than stock images",
                        "Images that clearly demonstrate concepts discussed in the content"
                    ]
                ),
                ContentRequirement(
                    requirement="Contextually relevant image placement",
                    examples=[
                        "Images placed near related text content",
                        "Infographics summarizing key points from the article"
                    ]
                ),
                ContentRequirement(
                    requirement="Comprehensive image captions",
                    examples=[
                        "Descriptive captions that provide additional context and include keywords",
                        "Captions that encourage engagement with the surrounding content"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement proper image HTML",
                    implementation="Use complete img tags with all necessary attributes",
                    code_example="""<img 
  src="seo-image-optimization-guide.jpg" 
  alt="SEO image optimization guide showing best practices for image search visibility" 
  width="800" 
  height="600" 
  loading="lazy"
/>"""
                ),
                TechnicalRequirement(
                    requirement="Add ImageObject Schema Markup",
                    implementation="Implement schema markup for important images",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ImageObject",
  "contentUrl": "https://www.example.com/images/seo-image-optimization-guide.jpg",
  "name": "SEO Image Optimization Guide",
  "description": "A comprehensive visual guide to optimizing images for search engines",
  "width": "800px",
  "height": "600px"
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Implement responsive images",
                    implementation="Use srcset and sizes attributes to serve appropriate image sizes",
                    code_example="""<img 
  src="seo-image-small.jpg" 
  srcset="seo-image-small.jpg 400w, seo-image-medium.jpg 800w, seo-image-large.jpg 1200w" 
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px" 
  alt="SEO image optimization guide" 
/>"""
                )
            ],
            examples=[
                "Product search: 'red running shoes' showing images of products",
                "Informational search: 'types of succulents' showing plant images",
                "How-to search: 'how to tie a tie' showing instructional images"
            ],
            best_practices=[
                "Create images specifically designed to attract clicks in search results",
                "Use consistent image styles and branding across your website",
                "Consider adding your logo or watermark to images (subtly)",
                "Test different image formats (JPEG, PNG, WebP) for optimal quality and file size",
                "Create image sitemaps for large sites with many images"
            ]
        )
        
        # Video Carousel Optimization Strategy
        strategies["video_carousel"] = SerpFeatureOptimizationStrategy(
            feature_name="Video Carousel",
            description="A horizontal row of videos that appears in search results for queries with video intent.",
            optimization_goal="Get your videos featured in video carousels to increase visibility and drive traffic to your video content.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Create high-quality, relevant video content",
                    implementation_details="Develop engaging videos that directly address user search intent and provide value related to your target keywords.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Optimize video titles and descriptions",
                    implementation_details="Use keyword-rich, compelling titles and detailed descriptions that accurately represent your video content.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Create custom thumbnails",
                    implementation_details="Design eye-catching thumbnails that accurately represent your content and encourage clicks.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Implement video schema markup",
                    implementation_details="Add VideoObject schema to provide search engines with additional context about your videos.",
                    priority="Medium",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Create video transcripts and closed captions",
                    implementation_details="Add accurate transcripts and closed captions to improve accessibility and provide text content for search engines to index.",
                    priority="Medium",
                    technical_complexity="Moderate"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="High-quality video content",
                    examples=[
                        "Clear, well-lit footage with good audio quality",
                        "Content that directly addresses the target keyword or topic"
                    ]
                ),
                ContentRequirement(
                    requirement="Optimized video metadata",
                    examples=[
                        "Title: 'Complete SEO Guide for Beginners (Step-by-Step Tutorial)'",
                        "Description: 'In this comprehensive SEO tutorial, we cover everything beginners need to know about search engine optimization. Learn how to research keywords, optimize on-page elements, build quality backlinks, and measure your results...'"
                    ]
                ),
                ContentRequirement(
                    requirement="Engaging video structure",
                    examples=[
                        "Hook viewers in the first 15 seconds",
                        "Clear chapter markers or timestamps for longer videos"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement VideoObject Schema Markup",
                    implementation="Add structured data for your videos using JSON-LD format",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Complete SEO Guide for Beginners",
  "description": "In this comprehensive SEO tutorial, we cover everything beginners need to know about search engine optimization.",
  "thumbnailUrl": "https://www.example.com/images/seo-guide-thumbnail.jpg",
  "uploadDate": "2023-01-15T08:00:00+08:00",
  "duration": "PT15M33S",
  "contentUrl": "https://www.example.com/videos/seo-guide.mp4",
  "embedUrl": "https://www.youtube.com/embed/12345"
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Provide video transcripts",
                    implementation="Include full text transcripts on the page where the video is embedded",
                    code_example=None
                ),
                TechnicalRequirement(
                    requirement="Optimize video hosting",
                    implementation="Host videos on YouTube and embed on your site, or use a fast, reliable video hosting service",
                    code_example=None
                )
            ],
            examples=[
                "How-to search: 'how to change a tire' showing tutorial videos",
                "Product search: 'iPhone 14 review' showing review videos",
                "Entertainment search: 'funny cat videos' showing entertainment content"
            ],
            best_practices=[
                "Focus on video retention metrics to improve overall video performance",
                "Create video content for topics where visual demonstration adds value",
                "Keep videos concise and focused on delivering the promised content",
                "Use end screens and cards to encourage further engagement",
                "Cross-promote videos across your website and social media channels"
            ]
        )
        
        # FAQ Rich Results Optimization Strategy
        strategies["faq"] = SerpFeatureOptimizationStrategy(
            feature_name="FAQ Rich Results",
            description="Expandable questions and answers that appear directly in search results for pages with FAQ content.",
            optimization_goal="Get your FAQ content displayed as rich results to increase SERP real estate and improve click-through rates.",
            optimization_steps=[
                OptimizationStep(
                    step_description="Structure content in Q&A format",
                    implementation_details="Organize relevant content as clear questions followed by direct answers, with each Q&A pair in its own distinct section.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Implement FAQ schema markup",
                    implementation_details="Add FAQPage schema markup that correctly identifies each question and its corresponding answer.",
                    priority="High",
                    technical_complexity="Moderate"
                ),
                OptimizationStep(
                    step_description="Research relevant questions",
                    implementation_details="Identify questions your audience is actually asking through keyword research, customer support data, and 'People Also Ask' boxes.",
                    priority="High",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Provide comprehensive answers",
                    implementation_details="Ensure answers are complete, accurate, and valuable while remaining concise enough for rich results.",
                    priority="Medium",
                    technical_complexity="Simple"
                ),
                OptimizationStep(
                    step_description="Format FAQ content properly",
                    implementation_details="Use proper HTML structure with questions as headings (h2, h3, h4) and answers as paragraphs or lists.",
                    priority="Medium",
                    technical_complexity="Simple"
                )
            ],
            content_requirements=[
                ContentRequirement(
                    requirement="Clear question-answer format",
                    examples=[
                        "Q: What is FAQ schema markup? A: FAQ schema markup is structured data that helps search engines understand and display your frequently asked questions as rich results in search engine results pages.",
                        "Q: How many FAQs should I include on a page? A: Include between 3-10 relevant FAQs that address real user questions. Focus on quality over quantity, ensuring each question adds unique value."
                    ]
                ),
                ContentRequirement(
                    requirement="Relevant questions for your audience",
                    examples=[
                        "Questions derived from keyword research and 'People Also Ask' boxes",
                        "Questions commonly asked by customers or prospects"
                    ]
                ),
                ContentRequirement(
                    requirement="Concise but complete answers",
                    examples=[
                        "Answers that directly address the question in 1-2 paragraphs",
                        "Answers that provide value beyond what competitors offer"
                    ]
                )
            ],
            technical_requirements=[
                TechnicalRequirement(
                    requirement="Implement FAQPage Schema Markup",
                    implementation="Add structured data using JSON-LD format",
                    code_example="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is FAQ schema markup?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "FAQ schema markup is structured data that helps search engines understand and display your frequently asked questions as rich results in search engine results pages."
    }
  },
  {
    "@type": "Question",
    "name": "How many FAQs should I include on a page?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Include between 3-10 relevant FAQs that address real user questions. Focus on quality over quantity, ensuring each question adds unique value."
    }
  }]
}
</script>"""
                ),
                TechnicalRequirement(
                    requirement="Use proper HTML structure",
                    implementation="Format questions as headings and answers as paragraphs",
                    code_example="""<div class="faq-section">
  <h3>What is FAQ schema markup?</h3>
  <p>FAQ schema markup is structured data that helps search engines understand and display your frequently asked questions as rich results in search engine results pages.</p>
  
  <h3>How many FAQs should I include on a page?</h3>
  <p>Include between 3-10 relevant FAQs that address real user questions. Focus on quality over quantity, ensuring each question adds unique value.</p>
</div>"""
                ),
                TechnicalRequirement(
                    requirement="Test implementation with Google's Rich Results Test",
                    implementation="Validate your FAQ schema implementation using Google's testing tool",
                    code_example=None
                )
            ],
            examples=[
                "Product page: 'Common questions about our service' section with FAQ rich results",
                "Topic page: 'Frequently asked questions about mortgage refinancing' with FAQ rich results",
                "Support page: 'Troubleshooting FAQs' with FAQ rich results"
            ],
            best_practices=[
                "Don't duplicate questions across multiple pages on your site",
                "Keep answers concise but informative (1-2 paragraphs)",
                "Update FAQs regularly based on new customer questions and search trends",
                "Don't use FAQ schema for advertising or promotional content",
                "Consider user experience - don't overload pages with too many FAQs"
            ]
        )
        
        # Add more SERP feature strategies as needed
        
        return strategies
    
    def get_optimization_strategy(self, feature_name):
        """
        Get the optimization strategy for a specific SERP feature.
        
        Args:
            feature_name (str): Name of the SERP feature
            
        Returns:
            dict: Optimization strategy for the feature
        """
        # Normalize feature name to handle variations
        normalized_name = self._normalize_feature_name(feature_name)
        
        # Return strategy if available
        if normalized_name in self.optimization_strategies:
            strategy = self.optimization_strategies[normalized_name]
            return strategy.dict() if hasattr(strategy, 'dict') else strategy
        else:
            logger.warning(f"No optimization strategy available for feature: {feature_name}")
            return None
    
    def get_all_optimization_strategies(self):
        """
        Get all available optimization strategies.
        
        Returns:
            dict: All optimization strategies
        """
        return {name: (strategy.dict() if hasattr(strategy, 'dict') else strategy) 
                for name, strategy in self.optimization_strategies.items()}
    
    def _normalize_feature_name(self, feature_name):
        """Normalize feature name to match strategy keys."""
        if not feature_name:
            return ""
            
        name = feature_name.lower().strip()
        
        # Map common variations to standard names
        feature_mapping = {
            "featured snippet": "featured_snippet",
            "feature snippet": "featured_snippet",
            "answer box": "featured_snippet",
            "position zero": "featured_snippet",
            "people also ask": "people_also_ask",
            "paa": "people_also_ask",
            "related questions": "people_also_ask",
            "knowledge panel": "knowledge_panel",
            "knowledge graph": "knowledge_panel",
            "knowledge box": "knowledge_panel",
            "local pack": "local_pack",
            "map pack": "local_pack",
            "local 3-pack": "local_pack",
            "local results": "local_pack",
            "image pack": "image_pack",
            "image results": "image_pack",
            "images": "image_pack",
            "video carousel": "video_carousel",
            "video results": "video_carousel",
            "videos": "video_carousel",
            "faq": "faq",
            "faqs": "faq",
            "faq rich results": "faq",
            "frequently asked questions": "faq"
        }
        
        return feature_mapping.get(name, name)
    
    def generate_optimization_recommendations(self, detected_features, keyword_data=None):
        """
        Generate optimization recommendations based on detected SERP features.
        
        Args:
            detected_features (dict): Dictionary mapping keywords to detected features
            keyword_data (dict, optional): Additional keyword data for context
            
        Returns:
            list: Optimization recommendations
        """
        if not detected_features:
            return []
            
        recommendations = []
        processed_features = set()
        
        # Process each keyword and its features
        for keyword, features in detected_features.items():
            if not isinstance(features, list):
                continue
                
            for feature in features:
                # Skip if we've already processed this feature
                if feature in processed_features:
                    continue
                    
                # Get optimization strategy
                strategy = self.get_optimization_strategy(feature)
                if not strategy:
                    continue
                    
                # Create recommendation
                recommendation = {
                    "feature": strategy.get("feature_name", feature),
                    "description": strategy.get("description", ""),
                    "optimization_goal": strategy.get("optimization_goal", ""),
                    "priority_steps": [step for step in strategy.get("optimization_steps", [])
                                      if step.get("priority") == "High"],
                    "content_requirements": strategy.get("content_requirements", []),
                    "technical_requirements": strategy.get("technical_requirements", []),
                    "best_practices": strategy.get("best_practices", []),
                    "keywords_with_feature": [keyword]
                }
                
                # Add to recommendations
                recommendations.append(recommendation)
                processed_features.add(feature)
                
        return recommendations
