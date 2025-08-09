import requests
import json

def test_competitor_analysis_fix():
    """Test the competitor analysis fix"""
    print("[TEST] Testing competitor analysis fixes")
    print("=" * 50)
    
    blueprint_url = "http://localhost:5000/api/blueprints/generate"
    
    test_data = {
        "keyword": "python machine learning tutorial",
        "num_competitors": 3
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-fix-user"
    }
    
    try:
        response = requests.post(
            blueprint_url,
            json=test_data,
            headers=headers,
            timeout=90
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result_data = response.json()
            
            print("[SUCCESS] Blueprint generation successful!")
            
            # Check competitor analysis
            competitor_analysis = result_data.get('data', {}).get('competitor_analysis')
            content_gaps = result_data.get('data', {}).get('content_gaps', {})
            content_insights = result_data.get('data', {}).get('content_insights', {})
            
            print(f"\n[COMPETITOR ANALYSIS]")
            if competitor_analysis:
                print(f"   Status: Not null")
                print(f"   Analysis Status: {competitor_analysis.get('analysis_status', 'N/A')}")
                print(f"   Total Competitors: {competitor_analysis.get('total_competitors', 0)}")
                print(f"   Successful Analyses: {competitor_analysis.get('successful_analyses', 0)}")
            else:
                print(f"   Status: Still null")
            
            print(f"\n[CONTENT GAPS]")
            print(f"   Analysis Status: {content_gaps.get('analysis_status', 'N/A')}")
            print(f"   Content Opportunities: {len(content_gaps.get('content_opportunities', []))}")
            print(f"   Format Gaps: {len(content_gaps.get('format_gaps', []))}")
            print(f"   Missing Topics: {len(content_gaps.get('missing_topics', []))}")
            print(f"   Underserved Keywords: {len(content_gaps.get('underserved_keywords', []))}")
            
            print(f"\n[CONTENT INSIGHTS]")
            print(f"   Analysis Status: {content_insights.get('analysis_status', 'N/A')}")
            print(f"   Avg Word Count: {content_insights.get('avg_word_count', 0)}")
            print(f"   Common Sections: {len(content_insights.get('common_sections', []))}")
            print(f"   Content Gaps: {len(content_insights.get('content_gaps', []))}")
            
            # Show first few items from each category
            if content_gaps.get('content_opportunities'):
                print(f"\n[SAMPLE] Content Opportunities:")
                for i, opp in enumerate(content_gaps['content_opportunities'][:3]):
                    print(f"   {i+1}. {opp}")
            
            if content_gaps.get('format_gaps'):
                print(f"\n[SAMPLE] Format Gaps:")
                for i, gap in enumerate(content_gaps['format_gaps'][:3]):
                    print(f"   {i+1}. {gap}")
            
            # Save detailed result
            with open("competitor_analysis_test_result.json", "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVE] Full result saved to competitor_analysis_test_result.json")
            
            return True
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"[ERROR] Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"[ERROR] Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("[SUITE] Competitor Analysis Fix Test")
    print("=" * 50)
    
    success = test_competitor_analysis_fix()
    
    if success:
        print("\n[SUCCESS] Competitor analysis fix test completed!")
    else:
        print("\n[FAIL] Competitor analysis fix test failed!")