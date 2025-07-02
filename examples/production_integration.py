"""
Production-ready integration for your existing application
This shows how to replace SerpAPI calls with Google APIs in your current codebase
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Load environment variables
load_dotenv()

from utils.google_apis.migration_manager import migration_manager


class ProductionSEOIntegration:
    """
    Drop-in replacement for your existing SerpAPI integration
    
    This class provides the same methods you're currently using with SerpAPI
    but uses Google APIs underneath with automatic fallback.
    """
    
    def __init__(self):
        self.migration_manager = migration_manager
    
    # EXISTING METHOD SIGNATURES - Replace your SerpAPI calls with these
    
    def get_google_results(self, query, location="United States", num_results=10):
        """
        Replace your existing SerpAPI google results call
        
        OLD: serpapi_client.get_google_results(query, location)
        NEW: seo_integration.get_google_results(query, location)
        """
        try:
            # This will use Google Custom Search API first, then fallback to SerpAPI
            serp_data = self.migration_manager.get_serp_data(
                query=query,
                location=location,
                use_google_apis=True
            )
            
            # Convert to your existing format
            results = {
                'search_metadata': {
                    'status': 'Success',
                    'query': query,
                    'location': location,
                    'data_source': serp_data.get('data_source', 'google_apis')
                },
                'organic_results': serp_data.get('organic_results', []),
                'total_results': serp_data.get('total_results', 0),
                'related_searches': [],  # Can be enhanced later
                'pagination': serp_data.get('pagination', {})
            }
            
            return results
            
        except Exception as e:
            print(f"Error in get_google_results: {e}")
            return {'error': str(e)}
    
    def get_serp_analysis(self, keyword, domain=None):
        """
        Enhanced SERP analysis - NEW functionality not available in SerpAPI
        
        This provides deeper analysis than SerpAPI including:
        - SERP features analysis
        - Competitor positioning
        - Content gap analysis
        """
        try:
            from utils.google_apis.custom_search_client import CustomSearchClient
            
            custom_search = CustomSearchClient()
            
            # Get search results
            search_results = custom_search.search(keyword, num_results=20)
            
            # Analyze SERP features
            serp_features = custom_search.analyze_serp_features(keyword)
            
            # Get competitor analysis
            competitors = custom_search.get_competitors(keyword, exclude_domain=domain)
            
            # Content gap analysis
            content_gaps = custom_search.analyze_content_gaps(keyword, domain) if domain else {}
            
            analysis = {
                'keyword': keyword,
                'domain': domain,
                'search_results': search_results,
                'serp_features': serp_features,
                'competitors': competitors,
                'content_gaps': content_gaps,
                'data_source': 'google_custom_search'
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in get_serp_analysis: {e}")
            return {'error': str(e)}
    
    def analyze_content_seo(self, content, target_keywords=None):
        """
        Advanced content analysis - NEW functionality
        
        Uses Google Natural Language API + Gemini AI for comprehensive analysis
        """
        try:
            # Enhanced content analysis with Google APIs
            analysis = self.migration_manager.analyze_content(
                content=content,
                enhanced_analysis=True
            )
            
            # Add keyword analysis if provided
            if target_keywords:
                from utils.google_apis.natural_language_client import NaturalLanguageClient
                nl_client = NaturalLanguageClient()
                
                # Get content suggestions
                suggestions = nl_client.suggest_content_improvements(content, target_keywords)
                analysis['keyword_optimization'] = suggestions
            
            # AI-powered insights
            if 'ai_optimization' in analysis:
                analysis['ai_insights'] = analysis['ai_optimization']
            
            return analysis
            
        except Exception as e:
            print(f"Error in analyze_content_seo: {e}")
            return {'error': str(e)}
    
    def get_entity_analysis(self, content):
        """
        Entity extraction and verification - NEW functionality
        
        Uses Google Knowledge Graph to verify entities found in content
        """
        try:
            entities = self.migration_manager.extract_and_verify_entities(content)
            
            # Group entities by verification status
            verified_entities = [e for e in entities if e.get('verified', False)]
            unverified_entities = [e for e in entities if not e.get('verified', False)]
            
            return {
                'total_entities': len(entities),
                'verified_entities': verified_entities,
                'unverified_entities': unverified_entities,
                'verification_rate': len(verified_entities) / len(entities) if entities else 0,
                'authority_score': sum(e.get('confidence', 0) for e in verified_entities) / len(verified_entities) if verified_entities else 0
            }
            
        except Exception as e:
            print(f"Error in get_entity_analysis: {e}")
            return {'error': str(e)}
    
    def get_search_console_data(self, days=28):
        """
        Search Console integration - NEW functionality
        
        Get real performance data from your verified domain
        """
        try:
            from utils.google_apis.search_console_client import SearchConsoleClient
            
            sc_client = SearchConsoleClient()
            
            # Get performance data
            performance = sc_client.get_performance_data(days=days)
            
            if 'note' in performance and 'Mock data' in performance['note']:
                return {
                    'error': 'Search Console not configured',
                    'message': 'Please verify your domain in Search Console and configure credentials'
                }
            
            # Process and return data
            return {
                'date_range': performance.get('date_range'),
                'total_queries': len(performance.get('data', [])),
                'performance_data': performance.get('data', []),
                'summary': {
                    'total_clicks': sum(row.get('clicks', 0) for row in performance.get('data', [])),
                    'total_impressions': sum(row.get('impressions', 0) for row in performance.get('data', [])),
                    'average_ctr': sum(row.get('ctr', 0) for row in performance.get('data', [])) / len(performance.get('data', [])) if performance.get('data') else 0,
                    'average_position': sum(row.get('position', 0) for row in performance.get('data', [])) / len(performance.get('data', [])) if performance.get('data') else 0
                }
            }
            
        except Exception as e:
            print(f"Error in get_search_console_data: {e}")
            return {'error': str(e)}
    
    def get_ranking_data(self, keywords, domain):
        """
        Track rankings for multiple keywords - NEW functionality
        
        Monitor your domain's position for target keywords
        """
        try:
            from utils.google_apis.custom_search_client import CustomSearchClient
            
            custom_search = CustomSearchClient()
            ranking_data = custom_search.monitor_rankings(keywords, domain)
            
            return ranking_data
            
        except Exception as e:
            print(f"Error in get_ranking_data: {e}")
            return {'error': str(e)}
    
    def generate_schema_markup(self, content_type, content_data):
        """
        Generate schema markup - NEW functionality
        
        Create structured data markup for better search visibility
        """
        try:
            from utils.google_apis.schema_validator import SchemaValidator
            
            schema_validator = SchemaValidator()
            schema_suggestions = schema_validator.suggest_schema_markup(content_type, content_data)
            
            return schema_suggestions
            
        except Exception as e:
            print(f"Error in generate_schema_markup: {e}")
            return {'error': str(e)}
    
    def optimize_for_ai_search(self, content, target_query):
        """
        AI Search optimization - NEW functionality
        
        Optimize content for Google AI Overviews and SGE
        """
        try:
            from utils.google_apis.gemini_client import GeminiClient
            
            gemini_client = GeminiClient()
            
            # AI Overview optimization
            ai_optimization = gemini_client.optimize_for_ai_overview(content, target_query)
            
            # Featured snippet optimization
            snippet_optimization = gemini_client.suggest_featured_snippet_optimization(content, target_query)
            
            return {
                'ai_overview_optimization': ai_optimization,
                'featured_snippet_optimization': snippet_optimization,
                'implementation_priority': 'high'
            }
            
        except Exception as e:
            print(f"Error in optimize_for_ai_search: {e}")
            return {'error': str(e)}
    
    # MIGRATION STATUS AND MONITORING
    
    def check_migration_status(self):
        """
        Check the status of your migration from SerpAPI to Google APIs
        """
        try:
            migration_status = self.migration_manager.get_migration_status()
            
            return {
                'migration_health': migration_status['google_api_health'],
                'performance_metrics': migration_status['performance_metrics'],
                'recommendations': migration_status['recommendations'],
                'cost_analysis': migration_status['cost_analysis'],
                'next_steps': migration_status['next_steps']
            }
            
        except Exception as e:
            print(f"Error checking migration status: {e}")
            return {'error': str(e)}
    
    def get_api_usage_summary(self):
        """
        Get usage summary and cost analysis
        """
        try:
            from utils.google_apis.api_manager import google_api_manager
            
            usage_report = google_api_manager.get_usage_report()
            
            return {
                'total_calls': usage_report['total_calls'],
                'total_errors': usage_report['total_errors'],
                'cost_estimate': usage_report['total_cost_estimate'],
                'api_breakdown': usage_report['apis'],
                'efficiency_score': (usage_report['total_calls'] - usage_report['total_errors']) / usage_report['total_calls'] if usage_report['total_calls'] > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting usage summary: {e}")
            return {'error': str(e)}


# INTEGRATION EXAMPLE FOR YOUR EXISTING APPLICATION

def integrate_with_existing_app():
    """
    Example of how to integrate this into your existing application
    
    Replace your existing SerpAPI calls with these Google API calls
    """
    
    # Initialize the integration
    seo_integration = ProductionSEOIntegration()
    
    print("🔄 Production Integration Example")
    print("=" * 50)
    
    # 1. Replace existing SERP calls
    print("\n1. SERP Results (replaces SerpAPI)")
    
    # OLD CODE:
    # results = serpapi_client.get_google_results("python seo tools")
    
    # NEW CODE:
    results = seo_integration.get_google_results("python seo tools")
    
    if 'error' not in results:
        print(f"   ✅ Data source: {results['search_metadata']['data_source']}")
        print(f"   📊 Total results: {results['total_results']:,}")
        print(f"   🔍 Organic results: {len(results['organic_results'])}")
    else:
        print(f"   ❌ Error: {results['error']}")
    
    # 2. Enhanced SERP analysis (NEW)
    print("\n2. Enhanced SERP Analysis (NEW feature)")
    
    serp_analysis = seo_integration.get_serp_analysis("seo tools", "yoursite.com")
    
    if 'error' not in serp_analysis:
        print(f"   ✅ Competitors found: {len(serp_analysis.get('competitors', []))}")
        print(f"   🎯 SERP features detected: {len(serp_analysis.get('serp_features', {}).get('features', {}))}")
    
    # 3. Content analysis (NEW)
    print("\n3. Content Analysis (NEW feature)")
    
    sample_content = "Your content here for analysis..."
    content_analysis = seo_integration.analyze_content_seo(
        content=sample_content,
        target_keywords=["seo", "tools", "optimization"]
    )
    
    if 'error' not in content_analysis:
        print(f"   ✅ Quality score: {content_analysis.get('quality_score', 'N/A')}")
        print(f"   📝 Word count: {content_analysis.get('content_metrics', {}).get('word_count', 'N/A')}")
    
    # 4. Search Console data (NEW)
    print("\n4. Search Console Data (NEW feature)")
    
    sc_data = seo_integration.get_search_console_data(days=30)
    
    if 'error' not in sc_data:
        print(f"   ✅ Total queries: {sc_data.get('total_queries', 0)}")
        print(f"   📈 Total clicks: {sc_data.get('summary', {}).get('total_clicks', 0)}")
    else:
        print(f"   ⚠️ {sc_data.get('message', 'Search Console not configured')}")
    
    # 5. Migration status
    print("\n5. Migration Status")
    
    migration_status = seo_integration.check_migration_status()
    
    if 'error' not in migration_status:
        success_rate = migration_status['performance_metrics']['google_success_rate']
        print(f"   📊 Google APIs success rate: {success_rate:.1f}%")
        print(f"   💰 Estimated cost savings: ${migration_status.get('cost_analysis', {}).get('projected_monthly_savings', 0):.2f}/month")
    
    print("\n✅ Integration example completed!")
    print("💡 Replace your SerpAPI calls with the methods above for enhanced functionality.")


# STEP-BY-STEP MIGRATION GUIDE

def migration_checklist():
    """
    Step-by-step checklist for migrating from SerpAPI to Google APIs
    """
    
    print("📋 Migration Checklist")
    print("=" * 30)
    
    checklist = [
        "1. ✅ Install required dependencies (pip install -r requirements.txt)",
        "2. ✅ Set up Google Cloud project and enable APIs",
        "3. ✅ Create service account and download credentials",
        "4. ✅ Configure environment variables (.env file)",
        "5. ✅ Verify domain in Search Console",
        "6. ✅ Create Custom Search Engine",
        "7. ✅ Run verification script (python verify_google_apis.py)",
        "8. ✅ Update your application code to use new integration",
        "9. ✅ Test with real data",
        "10. ✅ Monitor performance and costs"
    ]
    
    for item in checklist:
        print(f"   {item}")
    
    print("\n📖 Detailed instructions: See GOOGLE_APIS_SETUP.md")
    print("🔧 Verification script: python verify_google_apis.py")
    print("🚀 Example usage: python examples/production_integration.py")


if __name__ == "__main__":
    print("🚀 Production Integration for Google APIs")
    print("This script shows how to integrate Google APIs into your existing application")
    print()
    
    # Run integration example
    integrate_with_existing_app()
    
    print("\n" + "=" * 60)
    
    # Show migration checklist
    migration_checklist()
