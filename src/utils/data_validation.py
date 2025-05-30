"""
Data Quality Validation Module

This module provides validation functions to ensure real data implementation
and prevent mock/dummy data usage, following production-quality requirements.
"""

import logging
from typing import Dict, Any, List
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_real_implementation(data: Dict[str, Any]) -> Dict[str, bool]:
    """Validate that implementation uses real data, not mock"""

    validations = {
        "has_real_competitor_data": _check_real_competitor_data(data),
        "has_real_search_volumes": _check_real_search_volumes(data),
        "has_real_content_analysis": _check_real_content_analysis(data),
        "no_random_generation": _check_no_random_data(data),
        "api_calls_made": _check_real_api_usage(data),
        "confidence_intervals_realistic": _check_realistic_confidence(data)
    }

    return validations

def _check_real_competitor_data(data: Dict[str, Any]) -> bool:
    """Ensure competitor data comes from real scraping"""
    competitor_insights = data.get("competitor_insights", {})

    # Check for real content length data
    content_length = competitor_insights.get("content_length", {})
    if isinstance(content_length, dict) and content_length.get("average", 0) > 0:
        # Verify it's not a suspiciously round number
        avg_len = content_length.get("average", 0)
        if avg_len % 500 == 0 and avg_len > 1000:  # Suspicious round numbers
            return False
        return True

    # Check for real common topics
    common_topics = competitor_insights.get("common_topics", [])
    if isinstance(common_topics, list) and len(common_topics) > 0:
        # Topics should be real words, not "topic1", "topic2", etc.
        mock_patterns = ["topic", "example", "sample", "test", "demo"]
        for topic in common_topics[:3]:
            if any(pattern in topic.lower() for pattern in mock_patterns):
                return False
        return True

    return False

def _check_real_search_volumes(data: Dict[str, Any]) -> bool:
    """Check that search volume data appears real"""
    keyword_data = data.get("keyword_data", {})
    search_volume = keyword_data.get("search_volume", 0)

    # Real search volumes are rarely perfect round numbers
    if search_volume == 0:
        return False

    # Check for suspicious patterns
    suspicious_volumes = [1000, 1500, 2000, 2500, 3000, 5000, 10000]
    if search_volume in suspicious_volumes:
        return False

    # Real search volumes typically have some variance
    if search_volume % 100 == 0 and search_volume > 1000:
        return False

    return True

def _check_real_content_analysis(data: Dict[str, Any]) -> bool:
    """Verify content analysis contains real insights"""
    competitor_insights = data.get("competitor_insights", {})

    # Check sentiment analysis
    sentiment_trend = competitor_insights.get("sentiment_trend", "")
    if sentiment_trend and sentiment_trend != "Unknown - No competitor data scraped":
        return True

    # Check entity extraction
    common_topics = competitor_insights.get("common_topics", [])
    if len(common_topics) > 0:
        # Real topics should be substantive words
        real_topics = [t for t in common_topics if len(t) > 3 and t.isalpha()]
        return len(real_topics) > 0

    return False

def _check_no_random_data(data: Dict[str, Any]) -> bool:
    """Ensure no random number generation was used"""

    # Check for suspicious round numbers that indicate random generation
    suspicious_patterns = [
        lambda x: x == 1500,  # Common random content length
        lambda x: x % 100 == 0 and x > 1000,  # Round hundreds
        lambda x: str(x).endswith("000"),  # Round thousands
        lambda x: x in [75, 85, 65, 55],  # Common fake confidence scores
    ]

    # Check various numeric fields
    numeric_fields = []

    # Extract numeric values from nested data
    def extract_numbers(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                extract_numbers(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, (int, float)) and obj > 0:
            numeric_fields.append(obj)

    extract_numbers(data)

    # Check for suspicious patterns
    suspicious_count = 0
    for value in numeric_fields:
        if any(pattern(value) for pattern in suspicious_patterns):
            suspicious_count += 1

    # If more than 20% of numeric values are suspicious, likely random
    return suspicious_count / max(len(numeric_fields), 1) < 0.2

def _check_real_api_usage(data: Dict[str, Any]) -> bool:
    """Check for evidence of real API calls"""

    # Look for API-specific metadata
    analysis_method = data.get("analysis_method", "")
    data_source = data.get("data_source", "")

    # Check for real API indicators
    real_api_indicators = [
        "serpapi", "gemini", "ahrefs", "real_scraping", 
        "api_call", "real_domain_analysis"
    ]

    if any(indicator in analysis_method.lower() for indicator in real_api_indicators):
        return True

    if any(indicator in data_source.lower() for indicator in real_api_indicators):
        return True

    # Check for data quality indicators
    data_quality = data.get("data_quality", {})
    if isinstance(data_quality, dict):
        real_samples = data_quality.get("real_content_samples", 0)
        total_samples = data_quality.get("competitors_analyzed", 0)

        # If we have real content samples, APIs were likely used
        return real_samples > 0 and total_samples > 0

    return False

def _check_realistic_confidence(data: Dict[str, Any]) -> bool:
    """Check that confidence scores are realistic, not artificially precise"""

    # Extract confidence-related metrics
    confidence_fields = []

    def find_confidence_metrics(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if "confidence" in key.lower() or "score" in key.lower():
                    if isinstance(value, (int, float)):
                        confidence_fields.append(value)
                find_confidence_metrics(value, f"{path}.{key}" if path else key)

    find_confidence_metrics(data)

    # Check for unrealistic precision
    for score in confidence_fields:
        # Confidence scores should not be artificially precise
        if isinstance(score, float) and len(str(score).split('.')[1]) > 2:
            return False  # Too many decimal places

        # Should be in reasonable range
        if score < 0 or score > 100:
            return False

        # Avoid suspiciously perfect scores
        if score in [75.0, 80.0, 85.0, 90.0, 95.0]:
            return False

    return len(confidence_fields) > 0  # Should have some confidence metrics

def validate_serp_data_quality(serp_data: Dict[str, Any]) -> Dict[str, bool]:
    """Validate SERP data quality and authenticity"""

    validations = {
        "has_organic_results": _check_organic_results(serp_data),
        "realistic_result_count": _check_realistic_result_counts(serp_data),
        "valid_urls": _check_valid_urls(serp_data),
        "diverse_domains": _check_domain_diversity(serp_data),
        "no_placeholder_content": _check_no_placeholders(serp_data)
    }

    return validations

def _check_organic_results(serp_data: Dict[str, Any]) -> bool:
    """Check for presence of realistic organic results"""
    organic_results = serp_data.get("organic_results", [])

    if not organic_results or len(organic_results) < 3:
        return False

    # Check that results have required fields
    for result in organic_results[:5]:
        if not all(key in result for key in ["title", "link", "snippet"]):
            return False

        # Titles and snippets should be substantial
        if len(result.get("title", "")) < 10 or len(result.get("snippet", "")) < 20:
            return False

    return True

def _check_realistic_result_counts(serp_data: Dict[str, Any]) -> bool:
    """Check that result counts are realistic"""
    search_info = serp_data.get("search_information", {})
    total_results = search_info.get("total_results", 0)

    # Total results should be realistic (not round numbers)
    if total_results == 0:
        return False

    # Avoid suspiciously round numbers
    if total_results % 1000000 == 0 or total_results % 500000 == 0:
        return False

    # Should be in reasonable range
    return 1000 <= total_results <= 50000000

def _check_valid_urls(serp_data: Dict[str, Any]) -> bool:
    """Check that URLs are valid and diverse"""
    organic_results = serp_data.get("organic_results", [])

    url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*')

    for result in organic_results[:5]:
        url = result.get("link", "")
        if not url_pattern.match(url):
            return False

        # Should not be placeholder URLs
        if "example.com" in url or "placeholder" in url:
            return False

    return True

def _check_domain_diversity(serp_data: Dict[str, Any]) -> bool:
    """Check for diverse domains in results"""
    organic_results = serp_data.get("organic_results", [])

    domains = []
    for result in organic_results[:10]:
        url = result.get("link", "")
        if url.startswith("http"):
            try:
                domain = url.split("//")[-1].split("/")[0]
                domains.append(domain)
            except:
                continue

    # Should have diverse domains (not all the same)
    unique_domains = set(domains)
    return len(unique_domains) >= min(3, len(domains) // 2)

def _check_no_placeholders(serp_data: Dict[str, Any]) -> bool:
    """Check for absence of placeholder content"""
    organic_results = serp_data.get("organic_results", [])

    placeholder_indicators = [
        "lorem ipsum", "placeholder", "example", "sample",
        "test content", "dummy", "mock", "fake"
    ]

    for result in organic_results[:5]:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()

        for indicator in placeholder_indicators:
            if indicator in title or indicator in snippet:
                return False

    return True

def validate_competitor_analysis_quality(analysis: Dict[str, Any]) -> Dict[str, bool]:
    """Validate competitor analysis data quality"""

    validations = {
        "has_real_competitors": _check_real_competitors(analysis),
        "content_analysis_depth": _check_content_analysis_depth(analysis),
        "realistic_metrics": _check_realistic_metrics(analysis),
        "diverse_insights": _check_diverse_insights(analysis),
        "proper_data_attribution": _check_data_attribution(analysis)
    }

    return validations

def _check_real_competitors(analysis: Dict[str, Any]) -> bool:
    """Check for real competitor data"""
    competitors = analysis.get("competitors", [])

    if len(competitors) < 3:
        return False

    for competitor in competitors[:5]:
        # Should have real URLs
        url = competitor.get("url", "")
        if not url.startswith("http") or "example.com" in url:
            return False

        # Should have substantial content
        content_length = competitor.get("content_length", 0)
        if content_length < 100:  # Very short content is suspicious
            return False

    return True

def _check_content_analysis_depth(analysis: Dict[str, Any]) -> bool:
    """Check depth of content analysis"""
    insights = analysis.get("insights", {})

    # Should have multiple types of insights
    required_insights = ["content_length", "common_topics", "sentiment_trend"]

    for insight_type in required_insights:
        if insight_type not in insights:
            return False

        insight_data = insights[insight_type]
        if not insight_data or (isinstance(insight_data, str) and "error" in insight_data.lower()):
            return False

    return True

def _check_realistic_metrics(analysis: Dict[str, Any]) -> bool:
    """Check that metrics appear realistic"""
    insights = analysis.get("insights", {})
    content_length = insights.get("content_length", {})

    if isinstance(content_length, dict):
        avg_length = content_length.get("average", 0)
        min_length = content_length.get("min", 0)
        max_length = content_length.get("max", 0)

        # Basic sanity checks
        if avg_length <= 0 or min_length <= 0 or max_length <= 0:
            return False

        if min_length > avg_length or avg_length > max_length:
            return False

        # Range should be reasonable
        if max_length / min_length > 50:  # Too wide a range
            return False

    return True

def _check_diverse_insights(analysis: Dict[str, Any]) -> bool:
    """Check for diverse, meaningful insights"""
    insights = analysis.get("insights", {})
    common_topics = insights.get("common_topics", [])

    # Should have some common topics
    if not common_topics or len(common_topics) == 0:
        return False

    # Topics should be diverse (not all similar)
    if len(set(common_topics)) < len(common_topics) * 0.8:
        return False  # Too much repetition

    return True

def _check_data_attribution(analysis: Dict[str, Any]) -> bool:
    """Check for proper data source attribution"""

    # Should have data quality metrics
    data_quality = analysis.get("data_quality", {})
    if not isinstance(data_quality, dict):
        return False

    # Should track real samples
    competitors_analyzed = data_quality.get("competitors_analyzed", 0)
    content_samples = data_quality.get("content_samples", 0)

    return competitors_analyzed > 0 and content_samples >= 0

def generate_validation_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive validation report"""

    # Run all validation checks
    implementation_checks = validate_real_implementation(data)

    # Check SERP data if present
    serp_checks = {}
    if "serp_data" in data:
        serp_checks = validate_serp_data_quality(data["serp_data"])

    # Check competitor analysis if present
    competitor_checks = {}
    if "competitor_analysis" in data:
        competitor_checks = validate_competitor_analysis_quality(data["competitor_analysis"])

    # Calculate overall scores
    all_checks = {**implementation_checks, **serp_checks, **competitor_checks}
    total_checks = len(all_checks)
    passed_checks = sum(all_checks.values())

    overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    # Determine quality level
    if overall_score >= 90:
        quality_level = "excellent"
    elif overall_score >= 75:
        quality_level = "good"
    elif overall_score >= 60:
        quality_level = "acceptable"
    else:
        quality_level = "needs_improvement"

    return {
        "overall_score": round(overall_score, 1),
        "quality_level": quality_level,
        "checks_passed": passed_checks,
        "total_checks": total_checks,
        "detailed_results": {
            "implementation": implementation_checks,
            "serp_data": serp_checks,
            "competitor_analysis": competitor_checks
        },
        "recommendations": _generate_improvement_recommendations(all_checks)
    }

def _generate_improvement_recommendations(checks: Dict[str, bool]) -> List[str]:
    """Generate recommendations based on failed checks"""

    recommendations = []

    if not checks.get("has_real_competitor_data", True):
        recommendations.append("Implement real competitor data scraping with actual URLs and content")

    if not checks.get("has_real_search_volumes", True):
        recommendations.append("Use real search volume data from keyword APIs, avoid round numbers")

    if not checks.get("no_random_generation", True):
        recommendations.append("Remove random number generation and use real data sources")

    if not checks.get("api_calls_made", True):
        recommendations.append("Implement actual API calls to SerpAPI, Gemini, or other services")

    if not checks.get("realistic_result_count", True):
        recommendations.append("Ensure SERP result counts are realistic and varied")

    if not checks.get("diverse_domains", True):
        recommendations.append("Include diverse domains in SERP results, avoid repetition")

    return recommendations[:5]  # Return top 5 recommendations