#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for Blueprint Generation and Retrieval APIs

This script tests all blueprint-related endpoints on the running SERP Strategist API server.
Tests include generation, retrieval, listing, error handling, and performance validation.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USER_ID = "test-user-api-validation"
REQUEST_TIMEOUT = 30

# Test data
TEST_KEYWORDS = [
    "content marketing",
    "SEO strategy", 
    "digital transformation",
    "artificial intelligence",
    "e-commerce optimization"
]

EDGE_CASE_KEYWORDS = [
    "",  # Empty string
    "a",  # Single character
    "x" * 300,  # Very long keyword (over 255 chars)
    "special!@#$%^&*()chars",  # Special characters
    "   leading and trailing spaces   "  # Whitespace
]

class APITester:
    """Comprehensive API testing class."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-User-ID': TEST_USER_ID
        })
        self.generated_blueprints = []
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'errors': []
        }
    
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results."""
        self.test_results['total'] += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if message:
            print(f"    {message}")
        
        if data and isinstance(data, dict):
            for key, value in data.items():
                print(f"    {key}: {value}")
        
        if success:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
        
        print()
    
    def test_server_connectivity(self) -> bool:
        """Test basic server connectivity."""
        print("🌐 Testing Server Connectivity")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Server Connectivity",
                    True,
                    f"Server running: {data.get('name', 'Unknown')} v{data.get('version', 'Unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Server Connectivity",
                    False,
                    f"Unexpected status code: {response.status_code}"
                )
                return False
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Server Connectivity",
                False,
                "Connection refused - server may not be running"
            )
            return False
        except Exception as e:
            self.log_test(
                "Server Connectivity",
                False,
                f"Connection error: {str(e)}"
            )
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        print("🏥 Testing Health Check Endpoint")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/health", timeout=REQUEST_TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                health_data = {
                    "Status": data.get('status', 'Unknown'),
                    "Version": data.get('version', 'Unknown'),
                    "Response Time": f"{response_time:.3f}s",
                    "Enhanced Features": data.get('features', {}).get('enhanced_processing', 'Unknown'),
                    "Database": data.get('features', {}).get('database', 'Unknown'),
                    "Services Available": sum(1 for v in data.get('services', {}).values() if v)
                }
                
                self.log_test("Health Check", True, "Health endpoint responsive", health_data)
                return True
            else:
                self.log_test(
                    "Health Check",
                    False,
                    f"Health check failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_blueprint_generation(self, keyword: str, expect_success: bool = True) -> Optional[str]:
        """Test blueprint generation for a specific keyword."""
        try:
            payload = {"keyword": keyword}
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/api/blueprints/generate",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            response_time = time.time() - start_time
            
            if expect_success and response.status_code == 201:
                data = response.json()
                blueprint_id = data.get('blueprint_id', 'Unknown')
                
                # Store generated blueprint for later testing
                if blueprint_id != 'Unknown':
                    self.generated_blueprints.append(blueprint_id)
                
                result_data = {
                    "Blueprint ID": blueprint_id,
                    "Generation Time": f"{response_time:.2f}s",
                    "Status": data.get('status', 'Unknown'),
                    "Fallback Used": "note" in data
                }
                
                self.log_test(
                    f"Generate Blueprint: '{keyword[:30]}{'...' if len(keyword) > 30 else ''}'",
                    True,
                    "Blueprint generated successfully",
                    result_data
                )
                return blueprint_id
            
            elif not expect_success and response.status_code >= 400:
                # Expected failure (e.g., validation error)
                error_data = response.json() if response.content else {}
                self.log_test(
                    f"Generate Blueprint (Expected Failure): '{keyword[:30]}{'...' if len(keyword) > 30 else ''}'",
                    True,
                    f"Expected error: {error_data.get('error', 'Unknown error')}"
                )
                return None
            
            else:
                # Unexpected result
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = f"Status {response.status_code}, no JSON response"
                
                self.log_test(
                    f"Generate Blueprint: '{keyword[:30]}{'...' if len(keyword) > 30 else ''}'",
                    False,
                    f"Unexpected response: {error_msg}"
                )
                return None
        
        except requests.exceptions.Timeout:
            self.log_test(
                f"Generate Blueprint: '{keyword[:30]}{'...' if len(keyword) > 30 else ''}'",
                False,
                f"Request timeout after {REQUEST_TIMEOUT}s"
            )
            return None
        except Exception as e:
            self.log_test(
                f"Generate Blueprint: '{keyword[:30]}{'...' if len(keyword) > 30 else ''}'",
                False,
                f"Request error: {str(e)}"
            )
            return None
    
    def test_blueprint_retrieval(self, blueprint_id: str) -> bool:
        """Test blueprint retrieval by ID."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/blueprints/{blueprint_id}",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                retrieval_data = {
                    "Blueprint ID": data.get('id', 'Unknown'),
                    "Keyword": data.get('keyword', 'Unknown'),
                    "Status": data.get('status', 'Unknown'),
                    "Created": data.get('created_at', 'Unknown'),
                    "Has Competitor Analysis": bool(data.get('competitor_analysis')),
                    "Has Heading Structure": bool(data.get('heading_structure')),
                    "Has Topic Clusters": bool(data.get('topic_clusters'))
                }
                
                self.log_test(
                    f"Retrieve Blueprint: {blueprint_id[:16]}...",
                    True,
                    "Blueprint retrieved successfully",
                    retrieval_data
                )
                return True
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    f"Retrieve Blueprint: {blueprint_id[:16]}...",
                    False,
                    f"Retrieval failed: {error_data.get('error', f'Status {response.status_code}')}"
                )
                return False
        
        except Exception as e:
            self.log_test(
                f"Retrieve Blueprint: {blueprint_id[:16]}...",
                False,
                f"Retrieval error: {str(e)}"
            )
            return False
    
    def test_blueprint_listing(self) -> bool:
        """Test blueprint listing endpoint."""
        try:
            # Test basic listing
            response = self.session.get(
                f"{self.base_url}/api/blueprints",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                blueprints = data.get('blueprints', [])
                
                listing_data = {
                    "Total Blueprints": data.get('total', 0),
                    "Returned Count": len(blueprints),
                    "Limit": data.get('limit', 'Unknown'),
                    "Offset": data.get('offset', 'Unknown')
                }
                
                self.log_test(
                    "List Blueprints",
                    True,
                    "Blueprint listing successful",
                    listing_data
                )
                
                # Test pagination
                if len(blueprints) > 0:
                    paginated_response = self.session.get(
                        f"{self.base_url}/api/blueprints?limit=2&offset=0",
                        timeout=REQUEST_TIMEOUT
                    )
                    
                    if paginated_response.status_code == 200:
                        paginated_data = paginated_response.json()
                        self.log_test(
                            "List Blueprints (Pagination)",
                            True,
                            f"Paginated listing returned {len(paginated_data.get('blueprints', []))} items"
                        )
                    else:
                        self.log_test(
                            "List Blueprints (Pagination)",
                            False,
                            "Pagination test failed"
                        )
                
                return True
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "List Blueprints",
                    False,
                    f"Listing failed: {error_data.get('error', f'Status {response.status_code}')}"
                )
                return False
        
        except Exception as e:
            self.log_test(
                "List Blueprints",
                False,
                f"Listing error: {str(e)}"
            )
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication requirements."""
        print("🔐 Testing Authentication")
        print("=" * 50)
        
        # Test without X-User-ID header
        session_no_auth = requests.Session()
        session_no_auth.headers.update({'Content-Type': 'application/json'})
        
        try:
            response = session_no_auth.post(
                f"{self.base_url}/api/blueprints/generate",
                json={"keyword": "test"},
                timeout=5
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Required",
                    True,
                    "API correctly rejects requests without authentication"
                )
                return True
            else:
                self.log_test(
                    "Authentication Required",
                    False,
                    f"Expected 401, got {response.status_code}"
                )
                return False
        
        except Exception as e:
            self.log_test(
                "Authentication Required",
                False,
                f"Authentication test error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run the complete test suite."""
        print("🚀 SERP Strategist API - Blueprint Testing Suite")
        print(f"Testing server: {self.base_url}")
        print(f"Test User ID: {TEST_USER_ID}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
        
        # 1. Basic connectivity and health
        if not self.test_server_connectivity():
            print("❌ Server connectivity failed. Cannot continue tests.")
            return False
        
        # Update todo: mark connectivity test as completed
        self.test_health_endpoint()
        
        # 2. Authentication tests
        self.test_authentication()
        
        # 3. Blueprint generation tests
        print("🔧 Testing Blueprint Generation")
        print("=" * 50)
        
        # Test valid keywords
        for keyword in TEST_KEYWORDS:
            self.test_blueprint_generation(keyword, expect_success=True)
            time.sleep(1)  # Small delay between requests
        
        # Test edge cases (expecting failures)
        print("🔍 Testing Edge Cases")
        print("=" * 50)
        
        for keyword in EDGE_CASE_KEYWORDS:
            expected_success = len(keyword.strip()) > 0 and len(keyword) <= 255
            self.test_blueprint_generation(keyword, expect_success=expected_success)
            time.sleep(0.5)
        
        # 4. Blueprint retrieval tests
        if self.generated_blueprints:
            print("📖 Testing Blueprint Retrieval")
            print("=" * 50)
            
            for blueprint_id in self.generated_blueprints[:3]:  # Test first 3
                self.test_blueprint_retrieval(blueprint_id)
                time.sleep(0.5)
            
            # Test non-existent blueprint
            self.test_blueprint_retrieval("non-existent-id-12345")
        
        # 5. Blueprint listing tests
        print("📋 Testing Blueprint Listing")
        print("=" * 50)
        self.test_blueprint_listing()
        
        # Final results
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total = self.test_results['total']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.generated_blueprints:
            print(f"\nGenerated Blueprints: {len(self.generated_blueprints)}")
            print("Blueprint IDs:")
            for blueprint_id in self.generated_blueprints:
                print(f"  - {blueprint_id}")
        
        if self.test_results['errors']:
            print(f"\n❌ Failed Tests:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall result
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Your API is working perfectly.")
        elif success_rate >= 80:
            print(f"\n✅ Most tests passed ({success_rate:.1f}%). Minor issues detected.")
        else:
            print(f"\n⚠️  Significant issues detected ({success_rate:.1f}% success rate).")

if __name__ == "__main__":
    print("Starting API tests...")
    tester = APITester()
    tester.run_all_tests()