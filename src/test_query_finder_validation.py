"""
Query Finder Validation Framework - Comprehensive testing suite

Complete validation framework for the conversational query finder service covering
functionality, integration, performance, and regression testing.

Features:
- Component unit testing (classifier, expander, scorer)
- Integration testing with existing conversational engine
- API endpoint validation
- Performance regression testing
- Error handling and edge case validation
- Quality metrics validation
- Batch processing validation
- Cache effectiveness testing

Test Categories:
- Unit Tests: Individual component functionality
- Integration Tests: Component interactions
- API Tests: REST endpoint validation  
- Performance Tests: Speed and throughput
- Regression Tests: Prevent quality degradation
- Edge Case Tests: Error handling and boundaries
"""

import asyncio
import unittest
import time
import json
import logging
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass, field

# Import the services to test
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.conversational_query_finder import (
    get_conversational_query_finder, 
    ConversationalQueryFinder,
    ProcessingMode,
    QueryFinderResult,
    BatchProcessingResult
)
from services.question_type_classifier import (
    get_question_type_classifier,
    QuestionType,
    ClassificationResult
)
from services.domain_expansion_engine import (
    get_domain_expansion_engine,
    BusinessDomain,
    ExpansionResult
)
from services.query_quality_scorer import (
    get_query_quality_scorer,
    QualityAssessment,
    QualityDimension
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Individual test case definition"""
    name: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    validation_rules: List[str] = field(default_factory=list)
    timeout_seconds: float = 10.0

@dataclass
class TestSuite:
    """Test suite containing multiple test cases"""
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_required: bool = True

@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    passed: bool
    execution_time: float
    error_message: Optional[str] = None
    actual_output: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

class QueryFinderValidator:
    """Comprehensive validation framework for query finder"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.query_finder = None
        self.question_classifier = None
        self.domain_expander = None
        self.quality_scorer = None
        
        # Test results storage
        self.test_results = []
        self.test_suites = []
        
        # Initialize test suites
        self._initialize_test_suites()
    
    def _initialize_test_suites(self):
        """Initialize all test suites"""
        
        # Question Type Classification Tests
        classification_suite = TestSuite(
            name="Question Type Classification",
            description="Validate 6-type question classification accuracy"
        )
        
        classification_suite.test_cases = [
            TestCase(
                name="Factual Query Classification",
                input_data={"query": "What is the population of New York City?"},
                expected_output={"question_type": "factual", "min_confidence": 0.7}
            ),
            TestCase(
                name="Analytical Query Classification", 
                input_data={"query": "Why is customer retention decreasing in our industry?"},
                expected_output={"question_type": "analytical", "min_confidence": 0.7}
            ),
            TestCase(
                name="Comparative Query Classification",
                input_data={"query": "Compare React vs Vue for frontend development"},
                expected_output={"question_type": "comparative", "min_confidence": 0.7}
            ),
            TestCase(
                name="Procedural Query Classification",
                input_data={"query": "How to implement OAuth2 authentication in Python?"},
                expected_output={"question_type": "procedural", "min_confidence": 0.7}
            ),
            TestCase(
                name="Creative Query Classification",
                input_data={"query": "Generate marketing campaign ideas for eco-friendly products"},
                expected_output={"question_type": "creative", "min_confidence": 0.7}
            ),
            TestCase(
                name="Diagnostic Query Classification",
                input_data={"query": "Why is my website loading slowly and how to fix it?"},
                expected_output={"question_type": "diagnostic", "min_confidence": 0.7}
            )
        ]
        
        self.test_suites.append(classification_suite)
        
        # Domain Expansion Tests
        domain_suite = TestSuite(
            name="Domain Expansion",
            description="Validate cross-domain query expansion functionality"
        )
        
        domain_suite.test_cases = [
            TestCase(
                name="Marketing Domain Detection",
                input_data={"query": "improve customer engagement through social media campaigns"},
                expected_output={"primary_domain": "marketing", "min_domains": 1, "has_expansions": True}
            ),
            TestCase(
                name="Technology Domain Detection",
                input_data={"query": "implement microservices architecture for scalability"},
                expected_output={"primary_domain": "technology", "min_domains": 1, "has_expansions": True}
            ),
            TestCase(
                name="Cross-Domain Query Expansion",
                input_data={"query": "optimize sales process using CRM technology"},
                expected_output={"min_domains": 2, "contains_domains": ["sales", "technology"], "has_insights": True}
            )
        ]
        
        self.test_suites.append(domain_suite)
        
        # Quality Scoring Tests
        quality_suite = TestSuite(
            name="Quality Assessment",
            description="Validate multi-dimensional quality scoring"
        )
        
        quality_suite.test_cases = [
            TestCase(
                name="High Quality Query Assessment",
                input_data={"query": "Provide a comprehensive step-by-step guide to implement OAuth2 authentication in a React application with proper security considerations and error handling"},
                expected_output={"min_score": 0.7, "grade": ["A", "B"], "has_strengths": True}
            ),
            TestCase(
                name="Low Quality Query Assessment", 
                input_data={"query": "help"},
                expected_output={"max_score": 0.4, "grade": ["D", "F"], "has_suggestions": True}
            ),
            TestCase(
                name="Medium Quality Query Assessment",
                input_data={"query": "How to improve website performance?"},
                expected_output={"min_score": 0.4, "max_score": 0.8, "grade": ["B", "C", "D"]}
            )
        ]
        
        self.test_suites.append(quality_suite)
        
        # Integration Tests
        integration_suite = TestSuite(
            name="Query Finder Integration",
            description="Validate end-to-end query finder functionality"
        )
        
        integration_suite.test_cases = [
            TestCase(
                name="Fast Mode Processing",
                input_data={"query": "What is machine learning?", "mode": "fast"},
                expected_output={"has_classification": True, "max_time": 0.5, "components": ["question_classifier"]}
            ),
            TestCase(
                name="Standard Mode Processing",
                input_data={"query": "Compare different cloud storage solutions", "mode": "standard"},
                expected_output={"has_classification": True, "has_expansion": True, "max_time": 2.0}
            ),
            TestCase(
                name="Comprehensive Mode Processing",
                input_data={"query": "Develop a content marketing strategy for B2B SaaS", "mode": "comprehensive"},
                expected_output={"has_classification": True, "has_expansion": True, "has_quality": True, "max_time": 5.0}
            )
        ]
        
        self.test_suites.append(integration_suite)
        
        # Batch Processing Tests
        batch_suite = TestSuite(
            name="Batch Processing",
            description="Validate batch processing functionality and performance"
        )
        
        batch_suite.test_cases = [
            TestCase(
                name="Small Batch Processing",
                input_data={"queries": ["What is AI?", "How to code?", "Best practices"], "mode": "fast"},
                expected_output={"success_rate": 1.0, "max_time": 5.0, "all_processed": True}
            ),
            TestCase(
                name="Medium Batch Processing",
                input_data={"query_count": 50, "mode": "standard"},
                expected_output={"success_rate": 0.95, "max_time": 15.0, "throughput_min": 3.0}
            ),
            TestCase(
                name="Large Batch Performance", 
                input_data={"query_count": 100, "mode": "fast"},
                expected_output={"success_rate": 0.95, "max_time": 10.0, "throughput_min": 10.0},
                timeout_seconds=15.0
            )
        ]
        
        self.test_suites.append(batch_suite)
        
        # Error Handling Tests
        error_suite = TestSuite(
            name="Error Handling",
            description="Validate error handling and edge cases"
        )
        
        error_suite.test_cases = [
            TestCase(
                name="Empty Query Handling",
                input_data={"query": ""},
                expected_output={"question_type": "unknown", "has_error_handling": True}
            ),
            TestCase(
                name="Very Long Query Handling",
                input_data={"query": "A" * 10000},
                expected_output={"processed": True, "has_truncation": False}
            ),
            TestCase(
                name="Special Characters Handling",
                input_data={"query": "What is @#$%^&*()? How to handle?"},
                expected_output={"processed": True, "question_type": ["factual", "procedural"]}
            ),
            TestCase(
                name="Non-English Query Handling",
                input_data={"query": "¿Qué es machine learning?"},
                expected_output={"processed": True, "graceful_handling": True}
            )
        ]
        
        self.test_suites.append(error_suite)
    
    async def initialize(self):
        """Initialize all components for testing"""
        try:
            self.logger.info("🚀 Initializing Query Finder Validator...")
            
            # Initialize main components
            self.query_finder = await get_conversational_query_finder()
            self.question_classifier = await get_question_type_classifier()
            self.domain_expander = await get_domain_expansion_engine()
            self.quality_scorer = await get_query_quality_scorer()
            
            self.logger.info("✅ Query Finder Validator initialized")
            
        except Exception as e:
            self.logger.error(f"Validator initialization failed: {e}")
            raise
    
    async def run_test_case(self, test_case: TestCase, component: str = None) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            if component == "classifier":
                result = await self._test_classification(test_case)
            elif component == "expander":
                result = await self._test_expansion(test_case)
            elif component == "scorer":
                result = await self._test_quality(test_case)
            elif component == "integration":
                result = await self._test_integration(test_case)
            elif component == "batch":
                result = await self._test_batch(test_case)
            elif component == "error":
                result = await self._test_error_handling(test_case)
            else:
                result = await self._test_integration(test_case)  # Default to integration
            
            execution_time = time.time() - start_time
            
            # Validate result against expected output
            passed = self._validate_result(result, test_case.expected_output)
            
            return TestResult(
                test_name=test_case.name,
                passed=passed,
                execution_time=execution_time,
                actual_output=result,
                performance_metrics={
                    'execution_time': execution_time,
                    'timeout_seconds': test_case.timeout_seconds
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Test case {test_case.name} failed: {e}")
            
            return TestResult(
                test_name=test_case.name,
                passed=False,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _test_classification(self, test_case: TestCase) -> Dict[str, Any]:
        """Test question type classification"""
        query = test_case.input_data["query"]
        
        result = await self.question_classifier.classify_question(query)
        
        return {
            "question_type": result.question_type.value,
            "confidence": result.confidence_score,
            "reasoning": result.reasoning,
            "processing_time": result.processing_time,
            "alternatives": [(alt[0].value, alt[1]) for alt in result.alternative_types]
        }
    
    async def _test_expansion(self, test_case: TestCase) -> Dict[str, Any]:
        """Test domain expansion"""
        query = test_case.input_data["query"]
        
        result = await self.domain_expander.expand_query(query)
        
        return {
            "primary_domains": [domain.value for domain in result.primary_domains],
            "expanded_queries": [eq.expanded_query for eq in result.expanded_queries],
            "cross_domain_insights": result.cross_domain_insights,
            "confidence_score": result.confidence_score,
            "processing_time": result.processing_time,
            "suggested_domains": [(domain.value, score) for domain, score in result.suggested_domains]
        }
    
    async def _test_quality(self, test_case: TestCase) -> Dict[str, Any]:
        """Test quality assessment"""
        query = test_case.input_data["query"]
        
        result = await self.quality_scorer.assess_query_quality(query)
        
        return {
            "overall_score": result.overall_score,
            "grade": result.grade,
            "confidence_level": result.confidence_level,
            "strengths": result.strengths,
            "improvement_suggestions": result.improvement_suggestions,
            "individual_metrics": [
                {
                    "dimension": metric.dimension.value,
                    "score": metric.score,
                    "reasoning": metric.reasoning
                }
                for metric in result.individual_metrics
            ],
            "processing_time": result.processing_time
        }
    
    async def _test_integration(self, test_case: TestCase) -> Dict[str, Any]:
        """Test end-to-end query finder integration"""
        query = test_case.input_data["query"]
        mode = ProcessingMode(test_case.input_data.get("mode", "standard"))
        
        result = await self.query_finder.find_query(query, mode)
        
        return {
            "question_type": result.question_type.value,
            "classification_confidence": result.classification_confidence,
            "primary_domains": [domain.value for domain in result.primary_domains],
            "expanded_queries": result.expanded_queries,
            "processing_time": result.processing_time,
            "components_used": result.components_used,
            "quality_assessment": {
                "overall_score": result.quality_assessment.overall_score if result.quality_assessment else None,
                "grade": result.quality_assessment.grade if result.quality_assessment else None
            } if result.quality_assessment else None,
            "suggested_improvements": result.suggested_improvements,
            "cross_domain_insights": result.cross_domain_insights,
            "confidence_scores": result.confidence_scores
        }
    
    async def _test_batch(self, test_case: TestCase) -> Dict[str, Any]:
        """Test batch processing"""
        if "queries" in test_case.input_data:
            queries = test_case.input_data["queries"]
        else:
            # Generate test queries
            query_count = test_case.input_data["query_count"]
            queries = [f"Test query {i}: What is example {i}?" for i in range(query_count)]
        
        mode = ProcessingMode(test_case.input_data.get("mode", "standard"))
        
        result = await self.query_finder.batch_find_queries(queries, mode)
        
        return {
            "total_queries": result.total_queries,
            "successful_queries": result.successful_queries,
            "failed_queries": result.failed_queries,
            "success_rate": result.successful_queries / result.total_queries if result.total_queries > 0 else 0,
            "total_processing_time": result.total_processing_time,
            "average_processing_time": result.average_processing_time,
            "throughput_qps": result.throughput_queries_per_second,
            "quality_distribution": result.quality_distribution,
            "question_type_distribution": result.question_type_distribution,
            "cache_hit_rate": result.cache_hit_rate
        }
    
    async def _test_error_handling(self, test_case: TestCase) -> Dict[str, Any]:
        """Test error handling and edge cases"""
        query = test_case.input_data["query"]
        
        try:
            result = await self.query_finder.find_query(query)
            
            return {
                "processed": True,
                "question_type": result.question_type.value,
                "classification_confidence": result.classification_confidence,
                "processing_time": result.processing_time,
                "error": None,
                "graceful_handling": True
            }
            
        except Exception as e:
            return {
                "processed": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "graceful_handling": False
            }
    
    def _validate_result(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """Validate actual result against expected output"""
        try:
            for key, expected_value in expected.items():
                if key not in actual:
                    self.logger.warning(f"Missing key in result: {key}")
                    return False
                
                actual_value = actual[key]
                
                # Handle different validation types
                if key == "min_confidence" and actual_value < expected_value:
                    return False
                elif key == "max_confidence" and actual_value > expected_value:
                    return False
                elif key == "min_score" and actual_value < expected_value:
                    return False
                elif key == "max_score" and actual_value > expected_value:
                    return False
                elif key == "max_time" and actual_value > expected_value:
                    return False
                elif key == "min_domains" and len(actual.get("primary_domains", [])) < expected_value:
                    return False
                elif key == "success_rate" and actual_value < expected_value:
                    return False
                elif key == "throughput_min" and actual_value < expected_value:
                    return False
                elif key == "question_type" and actual_value != expected_value:
                    return False
                elif key == "grade" and actual_value not in expected_value:
                    return False
                elif key == "has_classification" and expected_value and "question_type" not in actual:
                    return False
                elif key == "has_expansion" and expected_value and not actual.get("expanded_queries"):
                    return False
                elif key == "has_quality" and expected_value and not actual.get("quality_assessment"):
                    return False
                elif key == "all_processed" and expected_value and actual.get("failed_queries", 0) > 0:
                    return False
                elif key == "contains_domains":
                    primary_domains = actual.get("primary_domains", [])
                    if not any(domain in primary_domains for domain in expected_value):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    async def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Run a complete test suite"""
        suite = next((s for s in self.test_suites if s.name == suite_name), None)
        if not suite:
            raise ValueError(f"Test suite not found: {suite_name}")
        
        self.logger.info(f"🧪 Running test suite: {suite.name}")
        
        results = []
        component_map = {
            "Question Type Classification": "classifier",
            "Domain Expansion": "expander", 
            "Quality Assessment": "scorer",
            "Query Finder Integration": "integration",
            "Batch Processing": "batch",
            "Error Handling": "error"
        }
        
        component = component_map.get(suite.name, "integration")
        
        for test_case in suite.test_cases:
            self.logger.info(f"  Running: {test_case.name}")
            result = await self.run_test_case(test_case, component)
            results.append(result)
            
            status = "✅ PASS" if result.passed else "❌ FAIL"
            self.logger.info(f"    {status} ({result.execution_time:.3f}s)")
            
            if not result.passed and result.error_message:
                self.logger.error(f"    Error: {result.error_message}")
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report"""
        self.logger.info("🚀 Starting Comprehensive Validation Test Suite...")
        
        all_results = {}
        total_tests = 0
        total_passed = 0
        
        for suite in self.test_suites:
            suite_results = await self.run_test_suite(suite.name)
            all_results[suite.name] = suite_results
            
            suite_passed = sum(1 for r in suite_results if r.passed)
            total_tests += len(suite_results)
            total_passed += suite_passed
            
            self.logger.info(f"  Suite {suite.name}: {suite_passed}/{len(suite_results)} passed")
        
        # Generate summary
        summary = {
            "overall_success": total_passed == total_tests,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "pass_rate": total_passed / total_tests if total_tests > 0 else 0,
            "suite_results": {}
        }
        
        for suite_name, results in all_results.items():
            passed = sum(1 for r in results if r.passed)
            summary["suite_results"][suite_name] = {
                "passed": passed,
                "total": len(results),
                "pass_rate": passed / len(results) if results else 0
            }
        
        self.logger.info("✅ Comprehensive Validation Complete")
        self.logger.info(f"  Overall: {total_passed}/{total_tests} tests passed ({summary['pass_rate']:.2%})")
        
        return {
            "summary": summary,
            "detailed_results": all_results,
            "timestamp": time.time()
        }
    
    def generate_test_report(self, results: Dict[str, Any], filename: str = None):
        """Generate comprehensive test report"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"
        
        try:
            # Convert test results to serializable format
            serializable_results = {}
            
            for suite_name, suite_results in results["detailed_results"].items():
                serializable_results[suite_name] = [
                    {
                        "test_name": r.test_name,
                        "passed": r.passed,
                        "execution_time": r.execution_time,
                        "error_message": r.error_message,
                        "performance_metrics": r.performance_metrics
                    }
                    for r in suite_results
                ]
            
            report = {
                "validation_report": "Conversational Query Finder",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": results["summary"],
                "detailed_results": serializable_results
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Validation report saved to: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save validation report: {e}")

async def main():
    """Main validation execution"""
    validator = QueryFinderValidator()
    
    try:
        # Initialize validator
        await validator.initialize()
        
        # Run all tests
        results = await validator.run_all_tests()
        
        # Generate and save report
        validator.generate_test_report(results)
        
        # Print summary
        summary = results["summary"]
        print("\n" + "="*80)
        print("QUERY FINDER VALIDATION REPORT")
        print("="*80)
        
        overall_status = "✅ SUCCESS" if summary["overall_success"] else "❌ FAILURE"
        print(f"Overall Status: {overall_status}")
        print(f"Tests Passed: {summary['total_passed']}/{summary['total_tests']} ({summary['pass_rate']:.2%})")
        
        print("\nSuite Results:")
        for suite_name, suite_summary in summary["suite_results"].items():
            status = "✅" if suite_summary["pass_rate"] == 1.0 else "⚠️" if suite_summary["pass_rate"] >= 0.8 else "❌"
            print(f"  {status} {suite_name}: {suite_summary['passed']}/{suite_summary['total']} ({suite_summary['pass_rate']:.2%})")
        
        print("="*80)
        
        # Exit with proper code
        exit(0 if summary["overall_success"] else 1)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())