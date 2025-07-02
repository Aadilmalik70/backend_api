"""
Real-world usage examples for Google APIs integration
Shows how to use the APIs in your application with real data
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Load environment variables
load_dotenv()

from utils.google_apis.migration_manager import migration_manager
from utils.google_apis.api_manager import google_api_manager


class SEOAnalyzer:
    """
    Production-ready SEO analyzer using Google APIs
    
    This replaces your SerpAPI usage with Google APIs while maintaining
    the same interface but with enhanced functionality.
    """
    
    def __init__(self):
        self.migration_manager = migration_manager
        self.api_manager = google_api_manager
    
    def analyze_serp_for_keyword(self, keyword, location="United States"):
        """
        Analyze SERP for a specific keyword - REAL DATA
        
        Args:
            keyword: Target keyword to analyze
            location: Geographic location for search
            
        Returns:
            dict: SERP analysis with competitor data, features, etc.
        """
        print(f"🔍 Analyzing SERP for: '{keyword}'")
        
        try:
            # Get SERP data using Google Custom Search
            serp_data = self.migration_manager.get_serp_data(
                query=keyword,
                location=location,
                use_google_apis=True
            )
            
            # Analyze SERP features
            from utils.google_apis.custom_search_client import CustomSearchClient
            custom_search = CustomSearchClient()
            serp_features = custom_search.analyze_serp_features(keyword)
            
            # Combine results
            analysis = {
                'keyword': keyword,
                'location': location,
                'data_source': serp_data.get('data_source', 'unknown'),
                'total_results': serp_data.get('total_results', 0),
                'organic_results': serp_data.get('organic_results', []),
                'serp_features': serp_features,
                'competitor_count': len(serp_data.get('organic_results', [])),
                'analysis_timestamp': serp_data.get('timestamp')
            }
            
            print(f"✅ Found {len(analysis['organic_results'])} organic results")
            print(f"📊 Data source: {analysis['data_source']}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ SERP analysis failed: {e}")
            return None
    
    def get_competitor_analysis(self, keyword, your_domain=None, limit=10):
        """
        Get competitor analysis for a keyword - REAL DATA
        
        Args:
            keyword: Target keyword
            your_domain: Your domain to exclude from competitors
            limit: Number of competitors to analyze
            
        Returns:
            list: Competitor analysis data
        """
        print(f"🏢 Analyzing competitors for: '{keyword}'")
        
        try:
            competitors = self.migration_manager.get_competitors(
                query=keyword,
                exclude_domain=your_domain,
                limit=limit
            )
            
            # Enhance competitor data
            enhanced_competitors = []
            for competitor in competitors:
                enhanced_competitor = {
                    **competitor,
                    'keyword': keyword,
                    'analysis_type': 'organic_competitor',
                    'market_share_estimate': self._estimate_market_share(competitor.get('position', 100)),
                    'threat_level': self._assess_threat_level(competitor)
                }
                enhanced_competitors.append(enhanced_competitor)
            
            print(f"✅ Found {len(enhanced_competitors)} competitors")
            return enhanced_competitors
            
        except Exception as e:
            print(f"❌ Competitor analysis failed: {e}")
            return []
    
    def analyze_content_for_seo(self, content, target_keywords=None):
        """
        Comprehensive content analysis for SEO - REAL DATA
        
        Args:
            content: Content to analyze
            target_keywords: List of target keywords
            
        Returns:
            dict: Comprehensive content analysis
        """
        print("📝 Analyzing content for SEO optimization...")
        
        try:
            # Get enhanced content analysis
            analysis = self.migration_manager.analyze_content(
                content=content,
                enhanced_analysis=True
            )
            
            # Add keyword analysis if provided
            if target_keywords:
                analysis['keyword_analysis'] = self._analyze_keyword_usage(content, target_keywords)
            
            # Get AI optimization suggestions
            if 'ai_optimization' in analysis:
                print("🤖 AI optimization insights included")
            
            # Extract and verify entities
            entities = self.migration_manager.extract_and_verify_entities(content)
            verified_entities = [e for e in entities if e.get('verified', False)]
            
            analysis['entity_verification'] = {
                'total_entities': len(entities),
                'verified_entities': len(verified_entities),
                'entities': entities
            }
            
            print(f"✅ Content analysis complete")
            print(f"📊 Quality score: {analysis.get('quality_score', 'N/A')}")
            print(f"🔍 Entities found: {len(entities)} ({len(verified_entities)} verified)")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Content analysis failed: {e}")
            return None
    
    def get_search_console_performance(self, days=28):
        """
        Get Search Console performance data - REAL DATA
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Search Console performance data
        """
        print(f"📊 Getting Search Console data for last {days} days...")
        
        try:
            from utils.google_apis.search_console_client import SearchConsoleClient
            sc_client = SearchConsoleClient()
            
            # Get performance data
            performance = sc_client.get_performance_data()
            
            if 'note' in performance and 'Mock data' in performance['note']:
                print("⚠️ Getting mock data - configure Search Console for real data")
                return None
            
            # Get top queries
            top_queries = []
            for row in performance.get('data', [])[:10]:
                if len(row.get('keys', [])) > 0:
                    top_queries.append({
                        'query': row['keys'][0],
                        'clicks': row.get('clicks', 0),
                        'impressions': row.get('impressions', 0),
                        'ctr': row.get('ctr', 0),
                        'position': row.get('position', 0)
                    })
            
            summary = {
                'date_range': performance.get('date_range'),
                'total_queries': len(performance.get('data', [])),
                'total_clicks': sum(row.get('clicks', 0) for row in performance.get('data', [])),
                'total_impressions': sum(row.get('impressions', 0) for row in performance.get('data', [])),
                'top_queries': top_queries
            }
            
            print(f"✅ Search Console data retrieved")
            print(f"📈 Total clicks: {summary['total_clicks']}")
            print(f"👀 Total impressions: {summary['total_impressions']}")
            
            return summary
            
        except Exception as e:
            print(f"❌ Search Console data failed: {e}")
            return None
    
    def generate_seo_report(self, keyword, your_domain=None):
        """
        Generate comprehensive SEO report - REAL DATA
        
        Args:
            keyword: Primary keyword to analyze
            your_domain: Your domain for competitor exclusion
            
        Returns:
            dict: Comprehensive SEO report
        """
        print(f"📋 Generating SEO report for: '{keyword}'")
        
        # Get all data
        serp_analysis = self.analyze_serp_for_keyword(keyword)
        competitors = self.get_competitor_analysis(keyword, your_domain)
        search_console = self.get_search_console_performance()
        
        # Generate summary
        report = {
            'keyword': keyword,
            'domain': your_domain,
            'generated_at': self._get_timestamp(),
            'serp_analysis': serp_analysis,
            'competitor_analysis': {
                'total_competitors': len(competitors),
                'top_competitors': competitors[:5],
                'market_insights': self._generate_market_insights(competitors)
            },
            'search_console_performance': search_console,
            'recommendations': self._generate_recommendations(serp_analysis, competitors)
        }
        
        print("✅ SEO report generated successfully")
        return report
    
    def get_api_usage_stats(self):
        """Get usage statistics for all APIs"""
        try:
            usage_report = self.api_manager.get_usage_report()
            migration_status = self.migration_manager.get_migration_status()
            
            stats = {
                'total_calls': usage_report.get('total_calls', 0),
                'google_api_calls': migration_status['performance_metrics']['google_api_calls'],
                'serpapi_fallbacks': migration_status['performance_metrics']['serpapi_fallbacks'],
                'success_rate': migration_status['performance_metrics']['google_success_rate'],
                'cost_estimate': usage_report.get('total_cost_estimate', 0),
                'apis_health': migration_status['google_api_health']
            }
            
            return stats
        except Exception as e:
            print(f"❌ Usage stats failed: {e}")
            return {}
    
    # Helper methods
    def _estimate_market_share(self, position):
        """Estimate market share based on SERP position"""
        # Simplified CTR estimates
        ctr_estimates = {1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.06}
        return ctr_estimates.get(position, 0.02)
    
    def _assess_threat_level(self, competitor):
        """Assess competitor threat level"""
        position = competitor.get('position', 100)
        if position <= 3:
            return 'high'
        elif position <= 10:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_keyword_usage(self, content, keywords):
        """Analyze keyword usage in content"""
        content_lower = content.lower()
        analysis = {}
        
        for keyword in keywords:
            count = content_lower.count(keyword.lower())
            density = (count * len(keyword.split())) / len(content.split()) * 100
            analysis[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
        
        return analysis
    
    def _generate_market_insights(self, competitors):
        """Generate market insights from competitor data"""
        if not competitors:
            return []
        
        insights = []
        
        # Domain diversity
        domains = set(c.get('domain', '') for c in competitors)
        insights.append(f"Market dominated by {len(domains)} unique domains")
        
        # Top threats
        high_threat = [c for c in competitors if c.get('threat_level') == 'high']
        if high_threat:
            insights.append(f"{len(high_threat)} high-threat competitors in top positions")
        
        return insights
    
    def _generate_recommendations(self, serp_analysis, competitors):
        """Generate SEO recommendations based on analysis"""
        recommendations = []
        
        if serp_analysis:
            # SERP-based recommendations
            total_results = serp_analysis.get('total_results', 0)
            if total_results > 1000000:
                recommendations.append("High competition keyword - consider long-tail variations")
            
            # Feature-based recommendations
            features = serp_analysis.get('serp_features', {}).get('features', {})
            if features.get('featured_snippets', {}).get('presence') == 'strong':
                recommendations.append("Optimize for featured snippets - structure content with clear answers")
        
        if competitors:
            # Competitor-based recommendations
            avg_position = sum(c.get('position', 100) for c in competitors) / len(competitors)
            if avg_position < 5:
                recommendations.append("Strong competition in top positions - focus on content differentiation")
            
            # Domain authority analysis
            competitor_domains = [c.get('domain', '') for c in competitors]
            if len(set(competitor_domains)) < len(competitor_domains) * 0.7:
                recommendations.append("Market concentration detected - opportunity for niche positioning")
        
        return recommendations
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Example usage of SEO Analyzer with real Google APIs data"""
    print("🚀 SEO Analyzer - Real Google APIs Integration Example")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SEOAnalyzer()
    
    # Example 1: Analyze SERP for a keyword
    print("\n1️⃣ SERP Analysis Example")
    serp_results = analyzer.analyze_serp_for_keyword(
        keyword="python seo tools",
        location="United States"
    )
    
    if serp_results:
        print(f"   Keyword: {serp_results['keyword']}")
        print(f"   Total Results: {serp_results['total_results']:,}")
        print(f"   Organic Results: {len(serp_results['organic_results'])}")
        print(f"   Data Source: {serp_results['data_source']}")
    
    # Example 2: Competitor Analysis
    print("\n2️⃣ Competitor Analysis Example")
    competitors = analyzer.get_competitor_analysis(
        keyword="seo tools",
        your_domain="yoursite.com",
        limit=5
    )
    
    if competitors:
        print(f"   Found {len(competitors)} competitors:")
        for i, comp in enumerate(competitors[:3], 1):
            print(f"   {i}. {comp['domain']} (Position: {comp['position']}, Threat: {comp['threat_level']})")
    
    # Example 3: Content Analysis
    print("\n3️⃣ Content Analysis Example")
    sample_content = """
    The Ultimate Guide to SEO Tools for Python Developers
    
    Search Engine Optimization (SEO) is crucial for any website's success. 
    Python developers have access to numerous SEO tools and libraries that can 
    help automate and improve their SEO efforts. This comprehensive guide covers 
    the best Python SEO tools available in 2024.
    
    Google's search algorithms continue to evolve, making it essential for 
    developers to stay updated with the latest SEO techniques and tools.
    """
    
    content_analysis = analyzer.analyze_content_for_seo(
        content=sample_content,
        target_keywords=["SEO tools", "Python", "developers"]
    )
    
    if content_analysis:
        print(f"   Quality Score: {content_analysis.get('quality_score', 'N/A')}")
        print(f"   Word Count: {content_analysis.get('content_metrics', {}).get('word_count', 'N/A')}")
        print(f"   Entities Found: {content_analysis.get('entity_verification', {}).get('total_entities', 'N/A')}")
    
    # Example 4: Search Console Performance
    print("\n4️⃣ Search Console Performance Example")
    sc_performance = analyzer.get_search_console_performance(days=30)
    
    if sc_performance:
        print(f"   Total Clicks: {sc_performance['total_clicks']:,}")
        print(f"   Total Impressions: {sc_performance['total_impressions']:,}")
        print(f"   Top Queries: {len(sc_performance['top_queries'])}")
    else:
        print("   ⚠️ Search Console not configured or no data available")
    
    # Example 5: Complete SEO Report
    print("\n5️⃣ Complete SEO Report Example")
    seo_report = analyzer.generate_seo_report(
        keyword="python seo",
        your_domain="yoursite.com"
    )
    
    if seo_report:
        print(f"   Report generated for: {seo_report['keyword']}")
        print(f"   Competitors analyzed: {seo_report['competitor_analysis']['total_competitors']}")
        print(f"   Recommendations: {len(seo_report['recommendations'])}")
    
    # Example 6: API Usage Statistics
    print("\n6️⃣ API Usage Statistics")
    usage_stats = analyzer.get_api_usage_stats()
    
    if usage_stats:
        print(f"   Total API Calls: {usage_stats.get('total_calls', 0)}")
        print(f"   Google API Calls: {usage_stats.get('google_api_calls', 0)}")
        print(f"   Success Rate: {usage_stats.get('success_rate', 0):.1f}%")
        print(f"   Estimated Cost: ${usage_stats.get('cost_estimate', 0):.4f}")
    
    print("\n✅ Example completed! Check the results above.")
    print("💡 If you see 'mock data' warnings, run verify_google_apis.py first.")


if __name__ == "__main__":
    main()
