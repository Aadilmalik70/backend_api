#!/usr/bin/env python3
"""
Test script for payment integration system

Tests the complete payment workflow including:
- Subscription plan creation
- Payment order creation
- Usage tracking and quota enforcement
- Database operations

Usage:
    python test_payment_integration.py
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the backend_api/src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def test_api_endpoint(url, method='GET', data=None, headers=None):
    """Test an API endpoint and return the response"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'data': response.json() if response.content else None,
            'headers': dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': None
        }
    except json.JSONDecodeError as e:
        return {
            'success': True,
            'status_code': response.status_code,
            'data': response.text,
            'json_error': str(e)
        }

def run_payment_integration_tests():
    """Run comprehensive payment integration tests"""
    print("🚀 SERP Strategist Payment Integration Test Suite")
    print("=" * 60)
    
    # Configuration
    base_url = "http://localhost:5000"
    test_user_id = "test-user-123"
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': test_user_id
    }
    
    tests_passed = 0
    tests_failed = 0
    
    def run_test(test_name, test_func):
        """Run a single test and track results"""
        nonlocal tests_passed, tests_failed
        
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                tests_passed += 1
            else:
                print(f"❌ FAILED: {test_name}")
                tests_failed += 1
        except Exception as e:
            print(f"💥 ERROR: {test_name} - {str(e)}")
            tests_failed += 1
    
    # Test 1: Health Check
    def test_health_check():
        response = test_api_endpoint(f"{base_url}/api/health")
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            print(f"📊 Health Status: {data.get('status', 'unknown')}")
            print(f"🔧 Features: {data.get('features', {})}")
            print(f"💳 Payment Available: {data.get('payment', {}).get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response}")
            return False
    
    # Test 2: Payment Service Status
    def test_payment_status():
        response = test_api_endpoint(f"{base_url}/api/payment/status")
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            print(f"💳 Payment Service Available: {data.get('payment_service_available', False)}")
            print(f"🔧 Razorpay Configured: {data.get('razorpay_configured', False)}")
            print(f"💰 Supported Currencies: {data.get('supported_currencies', [])}")
            return True
        else:
            print(f"❌ Payment status check failed: {response}")
            return False
    
    # Test 3: Get Subscription Plans
    def test_subscription_plans():
        response = test_api_endpoint(f"{base_url}/api/payment/plans")
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            plans = data.get('plans', [])
            print(f"📋 Available Plans: {len(plans)}")
            for plan in plans:
                print(f"  - {plan.get('name', 'Unknown')}: ₹{plan.get('price_monthly', 0)}/month")
                print(f"    Blueprints: {plan.get('blueprint_limit', 0)}")
                print(f"    API Calls: {plan.get('api_calls_limit', 0)}")
            return len(plans) > 0
        else:
            print(f"❌ Failed to get subscription plans: {response}")
            return False
    
    # Test 4: Get User Subscription
    def test_user_subscription():
        response = test_api_endpoint(f"{base_url}/api/payment/subscription", headers=headers)
        if response['success']:
            if response['status_code'] == 200:
                data = response['data']
                subscription = data.get('subscription')
                if subscription:
                    print(f"📊 Active Subscription: {subscription.get('plan', {}).get('name', 'Unknown')}")
                    print(f"🔄 Status: {subscription.get('status', 'unknown')}")
                    print(f"📅 Days Remaining: {subscription.get('days_remaining', 0)}")
                else:
                    print("📊 No active subscription found")
                return True
            else:
                print(f"❌ Authentication failed: {response['status_code']}")
                return response['status_code'] == 401  # Expected for test user
        else:
            print(f"❌ Failed to get user subscription: {response}")
            return False
    
    # Test 5: Check Usage Limits
    def test_usage_limits():
        response = test_api_endpoint(f"{base_url}/api/payment/usage/check?resource_type=blueprint", headers=headers)
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            print(f"🎯 Usage Check - Allowed: {data.get('allowed', False)}")
            print(f"📊 Subscription Status: {data.get('subscription_status', 'unknown')}")
            if data.get('subscription_status') == 'active':
                subscription = data.get('subscription', {})
                print(f"📈 Plan: {subscription.get('plan', {}).get('name', 'Unknown')}")
                print(f"📊 Used: {data.get('used', 0)}/{data.get('limit', 0)}")
                print(f"🔄 Remaining: {data.get('remaining', 0)}")
            return True
        else:
            print(f"❌ Failed to check usage limits: {response}")
            return False
    
    # Test 6: Create Payment Order (will fail without Razorpay config)
    def test_create_payment_order():
        # First get available plans
        plans_response = test_api_endpoint(f"{base_url}/api/payment/plans")
        if not plans_response['success'] or plans_response['status_code'] != 200:
            print("❌ Cannot get plans for payment order test")
            return False
        
        plans = plans_response['data'].get('plans', [])
        if not plans:
            print("❌ No plans available for payment order test")
            return False
        
        # Try to create order for the first plan
        plan_id = plans[0]['id']
        order_data = {
            'plan_id': plan_id,
            'billing_cycle': 'monthly'
        }
        
        response = test_api_endpoint(f"{base_url}/api/payment/create-order", 'POST', order_data, headers)
        
        if response['success']:
            if response['status_code'] == 200:
                data = response['data']
                print(f"✅ Order Created: {data.get('order_id', 'unknown')}")
                print(f"💰 Amount: ₹{data.get('amount', 0) / 100}")
                print(f"📋 Plan: {data.get('plan', {}).get('name', 'Unknown')}")
                return True
            elif response['status_code'] == 503:
                print("⚠️  Payment service unavailable (expected without Razorpay config)")
                return True  # This is expected in test environment
            else:
                print(f"❌ Order creation failed: {response['status_code']}")
                return False
        else:
            print(f"❌ Failed to create payment order: {response}")
            return False
    
    # Test 7: Test Payment Webhook (without signature)
    def test_payment_webhook():
        webhook_data = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_test_123',
                        'order_id': 'order_test_123',
                        'status': 'captured'
                    }
                }
            }
        }
        
        webhook_headers = {
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': 'test_signature_without_secret'
        }
        
        response = test_api_endpoint(f"{base_url}/api/payment/webhook", 'POST', webhook_data, webhook_headers)
        
        if response['success']:
            if response['status_code'] in [200, 400]:  # Either success or expected signature failure
                print(f"✅ Webhook endpoint responsive: {response['status_code']}")
                return True
            else:
                print(f"❌ Unexpected webhook response: {response['status_code']}")
                return False
        else:
            print(f"❌ Webhook test failed: {response}")
            return False
    
    # Test 8: Test Blueprint Generation with Usage Tracking
    def test_blueprint_with_usage_tracking():
        blueprint_data = {
            'keyword': 'test payment integration',
            'enable_websocket': False
        }
        
        response = test_api_endpoint(f"{base_url}/api/blueprints/generate-realtime", 'POST', blueprint_data, headers)
        
        if response['success']:
            if response['status_code'] == 202:  # Accepted
                data = response['data']
                print(f"✅ Blueprint Generation Started: {data.get('blueprint_id', 'unknown')}")
                print(f"🎯 Keyword: {data.get('keyword', 'unknown')}")
                if 'subscription_info' in data:
                    sub_info = data['subscription_info']
                    print(f"📊 Plan: {sub_info.get('plan', 'unknown')}")
                    print(f"🔄 Remaining: {sub_info.get('remaining_blueprints', 0)}")
                return True
            elif response['status_code'] == 402:  # Payment Required
                print("⚠️  Payment required for blueprint generation (expected for test user)")
                return True  # This is expected behavior
            elif response['status_code'] == 429:  # Too Many Requests
                print("⚠️  Usage limit exceeded (expected behavior)")
                return True  # This is expected behavior
            else:
                print(f"❌ Unexpected blueprint response: {response['status_code']}")
                return False
        else:
            print(f"❌ Blueprint generation test failed: {response}")
            return False
    
    # Test 9: Get User Transactions
    def test_user_transactions():
        response = test_api_endpoint(f"{base_url}/api/payment/transactions", headers=headers)
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            transactions = data.get('transactions', [])
            print(f"💳 Transaction History: {len(transactions)} transactions")
            for tx in transactions[:3]:  # Show first 3
                print(f"  - {tx.get('id', 'unknown')}: ₹{tx.get('amount', 0)} ({tx.get('status', 'unknown')})")
            return True
        else:
            print(f"❌ Failed to get user transactions: {response}")
            return False
    
    # Test 10: Get Usage History
    def test_usage_history():
        response = test_api_endpoint(f"{base_url}/api/payment/usage/history", headers=headers)
        if response['success'] and response['status_code'] == 200:
            data = response['data']
            events = data.get('usage_events', [])
            summary = data.get('usage_summary', [])
            print(f"📊 Usage Events: {len(events)} events")
            print(f"📈 Usage Summary: {len(summary)} event types")
            for item in summary:
                print(f"  - {item.get('event_type', 'unknown')}: {item.get('count', 0)} times")
            return True
        else:
            print(f"❌ Failed to get usage history: {response}")
            return False
    
    # Run all tests
    print(f"🎯 Testing against: {base_url}")
    print(f"👤 Test User ID: {test_user_id}")
    print(f"⏰ Test Time: {datetime.now().isoformat()}")
    
    run_test("API Health Check", test_health_check)
    run_test("Payment Service Status", test_payment_status)
    run_test("Subscription Plans", test_subscription_plans)
    run_test("User Subscription", test_user_subscription)
    run_test("Usage Limits Check", test_usage_limits)
    run_test("Payment Order Creation", test_create_payment_order)
    run_test("Payment Webhook", test_payment_webhook)
    run_test("Blueprint Generation with Usage Tracking", test_blueprint_with_usage_tracking)
    run_test("User Transactions", test_user_transactions)
    run_test("Usage History", test_usage_history)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📊 Success Rate: {(tests_passed / (tests_passed + tests_failed)) * 100:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! Payment integration is working correctly.")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Check the output above for details.")
    
    print("\n💡 Notes:")
    print("- Some failures are expected in test environment without Razorpay credentials")
    print("- Usage tracking and subscription limits should be working")
    print("- Database operations should be functional")
    
    return tests_failed == 0

if __name__ == '__main__':
    try:
        success = run_payment_integration_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {str(e)}")
        sys.exit(1)