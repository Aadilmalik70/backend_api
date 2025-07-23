#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_phase_2_4_keyword_processor import TestPhase24KeywordProcessor

# Run just one test
def test_keyword_processing():
    print("🔍 Testing keyword processing...")
    
    test_instance = TestPhase24KeywordProcessor()
    
    # Run just the keyword processing test
    success = test_instance.test_keyword_processing()
    
    print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
    return success

if __name__ == "__main__":
    test_keyword_processing()
