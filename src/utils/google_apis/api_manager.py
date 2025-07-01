"""
Google API Manager - Central coordination for all Google APIs

This module provides centralized management and coordination for all Google API clients,
including authentication, rate limiting, error handling, and fallback mechanisms.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIUsageStats:
    """Track API usage statistics"""
    api_name: str
    calls_made: int = 0
    errors: int = 0
    last_call: Optional[datetime] = None
    average_response_time: float = 0.0
    cost_estimate: float = 0.0

class GoogleAPIManager:
    """
    Central manager for all Google API clients with unified error handling,
    rate limiting, and fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize the Google API Manager"""
        self.api_clients = {}
        self.usage_stats = {}
        self.rate_limits = {
            'search_console': {'calls_per_minute': 100, 'calls_per_day': 1000},
            'knowledge_graph': {'calls_per_minute': 60, 'calls_per_day': 100000},
            'custom_search': {'calls_per_minute': 100, 'calls_per_day': 10000},
            'natural_language': {'calls_per_minute': 600, 'calls_per_day': 1000000},
            'gemini': {'calls_per_minute': 60, 'calls_per_day': 1500}
        }
        self.fallback_enabled = True
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all Google API clients"""
        try:
            # Import clients dynamically to avoid import errors if modules don't exist yet
            from .search_console_client import SearchConsoleClient
            from .knowledge_graph_client import KnowledgeGraphClient
            from .custom_search_client import CustomSearchClient
            from .natural_language_client import NaturalLanguageClient
            from .gemini_client import GeminiClient
            
            # Initialize clients
            self.api_clients['search_console'] = SearchConsoleClient()
            self.api_clients['knowledge_graph'] = KnowledgeGraphClient()
            self.api_clients['custom_search'] = CustomSearchClient()
            self.api_clients['natural_language'] = NaturalLanguageClient()
            self.api_clients['gemini'] = GeminiClient()
            
            # Initialize usage stats
            for api_name in self.api_clients.keys():
                self.usage_stats[api_name] = APIUsageStats(api_name)
                
            logger.info("Google API Manager initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Some API clients not available: {e}")
            # Initialize with empty dict for gradual implementation
            pass
    
    def get_client(self, api_name: str):
        """Get a specific API client"""
        return self.api_clients.get(api_name)
    
    def execute_with_fallback(self, primary_func, fallback_func, api_name: str, *args, **kwargs):
        """
        Execute API call with automatic fallback to SerpAPI if needed
        
        Args:
            primary_func: Primary Google API function
            fallback_func: Fallback function (usually SerpAPI)
            api_name: Name of the API for tracking
            *args, **kwargs: Function arguments
            
        Returns:
            API response with fallback handling
        """
        start_time = time.time()
        
        try:
            # Check rate limits
            if not self._check_rate_limit(api_name):
                logger.warning(f"Rate limit exceeded for {api_name}, using fallback")
                if fallback_func and self.fallback_enabled:
                    return fallback_func(*args, **kwargs)
                else:
                    raise Exception(f"Rate limit exceeded for {api_name}")
            
            # Execute primary function
            result = primary_func(*args, **kwargs)
            
            # Track successful call
            self._track_api_call(api_name, time.time() - start_time, success=True)
            
            return result
            
        except Exception as e:
            # Track failed call
            self._track_api_call(api_name, time.time() - start_time, success=False)
            
            logger.error(f"Google API {api_name} failed: {e}")
            
            # Try fallback if available
            if fallback_func and self.fallback_enabled:
                logger.info(f"Using fallback for {api_name}")
                return fallback_func(*args, **kwargs)
            else:
                raise e
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """Check if API call is within rate limits"""
        if api_name not in self.rate_limits:
            return True
        
        stats = self.usage_stats.get(api_name)
        if not stats:
            return True
        
        # Simple rate limiting - can be enhanced with sliding window
        current_time = datetime.now()
        if stats.last_call and current_time - stats.last_call < timedelta(seconds=1):
            return False
        
        return True
    
    def _track_api_call(self, api_name: str, response_time: float, success: bool = True):
        """Track API call statistics"""
        if api_name not in self.usage_stats:
            self.usage_stats[api_name] = APIUsageStats(api_name)
        
        stats = self.usage_stats[api_name]
        stats.calls_made += 1
        stats.last_call = datetime.now()
        
        if success:
            # Update average response time
            if stats.average_response_time == 0:
                stats.average_response_time = response_time
            else:
                stats.average_response_time = (stats.average_response_time + response_time) / 2
        else:
            stats.errors += 1
        
        # Estimate cost (simplified)
        cost_per_call = self._get_cost_per_call(api_name)
        stats.cost_estimate += cost_per_call
    
    def _get_cost_per_call(self, api_name: str) -> float:
        """Get estimated cost per API call"""
        cost_mapping = {
            'search_console': 0.0,  # Free
            'knowledge_graph': 0.0005,  # $0.50 per 1K queries
            'custom_search': 0.005,  # $5 per 1K queries
            'natural_language': 0.001,  # $1 per 1K units
            'gemini': 0.002  # Variable, estimated
        }
        return cost_mapping.get(api_name, 0.001)
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get comprehensive usage report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'apis': {},
            'total_calls': 0,
            'total_errors': 0,
            'total_cost_estimate': 0.0
        }
        
        for api_name, stats in self.usage_stats.items():
            report['apis'][api_name] = {
                'calls_made': stats.calls_made,
                'errors': stats.errors,
                'error_rate': stats.errors / max(stats.calls_made, 1),
                'average_response_time': stats.average_response_time,
                'cost_estimate': stats.cost_estimate,
                'last_call': stats.last_call.isoformat() if stats.last_call else None
            }
            
            report['total_calls'] += stats.calls_made
            report['total_errors'] += stats.errors
            report['total_cost_estimate'] += stats.cost_estimate
        
        return report
    
    def enable_fallback(self, enabled: bool = True):
        """Enable or disable fallback to SerpAPI"""
        self.fallback_enabled = enabled
        logger.info(f"Fallback mechanism {'enabled' if enabled else 'disabled'}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all API clients"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'apis': {}
        }
        
        for api_name, client in self.api_clients.items():
            try:
                # Try a simple health check call
                if hasattr(client, 'health_check'):
                    client.health_check()
                    health_status['apis'][api_name] = {
                        'status': 'healthy',
                        'last_successful_call': self.usage_stats[api_name].last_call.isoformat() 
                                               if self.usage_stats[api_name].last_call else None
                    }
                else:
                    health_status['apis'][api_name] = {
                        'status': 'unknown',
                        'note': 'No health check method available'
                    }
            except Exception as e:
                health_status['apis'][api_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        
        return health_status

# Global instance
google_api_manager = GoogleAPIManager()
