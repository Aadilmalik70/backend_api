"""
Blueprint Generator Utilities - Helper functions and fallback methods.

This module contains utility functions, fallback methods, and helper functions
for the blueprint generator service.
"""

import logging
import json
import re
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def get_google_apis_clients():
    """Get Google APIs clients from app config"""
    try:
        from flask import current_app
        return current_app.config.get('GOOGLE_APIS_CLIENTS', {})
    except RuntimeError as e:
        # Handle "Working outside of application context" error
        if "application context" in str(e):
            logger.warning("No Flask application context available for Google APIs clients")
            return {}
        raise e
    except Exception as e:
        logger.warning(f"Failed to get Google APIs clients: {str(e)}")
        return {}

def is_google_apis_enabled():
    """Check if Google APIs are enabled"""
    try:
        from flask import current_app
        return current_app.config.get('GOOGLE_APIS_ENABLED', False)
    except RuntimeError as e:
        # Handle "Working outside of application context" error
        if "application context" in str(e):
            logger.warning("No Flask application context available for Google APIs status")
            return False
        raise e
    except Exception as e:
        logger.warning(f"Failed to check Google APIs status: {str(e)}")
        return False

def get_migration_manager():
    """Get migration manager for seamless API transition"""
    try:
        google_apis_clients = get_google_apis_clients()
        return google_apis_clients.get('migration_manager')
    except RuntimeError as e:
        # Handle "Working outside of application context" error
        if "application context" in str(e):
            logger.warning("No Flask application context available for migration manager")
            return None
        raise e
    except Exception as e:
        logger.warning(f"Failed to get migration manager: {str(e)}")
        return None

def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from AI response with multiple fallback strategies."""
    if not response:
        return None
    
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except:
        pass
    
    try:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1).strip())
    except:
        pass
    
    try:
        # Try to find JSON object between first { and last }
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_str = response[first_brace:last_brace + 1]
            return json.loads(json_str)
    except:
        pass
    
    return None

def extract_paa_questions(serp_features: Dict[str, Any]) -> List[str]:
    """Extract People Also Ask questions from SERP features."""
    paa_questions = []
    
    try:
        if 'serp_features' in serp_features:
            serp_data = serp_features['serp_features']
            if 'people_also_ask' in serp_data:
                paa_data = serp_data['people_also_ask']
                if isinstance(paa_data, dict) and 'data' in paa_data:
                    paa_questions = [q.get('question', '') for q in paa_data['data'][:5]]
    except Exception as e:
        logger.warning(f"Failed to extract PAA questions: {str(e)}")
    
    return [q for q in paa_questions if q.strip()]

def get_fallback_competitors(keyword: str) -> Dict[str, Any]:
    """Get fallback competitor data when analysis fails."""
    return {
        'keyword': keyword,
        'competitors': [],
        'insights': {
            'common_topics': keyword.split() + ['guide', 'tips', 'strategy'],
            'content_length': {
                'average': 2500,
                'count': 0,
                'max': 0,
                'min': 0
            },
            'sentiment_trend': 'Positive',
            'data_quality': {
                'competitors_analyzed': 0,
                'content_samples': 0,
                'entities_extracted': 0,
                'failed_competitors': 0,
                'sentiment_samples': 0,
                'success_rate': 0,
                'successful_competitors': 0
            }
        },
        'analysis_status': 'fallback'
    }

def generate_fallback_heading_structure(keyword: str, common_sections: List[str]) -> Dict[str, Any]:
    """Generate a basic heading structure when AI fails."""
    keyword_title = keyword.title()
    
    h2_sections = [
        {
            "title": f"What is {keyword_title}?",
            "h3_subsections": ["Definition and Overview", "Key Benefits and Importance"]
        },
        {
            "title": f"How to Implement {keyword_title}",
            "h3_subsections": ["Step-by-Step Process", "Best Practices and Tips"]
        },
        {
            "title": f"{keyword_title} Strategies and Techniques",
            "h3_subsections": ["Advanced Methods", "Common Mistakes to Avoid"]
        },
        {
            "title": f"Measuring {keyword_title} Success",
            "h3_subsections": ["Key Performance Indicators", "Tools and Analytics"]
        }
    ]
    
    # Include common sections if available
    if common_sections:
        for section in common_sections[:2]:  # Add up to 2 common sections
            h2_sections.append({
                "title": section.title(),
                "h3_subsections": ["Key Concepts", "Implementation Guide"]
            })
    
    return {
        "h1": f"Complete Guide to {keyword_title}: Strategies, Tips, and Best Practices",
        "h2_sections": h2_sections[:6]  # Limit to 6 sections
    }

def generate_fallback_topic_clusters(keyword: str, paa_questions: List[str]) -> Dict[str, Any]:
    """Generate basic topic clusters when AI fails."""
    primary_cluster = [keyword, f"{keyword} guide", f"{keyword} tips", f"best {keyword} practices"]
    
    secondary_clusters = {
        "fundamentals": [f"{keyword} basics", f"{keyword} definition", f"introduction to {keyword}"],
        "implementation": [f"how to {keyword}", f"{keyword} process", f"{keyword} steps"],
        "advanced": [f"{keyword} strategies", f"advanced {keyword}", f"{keyword} optimization"],
        "tools": [f"{keyword} tools", f"best {keyword} software", f"{keyword} resources"]
    }
    
    # Add PAA-based clusters if available
    if paa_questions:
        secondary_clusters["common_questions"] = paa_questions[:3]
    
    related_keywords = [
        f"{keyword} guide", f"best {keyword}", f"{keyword} tips",
        f"{keyword} strategies", f"how to {keyword}", f"{keyword} best practices"
    ]
    
    return {
        "primary_cluster": primary_cluster,
        "secondary_clusters": secondary_clusters,
        "related_keywords": related_keywords
    }

def validate_blueprint_data(blueprint_data: Dict[str, Any]) -> bool:
    """
    Validate that the generated blueprint contains required components.
    
    Args:
        blueprint_data: Generated blueprint data
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['keyword', 'competitor_analysis', 'heading_structure', 'topic_clusters']
    
    for field in required_fields:
        if field not in blueprint_data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate heading structure
    heading_structure = blueprint_data['heading_structure']
    if not isinstance(heading_structure, dict) or 'h1' not in heading_structure:
        logger.error("Invalid heading structure format")
        return False
    
    # Validate topic clusters
    topic_clusters = blueprint_data['topic_clusters']
    if not isinstance(topic_clusters, dict) or 'primary_cluster' not in topic_clusters:
        logger.error("Invalid topic clusters format")
        return False
    
    return True

def get_fallback_serp_features(keyword: str, error_msg: str = "") -> Dict[str, Any]:
    """Get fallback SERP features data when analysis fails."""
    return {
        'serp_features': {},
        'recommendations': [],
        'analysis_status': 'fallback',
        'error': error_msg or 'SERP analysis failed'
    }

def get_fallback_content_insights(error_msg: str = "") -> Dict[str, Any]:
    """Get fallback content insights when analysis fails."""
    return {
        'avg_word_count': 0,
        'common_sections': [],
        'content_gaps': [],
        'structural_patterns': {},
        'analysis_status': 'failed',
        'error': error_msg or 'Content analysis failed'
    }

def safe_execution(func, *args, **kwargs):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Tuple of (success: bool, result: Any, error: str)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Safe execution failed for {func.__name__}: {error_msg}")
        return False, None, error_msg

def cleanup_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove any control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text

def format_error_response(error_msg: str, component: str = "blueprint_generator") -> Dict[str, Any]:
    """Format a standardized error response."""
    return {
        'error': True,
        'message': error_msg,
        'component': component,
        'timestamp': str(int(time.time())),
        'status': 'failed'
    }
