#!/usr/bin/env python3
"""
Production Readiness Validation for Conversational Query API
Comprehensive validation of API security, performance, and reliability
"""

import requests
import json
import time
import threading
import concurrent.futures
from typing import Dict, Any, List
import statistics

# Test configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/queries/conversational"

class ProductionReadinessValidator:
    """Validates API production readiness across multiple dimensions"""
    
    def __init__(self):
        self.results = {
            'security_tests': {},
            'performance_tests': {},
            'reliability_tests': {},
            'scalability_tests': {},
            'overall_assessment': {}
        }
    
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Run comprehensive production readiness validation"""
        print("=== PRODUCTION READINESS VALIDATION ===")
        print(f"API Endpoint: {API_BASE}")
        print()
        
        # 1. Security validation
        self._validate_security()
        
        # 2. Performance validation
        self._validate_performance()
        
        # 3. Reliability validation
        self._validate_reliability()
        
        # 4. Scalability validation  
        self._validate_scalability()
        
        # 5. Generate overall assessment
        self._generate_assessment()
        
        return self.results
    
    def _validate_security(self):
        """Validate security measures"""
        print("1. Security Validation...")
        
        security_results = {}
        
        # Test 1.1: Authentication enforcement
        response = requests.post(f"{API_BASE}/query", json={"query": "test"})
        auth_enforced = response.status_code == 401
        security_results['authentication_enforced'] = auth_enforced
        print(f"   {'✅' if auth_enforced else '❌'} Authentication enforced: {response.status_code}")
        
        # Test 1.2: Input sanitization
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "\x00\x08\x0b\x0c\x0e\x0f",
            "A" * 3000  # Very long input
        ]
        
        headers = {'X-User-ID': 'security-test', 'X-API-Key': 'test-key-12345678901234567890123456'}
        sanitization_passed = 0
        
        for malicious_input in malicious_inputs:
            try:
                response = requests.post(f"{API_BASE}/query", 
                                       json={"query": malicious_input}, 
                                       headers=headers, timeout=10)
                # Should be rejected (400) or handled safely (200 with sanitized input)
                if response.status_code in [400, 200]:
                    sanitization_passed += 1
            except Exception:
                pass
        
        sanitization_score = sanitization_passed / len(malicious_inputs)
        security_results['input_sanitization'] = {
            'passed': sanitization_passed,
            'total': len(malicious_inputs),
            'score': sanitization_score
        }
        print(f"   {'✅' if sanitization_score >= 0.75 else '❌'} Input sanitization: {sanitization_score:.1%}")
        
        # Test 1.3: Rate limiting effectiveness
        test_user = f"rate-test-{int(time.time())}"
        test_headers = {'X-User-ID': test_user, 'X-API-Key': 'test-key-12345678901234567890123456'}
        
        # Make requests rapidly
        rate_limit_triggered = False
        for i in range(20):
            response = requests.post(f"{API_BASE}/query", 
                                   json={"query": f"rate test {i}"}, 
                                   headers=test_headers)
            if response.status_code == 429:
                rate_limit_triggered = True
                break
        
        security_results['rate_limiting'] = rate_limit_triggered
        print(f"   {'✅' if rate_limit_triggered else '❌'} Rate limiting: {rate_limit_triggered}")
        
        # Test 1.4: Error handling (no sensitive info disclosure)
        response = requests.post(f"{API_BASE}/nonexistent", json={"query": "test"}, headers=headers)
        error_safe = response.status_code == 404 and 'traceback' not in response.text.lower()
        security_results['safe_error_handling'] = error_safe
        print(f"   {'✅' if error_safe else '❌'} Safe error handling: {error_safe}")
        
        self.results['security_tests'] = security_results
    
    def _validate_performance(self):
        """Validate performance requirements"""
        print("2. Performance Validation...")
        
        performance_results = {}
        headers = {'X-User-ID': 'perf-test', 'X-API-Key': 'test-key-12345678901234567890123456'}
        
        # Test 2.1: Response times
        response_times = []
        test_queries = [
            "What is SEO optimization?",
            "How to improve website performance?",
            "Content marketing best practices",
            "Social media strategy tips",
            "Email marketing automation"
        ]
        
        for query in test_queries:
            start_time = time.time()
            try:
                response = requests.post(f"{API_BASE}/query", 
                                       json={"query": query}, 
                                       headers=headers, timeout=30)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            except Exception:
                pass
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 5 else max_response_time
            
            performance_results['response_times'] = {
                'average': avg_response_time,
                'maximum': max_response_time,
                'p95': p95_response_time,
                'samples': len(response_times)
            }
            
            # Performance targets: <2s average, <5s p95
            performance_passed = avg_response_time < 2.0 and p95_response_time < 5.0
            
            print(f"   {'✅' if performance_passed else '❌'} Response times: avg={avg_response_time:.2f}s, p95={p95_response_time:.2f}s")
        else:
            performance_results['response_times'] = {'error': 'No successful responses'}
            print("   ❌ Response times: No successful responses")
        
        # Test 2.2: Throughput
        def make_request():
            try:
                response = requests.post(f"{API_BASE}/query", 
                                       json={"query": "throughput test"}, 
                                       headers=headers, timeout=10)
                return response.status_code == 200
            except Exception:
                return False
        
        # Concurrent requests test
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            successful_requests = sum(1 for future in concurrent.futures.as_completed(futures) if future.result())
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = successful_requests / duration if duration > 0 else 0
        
        performance_results['throughput'] = {
            'requests_per_second': throughput,
            'successful_requests': successful_requests,
            'total_requests': 20,
            'duration': duration
        }
        
        throughput_passed = throughput >= 5  # Target: 5 requests/second minimum
        print(f"   {'✅' if throughput_passed else '❌'} Throughput: {throughput:.1f} req/s")
        
        self.results['performance_tests'] = performance_results
    
    def _validate_reliability(self):
        """Validate reliability and error handling"""
        print("3. Reliability Validation...")
        
        reliability_results = {}
        headers = {'X-User-ID': 'reliability-test', 'X-API-Key': 'test-key-12345678901234567890123456'}
        
        # Test 3.1: Error recovery
        error_scenarios = [
            {"query": ""},  # Empty query
            {"query": None},  # Null query  
            {},  # Missing query
            {"query": "test", "invalid_field": "value"}  # Extra fields
        ]
        
        error_handling_passed = 0
        for scenario in error_scenarios:
            try:
                response = requests.post(f"{API_BASE}/query", json=scenario, headers=headers)
                # Should handle gracefully (400 or 200 with error message)
                if 400 <= response.status_code < 500:
                    error_handling_passed += 1
            except Exception:
                pass
        
        error_handling_score = error_handling_passed / len(error_scenarios)
        reliability_results['error_handling'] = {
            'passed': error_handling_passed,
            'total': len(error_scenarios),
            'score': error_handling_score
        }
        print(f"   {'✅' if error_handling_score >= 0.75 else '❌'} Error handling: {error_handling_score:.1%}")
        
        # Test 3.2: Consistency
        consistent_responses = 0
        test_query = "What is digital marketing?"
        
        for i in range(5):
            try:
                response = requests.post(f"{API_BASE}/query", 
                                       json={"query": test_query}, 
                                       headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data and 'intent' in data['result']:
                        consistent_responses += 1
                time.sleep(1)  # Avoid rate limiting
            except Exception:
                pass
        
        consistency_score = consistent_responses / 5
        reliability_results['consistency'] = {
            'consistent_responses': consistent_responses,
            'total_tests': 5,
            'score': consistency_score
        }
        print(f"   {'✅' if consistency_score >= 0.8 else '❌'} Consistency: {consistency_score:.1%}")
        
        self.results['reliability_tests'] = reliability_results
    
    def _validate_scalability(self):
        """Validate scalability characteristics"""
        print("4. Scalability Validation...")
        
        scalability_results = {}
        
        # Test 4.1: Multiple users
        def user_simulation(user_id: str, num_requests: int):
            headers = {'X-User-ID': user_id, 'X-API-Key': 'test-key-12345678901234567890123456'}
            successful = 0
            
            for i in range(num_requests):
                try:
                    response = requests.post(f"{API_BASE}/query", 
                                           json={"query": f"user {user_id} query {i}"}, 
                                           headers=headers, timeout=15)
                    if response.status_code == 200:
                        successful += 1
                    time.sleep(0.1)  # Small delay to be reasonable
                except Exception:
                    pass
            
            return successful
        
        # Simulate 10 concurrent users, 5 requests each
        user_count = 10
        requests_per_user = 5
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = [
                executor.submit(user_simulation, f"scale-user-{i}", requests_per_user) 
                for i in range(user_count)
            ]
            user_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        total_successful = sum(user_results)
        total_requests = user_count * requests_per_user
        success_rate = total_successful / total_requests if total_requests > 0 else 0
        duration = end_time - start_time
        
        scalability_results['multi_user'] = {
            'concurrent_users': user_count,
            'requests_per_user': requests_per_user,
            'total_successful': total_successful,
            'total_requests': total_requests,
            'success_rate': success_rate,
            'duration': duration
        }
        
        scalability_passed = success_rate >= 0.8  # 80% success rate under load
        print(f"   {'✅' if scalability_passed else '❌'} Multi-user: {success_rate:.1%} success rate")
        
        # Test 4.2: Resource monitoring (if possible)
        # This would ideally check memory usage, CPU usage, etc.
        # For now, we'll check if the service remains responsive
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            service_responsive = response.status_code == 200
            scalability_results['service_responsive_after_load'] = service_responsive
            print(f"   {'✅' if service_responsive else '❌'} Service responsive after load: {service_responsive}")
        except Exception:
            scalability_results['service_responsive_after_load'] = False
            print("   ❌ Service responsive after load: False")
        
        self.results['scalability_tests'] = scalability_results
    
    def _generate_assessment(self):
        """Generate overall production readiness assessment"""
        print("5. Overall Assessment...")
        
        # Security score
        security_tests = self.results['security_tests']
        security_score = (
            (1 if security_tests.get('authentication_enforced', False) else 0) * 0.3 +
            security_tests.get('input_sanitization', {}).get('score', 0) * 0.3 +
            (1 if security_tests.get('rate_limiting', False) else 0) * 0.2 +
            (1 if security_tests.get('safe_error_handling', False) else 0) * 0.2
        )
        
        # Performance score
        performance_tests = self.results['performance_tests']
        perf_score = 0
        if 'response_times' in performance_tests and 'error' not in performance_tests['response_times']:
            rt = performance_tests['response_times']
            avg_ok = rt['average'] < 2.0
            p95_ok = rt['p95'] < 5.0
            perf_score += (0.5 if avg_ok else 0) + (0.3 if p95_ok else 0)
        
        if 'throughput' in performance_tests:
            throughput_ok = performance_tests['throughput']['requests_per_second'] >= 5
            perf_score += (0.2 if throughput_ok else 0)
        
        # Reliability score
        reliability_tests = self.results['reliability_tests']
        reliability_score = (
            reliability_tests.get('error_handling', {}).get('score', 0) * 0.6 +
            reliability_tests.get('consistency', {}).get('score', 0) * 0.4
        )
        
        # Scalability score
        scalability_tests = self.results['scalability_tests']
        scalability_score = (
            (scalability_tests.get('multi_user', {}).get('success_rate', 0)) * 0.8 +
            (1 if scalability_tests.get('service_responsive_after_load', False) else 0) * 0.2
        )
        
        # Overall score
        overall_score = (
            security_score * 0.3 +
            perf_score * 0.25 +
            reliability_score * 0.25 +
            scalability_score * 0.2
        )
        
        # Grade determination
        if overall_score >= 0.9:
            grade = "A"
            status = "PRODUCTION_READY"
        elif overall_score >= 0.8:
            grade = "B"
            status = "MOSTLY_READY"
        elif overall_score >= 0.7:
            grade = "C"
            status = "NEEDS_IMPROVEMENT"
        else:
            grade = "F"
            status = "NOT_READY"
        
        assessment = {
            'overall_score': overall_score,
            'grade': grade,
            'status': status,
            'dimension_scores': {
                'security': security_score,
                'performance': perf_score,
                'reliability': reliability_score,
                'scalability': scalability_score
            },
            'production_ready': overall_score >= 0.8,
            'recommendations': self._generate_recommendations(overall_score, {
                'security': security_score,
                'performance': perf_score,
                'reliability': reliability_score,
                'scalability': scalability_score
            })
        }
        
        self.results['overall_assessment'] = assessment
        
        print(f"\n=== PRODUCTION READINESS REPORT ===")
        print(f"Overall Score: {overall_score:.3f}")
        print(f"Grade: {grade}")
        print(f"Status: {status}")
        print(f"Production Ready: {assessment['production_ready']}")
        
        print(f"\nDimension Scores:")
        print(f"  Security: {security_score:.3f}")
        print(f"  Performance: {perf_score:.3f}")
        print(f"  Reliability: {reliability_score:.3f}")
        print(f"  Scalability: {scalability_score:.3f}")
        
        if assessment['recommendations']:
            print(f"\nRecommendations:")
            for rec in assessment['recommendations']:
                print(f"  - {rec}")
    
    def _generate_recommendations(self, overall_score: float, dimension_scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if dimension_scores['security'] < 0.8:
            recommendations.append("Improve security measures: enhance input validation and error handling")
        
        if dimension_scores['performance'] < 0.8:
            recommendations.append("Optimize performance: reduce response times and increase throughput")
        
        if dimension_scores['reliability'] < 0.8:
            recommendations.append("Enhance reliability: improve error handling and response consistency")
        
        if dimension_scores['scalability'] < 0.8:
            recommendations.append("Scale improvements: optimize for concurrent users and resource usage")
        
        if overall_score < 0.8:
            recommendations.append("Conduct load testing with realistic traffic patterns")
            recommendations.append("Implement comprehensive monitoring and alerting")
            recommendations.append("Review and enhance API documentation")
        
        return recommendations


def main():
    """Main validation execution"""
    print("Starting Production Readiness Validation...\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding at {BASE_URL}")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        return
    
    print(f"✅ Server is running at {BASE_URL}")
    print()
    
    # Run validation
    validator = ProductionReadinessValidator()
    results = validator.validate_production_readiness()
    
    # Save results
    with open('production_readiness_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Full report saved to: production_readiness_report.json")
    
    return results


if __name__ == "__main__":
    results = main()
    
    if results and results.get('overall_assessment', {}).get('production_ready', False):
        print("🎉 API is production ready!")
        exit(0)
    else:
        print("⚠️  API needs improvements before production deployment")
        exit(1)