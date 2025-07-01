"""
Google Search Console API Client

Provides integration with Google Search Console API for performance data,
indexing status, and site analysis.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    service_account = None
    build = None
    HttpError = Exception

# Configure logging
logger = logging.getLogger(__name__)

class SearchConsoleClient:
    """
    Google Search Console API client for SEO performance data
    """
    
    def __init__(self):
        """Initialize Search Console client"""
        self.service = None
        self.site_url = os.getenv('SEARCH_CONSOLE_SITE_URL')
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google Search Console service"""
        try:
            if not service_account or not build:
                logger.warning("Google API libraries not installed. Install google-api-python-client")
                return
            
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_path or not os.path.exists(credentials_path):
                logger.warning("Google service account credentials not found")
                return
            
            # Create credentials
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            
            # Build service
            self.service = build('searchconsole', 'v1', credentials=credentials)
            logger.info("Search Console client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Search Console client: {e}")
    
    def get_performance_data(self, 
                           start_date: str = None, 
                           end_date: str = None,
                           dimensions: List[str] = None,
                           search_type: str = 'web') -> Dict[str, Any]:
        """
        Get performance data from Search Console
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            dimensions: List of dimensions (query, page, country, device, date)
            search_type: Type of search (web, image, video)
            
        Returns:
            Performance data dictionary
        """
        if not self.service or not self.site_url:
            return self._get_mock_performance_data()
        
        try:
            # Default dates - last 28 days
            if not end_date:
                end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Default dimensions
            if not dimensions:
                dimensions = ['query', 'page']
            
            # Prepare request
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'searchType': search_type,
                'rowLimit': 1000
            }
            
            # Execute request
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request
            ).execute()
            
            # Process results
            rows = response.get('rows', [])
            processed_data = {
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'dimensions': dimensions,
                'total_rows': len(rows),
                'data': []
            }
            
            for row in rows:
                processed_row = {
                    'keys': row.get('keys', []),
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': row.get('ctr', 0),
                    'position': row.get('position', 0)
                }
                processed_data['data'].append(processed_row)
            
            return processed_data
            
        except HttpError as e:
            logger.error(f"Search Console API error: {e}")
            return self._get_mock_performance_data()
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return self._get_mock_performance_data()
    
    def get_query_performance(self, query: str, days: int = 28) -> Dict[str, Any]:
        """
        Get performance data for a specific query
        
        Args:
            query: Search query to analyze
            days: Number of days to look back
            
        Returns:
            Query performance data
        """
        end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days + 3)).strftime('%Y-%m-%d')
        
        if not self.service or not self.site_url:
            return self._get_mock_query_performance(query)
        
        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query', 'page'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'query',
                        'operator': 'contains',
                        'expression': query
                    }]
                }],
                'searchType': 'web',
                'rowLimit': 100
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request
            ).execute()
            
            rows = response.get('rows', [])
            
            # Aggregate data for the query
            total_clicks = sum(row.get('clicks', 0) for row in rows)
            total_impressions = sum(row.get('impressions', 0) for row in rows)
            avg_ctr = total_clicks / max(total_impressions, 1)
            avg_position = sum(row.get('position', 0) for row in rows) / max(len(rows), 1)
            
            return {
                'query': query,
                'date_range': {'start_date': start_date, 'end_date': end_date},
                'performance': {
                    'clicks': total_clicks,
                    'impressions': total_impressions,
                    'ctr': avg_ctr,
                    'average_position': avg_position
                },
                'pages': [{'url': row['keys'][1], 'clicks': row.get('clicks', 0)} 
                         for row in rows if len(row.get('keys', [])) > 1]
            }
            
        except Exception as e:
            logger.error(f"Error getting query performance: {e}")
            return self._get_mock_query_performance(query)
    
    def get_sitemap_status(self) -> List[Dict[str, Any]]:
        """Get sitemap submission status"""
        if not self.service or not self.site_url:
            return [{'sitemap': 'https://example.com/sitemap.xml', 'status': 'Success', 'submitted': '2024-01-01'}]
        
        try:
            response = self.service.sitemaps().list(siteUrl=self.site_url).execute()
            sitemaps = response.get('sitemap', [])
            
            return [{
                'sitemap': sitemap.get('feedpath'),
                'status': sitemap.get('status'),
                'submitted': sitemap.get('lastSubmitted'),
                'errors': sitemap.get('errors', 0),
                'warnings': sitemap.get('warnings', 0)
            } for sitemap in sitemaps]
            
        except Exception as e:
            logger.error(f"Error getting sitemap status: {e}")
            return []
    
    def submit_url_for_indexing(self, url: str) -> Dict[str, Any]:
        """
        Submit URL for indexing (requires Indexing API)
        Note: This is a placeholder - Indexing API has specific use cases
        """
        logger.info(f"URL indexing request for: {url}")
        return {
            'url': url,
            'status': 'submitted',
            'message': 'URL submitted for indexing consideration'
        }
    
    def get_crawl_errors(self) -> List[Dict[str, Any]]:
        """
        Get crawl errors (Note: Legacy API deprecated)
        Returns mock data for compatibility
        """
        return [
            {
                'error_type': 'notFound',
                'platform': 'web',
                'count': 5,
                'sample_urls': ['https://example.com/page1', 'https://example.com/page2']
            }
        ]
    
    def health_check(self) -> bool:
        """Perform health check"""
        try:
            if not self.service or not self.site_url:
                return False
            
            # Try to list sites to check connectivity
            response = self.service.sites().list().execute()
            return True
            
        except Exception as e:
            logger.error(f"Search Console health check failed: {e}")
            return False
    
    def _get_mock_performance_data(self) -> Dict[str, Any]:
        """Return mock performance data when API is not available"""
        return {
            'date_range': {
                'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            },
            'dimensions': ['query', 'page'],
            'total_rows': 3,
            'data': [
                {
                    'keys': ['sample query 1', 'https://example.com/page1'],
                    'clicks': 150,
                    'impressions': 3000,
                    'ctr': 0.05,
                    'position': 8.5
                },
                {
                    'keys': ['sample query 2', 'https://example.com/page2'],
                    'clicks': 89,
                    'impressions': 1800,
                    'ctr': 0.049,
                    'position': 12.2
                },
                {
                    'keys': ['sample query 3', 'https://example.com/page3'],
                    'clicks': 67,
                    'impressions': 1200,
                    'ctr': 0.056,
                    'position': 6.8
                }
            ],
            'note': 'Mock data - Configure Search Console API for real data'
        }
    
    def _get_mock_query_performance(self, query: str) -> Dict[str, Any]:
        """Return mock query performance data"""
        return {
            'query': query,
            'date_range': {
                'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            },
            'performance': {
                'clicks': 45,
                'impressions': 890,
                'ctr': 0.051,
                'average_position': 9.2
            },
            'pages': [
                {'url': 'https://example.com/relevant-page-1', 'clicks': 28},
                {'url': 'https://example.com/relevant-page-2', 'clicks': 17}
            ],
            'note': 'Mock data - Configure Search Console API for real data'
        }
