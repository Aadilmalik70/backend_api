"""
Enhanced Keyword Processor with Real Data Integration - Compatibility Layer

This module provides backward compatibility for the refactored keyword processor.
The original large file has been split into focused modules for better maintainability.

Import the main class from the new modular structure.
"""

# Import from the refactored module structure
from .keyword_processing.keyword_processor import KeywordProcessorEnhancedReal

# For backward compatibility, also expose the component classes
from .keyword_processing.keyword_extractor import KeywordExtractor
from .keyword_processing.score_calculator import ScoreCalculator
from .keyword_processing.trend_analyzer import TrendAnalyzer

# Maintain the same interface as before
__all__ = [
    'KeywordProcessorEnhancedReal',
    'KeywordExtractor',
    'ScoreCalculator', 
    'TrendAnalyzer'
]
