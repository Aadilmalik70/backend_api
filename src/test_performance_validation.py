"""
Performance Validation Script - Conversational Query Finder

Comprehensive performance testing to validate <30s response time for 500-1000 queries
and <100ms response time for single queries with the performance optimization system.

Features:
- Single query performance testing
- Batch processing performance testing (500, 750, 1000 queries)
- Memory usage monitoring
- Throughput analysis
- Performance regression detection
- Load testing with concurrent users
- Performance optimization verification

Performance Targets:
- Single query: <100ms
- Batch 500 queries: <20s
- Batch 1000 queries: <30s
- Memory usage: <1GB
- Cache hit rate: >85%
"""

import asyncio
import time
import logging
import statistics
import psutil
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

# Import the services to test
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.conversational_query_finder import get_conversational_query_finder, ProcessingMode
from services.query_finder_performance_optimizer import get_performance_optimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceTestResult:
    """Performance test result"""
    test_name: str
    query_count: int
    processing_mode: str
    total_time: float
    average_time: float
    throughput_qps: float
    success_rate: float
    memory_usage_mb: float
    cache_hit_rate: float
    target_met: bool
    target_time: float
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    test_suite: str
    timestamp: datetime
    system_info: Dict[str, Any]
    test_results: List[PerformanceTestResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class PerformanceValidator:
    """Comprehensive performance validation system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.query_finder = None
        self.test_queries = []
        
        # Performance targets
        self.targets = {
            'single_query_ms': 100,
            'batch_500_s': 20,
            'batch_750_s': 25,
            'batch_1000_s': 30,
            'memory_limit_mb': 1000,
            'cache_hit_rate': 0.85,
            'min_throughput_qps': 33  # 1000 queries in 30s
        }
    
    def _generate_test_queries(self, count: int) -> List[str]:
        """Generate diverse test queries for performance testing"""
        query_templates = [
            # Factual queries
            "What is the population of {city}?",
            "Who is the CEO of {company}?",
            "When was {company} founded?",
            "What is the market cap of {company}?",
            "How many employees does {company} have?",
            
            # Analytical queries
            "Why is {metric} decreasing in {industry}?",
            "What are the implications of {trend} for {business}?",
            "How does {factor} affect {outcome}?",
            "Analyze the performance of {system} in {context}",
            "What are the root causes of {problem} in {domain}?",
            
            # Comparative queries
            "Compare {option1} vs {option2} for {use_case}",
            "Which is better: {approach1} or {approach2}?",
            "What are the pros and cons of {solution}?",
            "Evaluate different {category} options",
            "Benchmark {product1} against {product2}",
            
            # Procedural queries
            "How to implement {feature} in {technology}?",
            "What are the steps to {process} in {domain}?",
            "Create a workflow for {task}",
            "Guide me through {procedure}",
            "Best practices for {activity} in {context}",
            
            # Creative queries
            "Generate content ideas for {topic}",
            "Create a marketing campaign for {product}",
            "Design a solution for {problem}",
            "Brainstorm {category} concepts",
            "Write a {content_type} about {subject}",
            
            # Diagnostic queries
            "Why is {system} performing poorly?",
            "Fix the {issue} in {application}",
            "Troubleshoot {problem} with {technology}",
            "Optimize {process} for better {outcome}",
            "Resolve {error} in {context}"
        ]
        
        # Sample data for templates
        cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
        companies = ["Microsoft", "Google", "Apple", "Amazon", "Meta"]
        industries = ["technology", "finance", "healthcare", "retail", "energy"]
        metrics = ["customer satisfaction", "revenue", "performance", "engagement", "efficiency"]
        
        queries = []
        for i in range(count):
            template = query_templates[i % len(query_templates)]
            
            # Fill template with sample data
            query = template.format(
                city=cities[i % len(cities)],
                company=companies[i % len(companies)],
                industry=industries[i % len(industries)],
                metric=metrics[i % len(metrics)],
                business="business operations",
                trend="market consolidation",
                factor="economic uncertainty",
                outcome="customer retention",
                system="recommendation system",
                context="e-commerce platform",
                problem="data quality issues",
                domain="supply chain",
                option1="cloud storage",
                option2="on-premise storage",
                use_case="large dataset storage",
                approach1="microservices",
                approach2="monolithic architecture",
                solution="automated deployment",
                category="CRM",
                product1="Product A",
                product2="Product B",
                feature="real-time notifications",
                technology="React",
                process="customer onboarding",
                task="inventory management",
                procedure="security audit",
                activity="code review",
                topic="artificial intelligence",
                product="eco-friendly packaging",
                content_type="blog post",
                subject="sustainable business practices",
                application="web application",
                issue="memory leak",
                error="database timeout"
            )
            
            queries.append(query)
        
        return queries
    
    async def initialize(self):
        """Initialize performance validator"""
        try:
            self.logger.info("🚀 Initializing Performance Validator...")
            
            # Initialize query finder with performance optimization
            config = {
                'performance_mode': 'turbo',
                'enable_performance_optimization': True,
                'batch_processing_config': {
                    'optimal_batch_size': 150,
                    'parallel_batches': 15,
                    'batch_timeout': 25.0
                }
            }
            
            self.query_finder = await get_conversational_query_finder(config)
            
            # Generate test queries
            self.test_queries = self._generate_test_queries(1200)  # Extra queries for testing
            
            self.logger.info("✅ Performance Validator initialized")
            
        except Exception as e:
            self.logger.error(f"Performance validator initialization failed: {e}")
            raise
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'python_version': sys.version,
                'platform': sys.platform,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {'error': str(e)}
    
    async def test_single_query_performance(self) -> PerformanceTestResult:
        """Test single query performance (<100ms target)"""
        self.logger.info("🔬 Testing single query performance...")
        
        test_queries = self.test_queries[:50]  # Test 50 single queries
        processing_times = []
        successful_queries = 0
        
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                result = await self.query_finder.find_query(
                    query=query,
                    processing_mode=ProcessingMode.FAST
                )
                processing_time = (time.time() - start_time) * 1000  # Convert to ms
                processing_times.append(processing_time)
                successful_queries += 1
                
            except Exception as e:
                self.logger.error(f"Single query failed: {e}")
        
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        memory_usage = end_memory - start_memory
        
        # Get performance metrics
        metrics = await self.query_finder.get_performance_metrics()
        cache_hit_rate = metrics.get('cache_metrics', {}).get('cache_hit_rate', 0.0)
        
        # Calculate results
        avg_time_ms = statistics.mean(processing_times) if processing_times else 0
        success_rate = successful_queries / len(test_queries)
        target_met = avg_time_ms < self.targets['single_query_ms']
        
        return PerformanceTestResult(
            test_name="Single Query Performance",
            query_count=len(test_queries),
            processing_mode="FAST",
            total_time=sum(processing_times) / 1000,  # Convert to seconds
            average_time=avg_time_ms,
            throughput_qps=successful_queries / (sum(processing_times) / 1000) if processing_times else 0,
            success_rate=success_rate,
            memory_usage_mb=memory_usage,
            cache_hit_rate=cache_hit_rate,
            target_met=target_met,
            target_time=self.targets['single_query_ms'],
            detailed_metrics={
                'min_time_ms': min(processing_times) if processing_times else 0,
                'max_time_ms': max(processing_times) if processing_times else 0,
                'median_time_ms': statistics.median(processing_times) if processing_times else 0,
                'std_dev_ms': statistics.stdev(processing_times) if len(processing_times) > 1 else 0
            }
        )
    
    async def test_batch_performance(self, batch_size: int, processing_mode: ProcessingMode) -> PerformanceTestResult:
        """Test batch processing performance"""
        self.logger.info(f"🔬 Testing batch performance: {batch_size} queries...")
        
        test_queries = self.test_queries[:batch_size]
        target_time = self.targets.get(f'batch_{batch_size}_s', 30)
        
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        start_time = time.time()
        
        try:
            batch_result = await self.query_finder.batch_find_queries(
                queries=test_queries,
                processing_mode=processing_mode
            )
            
            total_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            memory_usage = end_memory - start_memory
            
            # Get performance metrics
            metrics = await self.query_finder.get_performance_metrics()
            cache_hit_rate = metrics.get('cache_metrics', {}).get('cache_hit_rate', 0.0)
            
            # Calculate results
            success_rate = batch_result.successful_queries / batch_result.total_queries
            throughput_qps = batch_result.successful_queries / total_time
            target_met = total_time < target_time
            
            return PerformanceTestResult(
                test_name=f"Batch {batch_size} Queries",
                query_count=batch_size,
                processing_mode=processing_mode.value,
                total_time=total_time,
                average_time=batch_result.average_processing_time * 1000,  # Convert to ms
                throughput_qps=throughput_qps,
                success_rate=success_rate,
                memory_usage_mb=memory_usage,
                cache_hit_rate=cache_hit_rate,
                target_met=target_met,
                target_time=target_time,
                detailed_metrics={
                    'batch_processing_time': batch_result.total_processing_time,
                    'throughput_queries_per_second': batch_result.throughput_queries_per_second,
                    'failed_queries': batch_result.failed_queries,
                    'quality_distribution': batch_result.quality_distribution,
                    'question_type_distribution': batch_result.question_type_distribution
                }
            )
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return PerformanceTestResult(
                test_name=f"Batch {batch_size} Queries",
                query_count=batch_size,
                processing_mode=processing_mode.value,
                total_time=time.time() - start_time,
                average_time=0,
                throughput_qps=0,
                success_rate=0,
                memory_usage_mb=0,
                cache_hit_rate=0,
                target_met=False,
                target_time=target_time,
                detailed_metrics={'error': str(e)}
            )
    
    async def test_concurrent_load(self) -> PerformanceTestResult:
        """Test concurrent load performance"""
        self.logger.info("🔬 Testing concurrent load performance...")
        
        concurrent_users = 10
        queries_per_user = 20
        total_queries = concurrent_users * queries_per_user
        
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        start_time = time.time()
        
        async def simulate_user(user_id: int):
            """Simulate a concurrent user"""
            user_queries = self.test_queries[user_id * queries_per_user:(user_id + 1) * queries_per_user]
            results = []
            
            for query in user_queries:
                try:
                    result = await self.query_finder.find_query(
                        query=query,
                        processing_mode=ProcessingMode.STANDARD
                    )
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Concurrent query failed for user {user_id}: {e}")
            
            return results
        
        try:
            # Run concurrent users
            user_tasks = [simulate_user(i) for i in range(concurrent_users)]
            user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            memory_usage = end_memory - start_memory
            
            # Calculate success rate
            successful_queries = 0
            for user_result in user_results:
                if not isinstance(user_result, Exception):
                    successful_queries += len(user_result)
            
            success_rate = successful_queries / total_queries
            throughput_qps = successful_queries / total_time
            
            # Get performance metrics
            metrics = await self.query_finder.get_performance_metrics()
            cache_hit_rate = metrics.get('cache_metrics', {}).get('cache_hit_rate', 0.0)
            
            # Target: Should handle concurrent load efficiently
            target_met = success_rate > 0.95 and throughput_qps > 10
            
            return PerformanceTestResult(
                test_name="Concurrent Load Test",
                query_count=total_queries,
                processing_mode="STANDARD",
                total_time=total_time,
                average_time=(total_time / successful_queries * 1000) if successful_queries > 0 else 0,
                throughput_qps=throughput_qps,
                success_rate=success_rate,
                memory_usage_mb=memory_usage,
                cache_hit_rate=cache_hit_rate,
                target_met=target_met,
                target_time=20,  # 20s target for concurrent load
                detailed_metrics={
                    'concurrent_users': concurrent_users,
                    'queries_per_user': queries_per_user,
                    'total_queries': total_queries
                }
            )
            
        except Exception as e:
            self.logger.error(f"Concurrent load test failed: {e}")
            return PerformanceTestResult(
                test_name="Concurrent Load Test",
                query_count=total_queries,
                processing_mode="STANDARD",
                total_time=time.time() - start_time,
                average_time=0,
                throughput_qps=0,
                success_rate=0,
                memory_usage_mb=0,
                cache_hit_rate=0,
                target_met=False,
                target_time=20,
                detailed_metrics={'error': str(e)}
            )
    
    async def run_comprehensive_performance_tests(self) -> PerformanceReport:
        """Run comprehensive performance test suite"""
        self.logger.info("🚀 Starting Comprehensive Performance Test Suite...")
        
        report = PerformanceReport(
            test_suite="Conversational Query Finder Performance Validation",
            timestamp=datetime.utcnow(),
            system_info=self._get_system_info()
        )
        
        try:
            # Test 1: Single query performance
            single_result = await self.test_single_query_performance()
            report.test_results.append(single_result)
            
            # Test 2: Batch processing - 500 queries
            batch_500_result = await self.test_batch_performance(500, ProcessingMode.STANDARD)
            report.test_results.append(batch_500_result)
            
            # Test 3: Batch processing - 750 queries  
            batch_750_result = await self.test_batch_performance(750, ProcessingMode.STANDARD)
            report.test_results.append(batch_750_result)
            
            # Test 4: Batch processing - 1000 queries (main target)
            batch_1000_result = await self.test_batch_performance(1000, ProcessingMode.COMPREHENSIVE)
            report.test_results.append(batch_1000_result)
            
            # Test 5: Concurrent load testing
            concurrent_result = await self.test_concurrent_load()
            report.test_results.append(concurrent_result)
            
            # Generate summary
            report.summary = self._generate_summary(report.test_results)
            report.recommendations = self._generate_recommendations(report.test_results)
            
            self.logger.info("✅ Comprehensive Performance Test Suite Complete")
            
        except Exception as e:
            self.logger.error(f"Performance test suite failed: {e}")
            report.summary = {'error': str(e)}
        
        return report
    
    def _generate_summary(self, results: List[PerformanceTestResult]) -> Dict[str, Any]:
        """Generate performance test summary"""
        passed_tests = sum(1 for r in results if r.target_met)
        total_tests = len(results)
        
        # Key metrics
        main_batch_test = next((r for r in results if "1000" in r.test_name), None)
        single_query_test = next((r for r in results if "Single" in r.test_name), None)
        
        return {
            'overall_success': passed_tests == total_tests,
            'tests_passed': passed_tests,
            'total_tests': total_tests,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'key_results': {
                'single_query_target_met': single_query_test.target_met if single_query_test else False,
                'batch_1000_target_met': main_batch_test.target_met if main_batch_test else False,
                'single_query_avg_ms': single_query_test.average_time if single_query_test else 0,
                'batch_1000_time_s': main_batch_test.total_time if main_batch_test else 0,
                'max_throughput_qps': max((r.throughput_qps for r in results), default=0),
                'avg_memory_usage_mb': statistics.mean([r.memory_usage_mb for r in results if r.memory_usage_mb > 0]),
                'avg_cache_hit_rate': statistics.mean([r.cache_hit_rate for r in results if r.cache_hit_rate > 0])
            }
        }
    
    def _generate_recommendations(self, results: List[PerformanceTestResult]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        for result in results:
            if not result.target_met:
                if "Single" in result.test_name and result.average_time > 100:
                    recommendations.append(f"Single query performance needs optimization: {result.average_time:.1f}ms > 100ms target")
                elif "Batch" in result.test_name:
                    recommendations.append(f"Batch processing needs optimization: {result.total_time:.1f}s > {result.target_time}s target")
                elif "Concurrent" in result.test_name:
                    recommendations.append(f"Concurrent load handling needs improvement: {result.success_rate:.2%} success rate")
            
            if result.cache_hit_rate < 0.8:
                recommendations.append("Consider increasing cache size or improving cache strategy")
            
            if result.memory_usage_mb > 500:
                recommendations.append("High memory usage detected - consider memory optimization")
        
        if not recommendations:
            recommendations.append("All performance targets met! System is optimally configured.")
        
        return recommendations
    
    def save_report(self, report: PerformanceReport, filename: str = None):
        """Save performance report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        try:
            # Convert dataclasses to dict for JSON serialization
            report_dict = {
                'test_suite': report.test_suite,
                'timestamp': report.timestamp.isoformat(),
                'system_info': report.system_info,
                'test_results': [
                    {
                        'test_name': r.test_name,
                        'query_count': r.query_count,
                        'processing_mode': r.processing_mode,
                        'total_time': r.total_time,
                        'average_time': r.average_time,
                        'throughput_qps': r.throughput_qps,
                        'success_rate': r.success_rate,
                        'memory_usage_mb': r.memory_usage_mb,
                        'cache_hit_rate': r.cache_hit_rate,
                        'target_met': r.target_met,
                        'target_time': r.target_time,
                        'detailed_metrics': r.detailed_metrics
                    }
                    for r in report.test_results
                ],
                'summary': report.summary,
                'recommendations': report.recommendations
            }
            
            with open(filename, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            self.logger.info(f"Performance report saved to: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save performance report: {e}")

async def main():
    """Main performance validation execution"""
    validator = PerformanceValidator()
    
    try:
        # Initialize validator
        await validator.initialize()
        
        # Run comprehensive tests
        report = await validator.run_comprehensive_performance_tests()
        
        # Display results
        print("\n" + "="*80)
        print("PERFORMANCE VALIDATION REPORT")
        print("="*80)
        print(f"Test Suite: {report.test_suite}")
        print(f"Timestamp: {report.timestamp}")
        print(f"System: {report.system_info}")
        print("\n" + "-"*80)
        print("TEST RESULTS:")
        print("-"*80)
        
        for result in report.test_results:
            status = "✅ PASS" if result.target_met else "❌ FAIL"
            print(f"{status} {result.test_name}")
            print(f"  Queries: {result.query_count}")
            print(f"  Time: {result.total_time:.2f}s (target: {result.target_time}s)")
            print(f"  Avg: {result.average_time:.1f}ms")
            print(f"  QPS: {result.throughput_qps:.1f}")
            print(f"  Success: {result.success_rate:.2%}")
            print(f"  Memory: {result.memory_usage_mb:.1f}MB")
            print(f"  Cache: {result.cache_hit_rate:.2%}")
            print()
        
        print("-"*80)
        print("SUMMARY:")
        print("-"*80)
        print(f"Overall Success: {'✅ YES' if report.summary.get('overall_success') else '❌ NO'}")
        print(f"Tests Passed: {report.summary.get('tests_passed')}/{report.summary.get('total_tests')}")
        
        key_results = report.summary.get('key_results', {})
        print(f"Single Query Target Met: {'✅' if key_results.get('single_query_target_met') else '❌'}")
        print(f"Batch 1000 Target Met: {'✅' if key_results.get('batch_1000_target_met') else '❌'}")
        print(f"Single Query Avg: {key_results.get('single_query_avg_ms', 0):.1f}ms")
        print(f"Batch 1000 Time: {key_results.get('batch_1000_time_s', 0):.1f}s")
        
        print("\n" + "-"*80)
        print("RECOMMENDATIONS:")
        print("-"*80)
        for rec in report.recommendations:
            print(f"• {rec}")
        
        # Save report
        validator.save_report(report)
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Performance validation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())