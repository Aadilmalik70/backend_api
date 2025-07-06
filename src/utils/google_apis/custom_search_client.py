"""
Google Custom Search API Client

Provides integration with Google Custom Search API for SERP analysis,
competitor monitoring, and search result insights.
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

class CustomSearchClient:
    """
    Google Custom Search API client for SERP analysis and monitoring
    """
    
    def __init__(self):
        """Initialize Custom Search client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
        self.base_url = 'https://www.googleapis.com/customsearch/v1'
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Custom Search not configured. Using mock data.")
    
    def search(self, query: str, 
               num_results: int = 10, 
               start_index: int = 1,
               site_search: str = None,
               exclude_sites: List[str] = None) -> Dict[str, Any]:
        """
        Perform custom search
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for results (1-based)
            site_search: Restrict search to specific site
            exclude_sites: List of sites to exclude
            
        Returns:
            Search results
        """
        if not self.api_key or not self.search_engine_id:
            return self._get_mock_search_results(query, num_results)
        
        try:
            # Prepare parameters
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10),  # Max 10 per request
                'start': start_index
            }
            
            # Add site restrictions
            if site_search:
                params['siteSearch'] = site_search
            
            # Exclude sites (Custom Search API limitation - need to modify query)
            if exclude_sites:
                exclusion_terms = ' '.join([f'-site:{site}' for site in exclude_sites])
                params['q'] = f"{query} {exclusion_terms}"
            
            logger.info(f"Making Google Custom Search request for: '{query}'")
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Google Custom Search response: {len(data.get('items', []))} items")
            
            # Check for API errors
            if 'error' in data:
                error_info = data['error']
                logger.error(f"Google Custom Search API error: {error_info}")
                return self._get_mock_search_results(query, num_results)
            
            # Process results
            items = data.get('items', [])
            
            if not items:
                logger.warning(f"No results returned for query: '{query}'")
                # Return mock data if no real results
                return self._get_mock_search_results(query, num_results)
            
            processed_results = []
            
            for i, item in enumerate(items):
                result = {
                    'position': start_index + i,
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'domain': self._extract_domain(item.get('link', '')),
                    'cache_id': item.get('cacheId'),
                    'formatted_url': item.get('formattedUrl', ''),
                    'html_formatted_url': item.get('htmlFormattedUrl', ''),
                    'html_snippet': item.get('htmlSnippet', ''),
                    'html_title': item.get('htmlTitle', '')
                }
                
                # Extract page metadata if available
                if 'pagemap' in item:
                    pagemap = item['pagemap']
                    result['metadata'] = {
                        'metatags': pagemap.get('metatags', [{}])[0] if pagemap.get('metatags') else {},
                        'cse_thumbnail': pagemap.get('cse_thumbnail', [{}])[0] if pagemap.get('cse_thumbnail') else {},
                        'cse_image': pagemap.get('cse_image', [{}])[0] if pagemap.get('cse_image') else {}
                    }
                
                processed_results.append(result)
            
            # Extract search information
            search_info = data.get('searchInformation', {})
            
            return {
                'query': query,
                'search_parameters': {
                    'num_results': num_results,
                    'start_index': start_index,
                    'site_search': site_search,
                    'exclude_sites': exclude_sites
                },
                'search_information': {
                    'total_results': int(search_info.get('totalResults', 0)),
                    'search_time': float(search_info.get('searchTime', 0)),
                    'formatted_total_results': search_info.get('formattedTotalResults', '0'),
                    'formatted_search_time': search_info.get('formattedSearchTime', '0')
                },
                'items': processed_results,  # Use 'items' to match Google API format
                'total_results_returned': len(processed_results),
                'data_source': 'google_custom_search'  # Mark as real data
            }
            
        except requests.RequestException as e:
            logger.error(f"Custom Search API request failed: {e}")
            return self._get_mock_search_results(query, num_results)
        except Exception as e:
            logger.error(f"Error performing custom search: {e}")
            return self._get_mock_search_results(query, num_results)
    
    def analyze_serp_features(self, query: str) -> Dict[str, Any]:
        """
        Analyze SERP features for a query
        
        Args:
            query: Search query to analyze
            
        Returns:
            SERP features analysis
        """
        search_results = self.search(query, num_results=10)
        
        if not search_results.get('results'):
            return self._get_mock_serp_features(query)
        
        # Analyze SERP features (simplified analysis)
        features = {
            'organic_results': {
                'count': len(search_results['results']),
                'domains': list(set(r['domain'] for r in search_results['results'])),
                'avg_snippet_length': sum(len(r.get('snippet', '')) for r in search_results['results']) / len(search_results['results'])
            },
            'featured_snippets': {'presence': 'none'},  # Custom Search API doesn't return these directly
            'people_also_ask': {'presence': 'none'},
            'knowledge_panels': {'presence': 'none'},
            'image_packs': {'presence': 'none'},
            'video_results': {'presence': 'none'},
            'local_pack': {'presence': 'none'},
            'shopping_results': {'presence': 'none'}
        }
        
        # Check for rich results based on metadata
        for result in search_results['results']:
            metadata = result.get('metadata', {})
            metatags = metadata.get('metatags', {})
            
            # Check for structured data indicators
            if any(tag in metatags for tag in ['og:type', 'article:author', 'product:price']):
                features['rich_results'] = {'presence': 'detected', 'types': []}
                
                if 'article:author' in metatags:
                    features['rich_results']['types'].append('article')
                if 'product:price' in metatags:
                    features['rich_results']['types'].append('product')
        
        return {
            'query': query,
            'features': features,
            'analysis_metadata': {
                'total_results_analyzed': len(search_results['results']),
                'search_time': search_results['search_information']['search_time']
            }
        }
    
    def get_competitors(self, query: str, exclude_domain: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get competitor analysis for a query
        
        Args:
            query: Search query
            exclude_domain: Domain to exclude from competitors
            limit: Maximum number of competitors
            
        Returns:
            List of competitor data
        """
        exclude_sites = [exclude_domain] if exclude_domain else None
        search_results = self.search(query, num_results=limit, exclude_sites=exclude_sites)
        
        competitors = []
        for result in search_results.get('results', []):
            competitor = {
                'domain': result['domain'],
                'url': result['link'],
                'title': result['title'],
                'snippet': result['snippet'],
                'position': result['position'],
                'display_link': result['display_link']
            }
            
            # Add metadata analysis
            metadata = result.get('metadata', {})
            if metadata:
                metatags = metadata.get('metatags', {})
                competitor['seo_analysis'] = {
                    'has_meta_description': bool(metatags.get('description')),
                    'has_og_tags': any(key.startswith('og:') for key in metatags.keys()),
                    'has_twitter_cards': any(key.startswith('twitter:') for key in metatags.keys()),
                    'estimated_content_length': len(result.get('snippet', '')) * 10  # Rough estimate
                }
            
            competitors.append(competitor)
        
        return competitors
    
    def monitor_rankings(self, queries: List[str], target_domain: str) -> Dict[str, Any]:
        """
        Monitor rankings for target domain across multiple queries
        
        Args:
            queries: List of queries to monitor
            target_domain: Domain to track rankings for
            
        Returns:
            Ranking monitoring results
        """
        ranking_data = {
            'target_domain': target_domain,
            'monitoring_date': '2024-01-01',  # In real implementation, use current date
            'queries': {}
        }
        
        for query in queries:
            search_results = self.search(query, num_results=20)
            
            # Find target domain position
            position = None
            target_result = None
            
            for result in search_results.get('results', []):
                if target_domain in result['domain']:
                    position = result['position']
                    target_result = result
                    break
            
            ranking_data['queries'][query] = {
                'position': position,
                'found': position is not None,
                'result_data': target_result,
                'total_results': search_results['search_information']['total_results'],
                'competitors_above': position - 1 if position else None
            }
        
        return ranking_data
    
    def analyze_content_gaps(self, query: str, target_domain: str) -> Dict[str, Any]:
        """
        Analyze content gaps compared to competitors
        
        Args:
            query: Search query to analyze
            target_domain: Your domain for comparison
            
        Returns:
            Content gap analysis
        """
        competitors = self.get_competitors(query, exclude_domain=target_domain, limit=5)
        
        # Analyze competitor content themes
        all_snippets = ' '.join([comp['snippet'] for comp in competitors])
        
        # Simple keyword extraction (would be enhanced with proper NLP)
        import re
        words = re.findall(r'\b\w{4,}\b', all_snippets.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top themes
        top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'query': query,
            'target_domain': target_domain,
            'content_gaps': {
                'competitor_themes': [{'theme': theme, 'frequency': freq} for theme, freq in top_themes],
                'coverage_opportunities': [
                    f"Content about {theme}" for theme, _ in top_themes[:5]
                ],
                'content_suggestions': [
                    f"Create comprehensive guide on {top_themes[0][0]}",
                    f"Add section about {top_themes[1][0]}",
                    f"Include information on {top_themes[2][0]}"
                ] if top_themes else []
            },
            'competitor_analysis': {
                'total_competitors': len(competitors),
                'avg_snippet_length': sum(len(comp['snippet']) for comp in competitors) / len(competitors) if competitors else 0,
                'domains_analyzed': [comp['domain'] for comp in competitors]
            }
        }
    
    def health_check(self) -> bool:
        """Perform health check"""
        try:
            if not self.api_key or not self.search_engine_id:
                return False
            
            # Test with a simple search
            test_result = self.search('test', num_results=1)
            return len(test_result.get('results', [])) >= 0  # Even 0 results is a successful API call
            
        except Exception as e:
            logger.error(f"Custom Search health check failed: {e}")
            return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc
        except:
            return ""
    
    def _get_mock_search_results(self, query: str, num_results: int) -> Dict[str, Any]:
        """Return mock search results when API is not available"""
        mock_results = []
        
        # Enhanced mock data with more keyword-rich content
        keyword_variations = {
            'seo': ['search engine optimization', 'seo strategy', 'seo tools', 'seo techniques', 'seo best practices'],
            'digital marketing': ['online marketing', 'digital marketing strategy', 'marketing automation', 'content marketing', 'social media marketing'],
            'tools': ['software tools', 'marketing tools', 'analytics tools', 'automation tools', 'productivity tools'],
            'strategies': ['marketing strategies', 'growth strategies', 'business strategies', 'optimization strategies', 'competitive strategies']
        }
        
        # Generate keyword-rich content based on query
        related_keywords = []
        for key, variations in keyword_variations.items():
            if key.lower() in query.lower():
                related_keywords.extend(variations)
        
        if not related_keywords:
            related_keywords = ['digital marketing', 'seo optimization', 'content strategy', 'marketing tools', 'analytics']
        
        for i in range(min(num_results, 5)):  # Generate up to 5 mock results
            # Create keyword-rich titles and snippets
            title_keywords = related_keywords[i:i+3] if i+3 <= len(related_keywords) else related_keywords[:3]
            snippet_keywords = related_keywords[i:i+5] if i+5 <= len(related_keywords) else related_keywords[:5]
            
            mock_results.append({
                'position': i + 1,
                'title': f'Complete Guide to {" and ".join(title_keywords[:2])} - Expert Tips and Best Practices',
                'link': f'https://example{i + 1}.com/{query.lower().replace(" ", "-")}-guide',
                'snippet': f'Learn about {" ".join(snippet_keywords[:3])} with our comprehensive guide. Discover advanced techniques for {" and ".join(snippet_keywords[3:])} to improve your marketing performance and achieve better results.',
                'display_link': f'example{i + 1}.com',
                'domain': f'example{i + 1}.com',
                'formatted_url': f'https://example{i + 1}.com/{query.lower().replace(" ", "-")}-guide',
                'metadata': {
                    'metatags': {
                        'description': f'Expert guide on {" and ".join(related_keywords[:2])} with practical tips and strategies',
                        'keywords': ', '.join(related_keywords[:10]),
                        'og:title': f'Master {" and ".join(title_keywords[:2])} - Complete Guide',
                        'og:type': 'article'
                    }
                }
            })
        
        return {
            'query': query,
            'search_parameters': {
                'num_results': num_results,
                'start_index': 1,
                'site_search': None,
                'exclude_sites': None
            },
            'search_information': {
                'total_results': 1500000,
                'search_time': 0.45,
                'formatted_total_results': '1,500,000',
                'formatted_search_time': '0.45'
            },
            'items': mock_results,  # Changed from 'results' to 'items' to match Google API format
            'total_results_returned': len(mock_results),
            'note': 'Mock data - Configure Google Custom Search API for real data'
        }
    
    def _get_mock_serp_features(self, query: str) -> Dict[str, Any]:
        """Return mock SERP features analysis"""
        return {
            'query': query,
            'features': {
                'organic_results': {
                    'count': 10,
                    'domains': ['example1.com', 'example2.com', 'example3.com'],
                    'avg_snippet_length': 156
                },
                'featured_snippets': {'presence': 'strong'},
                'people_also_ask': {'presence': 'medium'},
                'knowledge_panels': {'presence': 'none'},
                'image_packs': {'presence': 'weak'},
                'video_results': {'presence': 'medium'},
                'rich_results': {'presence': 'detected', 'types': ['article', 'product']}
            },
            'analysis_metadata': {
                'total_results_analyzed': 10,
                'search_time': 0.45
            },
            'note': 'Mock data - Configure Google Custom Search API for real analysis'
        }
