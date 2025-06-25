#!/usr/bin/env python3
"""
Test Blueprint Generation Without Database Storage

This script tests blueprint generation functionality without requiring database storage,
which is useful for verifying the core AI generation works independently.
"""

import sys
import os
import json
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_blueprint_generation():
    """Test the blueprint generation service directly"""
    print("🧪 Testing Blueprint Generation Service (No Database)")
    print("=" * 60)
    
    try:
        from src.services.blueprint_generator import BlueprintGeneratorService
        
        # Check API keys
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not serpapi_key:
            print("❌ SERPAPI_KEY not found in environment variables")
            return False
        
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            return False
        
        print("✅ API keys found")
        
        # Initialize generator
        generator = BlueprintGeneratorService(serpapi_key, gemini_key)
        print("✅ Blueprint generator initialized")
        
        # Test with a simple keyword
        test_keyword = "content strategy"
        user_id = "test-user"
        
        print(f"\n🚀 Generating blueprint for: '{test_keyword}'")
        print("⏳ This may take 30-90 seconds...")
        
        start_time = time.time()
        
        # Generate blueprint
        blueprint_data = generator.generate_blueprint(test_keyword, user_id)
        
        generation_time = time.time() - start_time
        print(f"✅ Blueprint generated in {generation_time:.1f} seconds")
        
        # Validate the result
        if generator.validate_blueprint_data(blueprint_data):
            print("✅ Blueprint data validation passed")
        else:
            print("❌ Blueprint data validation failed")
            return False
        
        # Display blueprint summary
        print("\n📊 Blueprint Summary:")
        print(f"   Keyword: {blueprint_data.get('keyword', 'Unknown')}")
        
        competitors = blueprint_data.get('competitor_analysis', {})
        if 'top_competitors' in competitors:
            print(f"   Competitors analyzed: {len(competitors['top_competitors'])}")
        
        headings = blueprint_data.get('heading_structure', {})
        if 'h2_sections' in headings:
            print(f"   H2 sections generated: {len(headings['h2_sections'])}")
        
        topics = blueprint_data.get('topic_clusters', {})
        if 'primary_cluster' in topics:
            print(f"   Primary topics: {len(topics['primary_cluster'])}")
        
        # Save to file for inspection
        output_file = f"blueprint_test_{test_keyword.replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(blueprint_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full blueprint saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Blueprint generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the blueprint generation test"""
    print("🎯 SERP Strategist Blueprint Generation Test")
    print("(Testing without database storage)")
    print("=" * 60)
    
    success = test_blueprint_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Blueprint generation test PASSED!")
        print("\nNext steps:")
        print("1. Restart your Flask server: python src/main.py")
        print("2. Test the full API with database storage")
        print("3. Check the generated JSON file for blueprint structure")
    else:
        print("❌ Blueprint generation test FAILED!")
        print("\nTroubleshooting:")
        print("1. Check your .env file has SERPAPI_KEY and GEMINI_API_KEY")
        print("2. Verify internet connectivity")
        print("3. Check API key quotas and validity")

if __name__ == "__main__":
    main()
