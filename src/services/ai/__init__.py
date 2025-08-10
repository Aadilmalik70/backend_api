"""
AI Services Module for SERP Strategist

Advanced AI-powered content analysis and optimization services using:
- spaCy for natural language processing
- sentence-transformers for semantic analysis  
- scikit-learn for machine learning classification
- networkx for content relationship mapping

Author: AI Infrastructure Specialist
Version: 1.0.0
"""

from .ai_manager import AIManager
from .nlp_service import NLPService
from .semantic_service import SemanticService
from .ml_service import MLService
from .graph_service import GraphService

__all__ = [
    'AIManager',
    'NLPService', 
    'SemanticService',
    'MLService',
    'GraphService'
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "AI Infrastructure Specialist"
__description__ = "Advanced AI services for content analysis and optimization"