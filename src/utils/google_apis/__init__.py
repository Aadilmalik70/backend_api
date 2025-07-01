"""
Google APIs Integration Package

This package provides comprehensive Google APIs integration for SEO optimization,
replacing SerpAPI dependency with native Google services.
"""

from .search_console_client import SearchConsoleClient
from .knowledge_graph_client import KnowledgeGraphClient
from .custom_search_client import CustomSearchClient
from .natural_language_client import NaturalLanguageClient
from .gemini_client import GeminiClient
from .schema_validator import SchemaValidator
from .api_manager import GoogleAPIManager

__all__ = [
    'SearchConsoleClient',
    'KnowledgeGraphClient', 
    'CustomSearchClient',
    'NaturalLanguageClient',
    'GeminiClient',
    'SchemaValidator',
    'GoogleAPIManager'
]

__version__ = '1.0.0'
