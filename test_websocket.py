#!/usr/bin/env python3
"""
WebSocket Test Script - Test real-time blueprint generation functionality.

This script tests the WebSocket integration by connecting to the server,
starting a blueprint generation, and monitoring real-time progress updates.
"""

import asyncio
import socketio
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
USER_ID = "test-user-websocket"
TEST_KEYWORD = "content marketing strategy"

class WebSocketTester:
    def __init__(self):
        self.sio = socketio.AsyncClient()
        self.blueprint_id = None
        self.events_received = []
        
        # Register event handlers
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup WebSocket event handlers for testing."""
        
        @self.sio.event
        async def connect():
            print(f"✅ WebSocket connected at {datetime.now()}")
            self.log_event("connect", {"timestamp": datetime.now().isoformat()})
        
        @self.sio.event
        async def disconnect():
            print(f"❌ WebSocket disconnected at {datetime.now()}")
            self.log_event("disconnect", {"timestamp": datetime.now().isoformat()})
        
        @self.sio.event
        async def connection_status(data):
            print(f"🔗 Connection status: {data}")
            self.log_event("connection_status", data)
        
        @self.sio.event
        async def room_joined(data):
            print(f"🏠 Joined room: {data}")
            self.log_event("room_joined", data)
        
        @self.sio.event
        async def generation_started(data):
            print(f"🚀 Generation started: {data}")
            self.log_event("generation_started", data)
        
        @self.sio.event
        async def progress_update(data):
            progress = data.get('progress', 0)
            message = data.get('message', '')
            step = data.get('step', 0)
            total_steps = data.get('total_steps', 0)
            print(f"📊 Progress {progress}% - Step {step}/{total_steps}: {message}")
            self.log_event("progress_update", data)
        
        @self.sio.event
        async def step_completed(data):
            step_name = data.get('step_name', 'Unknown')
            print(f"✅ Step completed: {step_name}")
            self.log_event("step_completed", data)
        
        @self.sio.event
        async def generation_complete(data):
            print(f"🎉 Generation completed!")
            print(f"   Blueprint ID: {data.get('blueprint_id')}")
            print(f"   Generation Time: {data.get('generation_time')}s")
            self.log_event("generation_complete", data)
        
        @self.sio.event
        async def generation_failed(data):
            print(f"💥 Generation failed: {data.get('error', 'Unknown error')}")
            self.log_event("generation_failed", data)
        
        @self.sio.event
        async def custom_message(data):
            print(f"📧 Custom message: {data}")
            self.log_event("custom_message", data)
        
        @self.sio.event
        async def pong(data):
            print(f"🏓 Pong received: {data}")
            self.log_event("pong", data)
    
    def log_event(self, event_name, data):
        """Log received events for analysis."""
        self.events_received.append({
            "event": event_name,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_websocket(self):
        """Connect to the WebSocket server."""
        try:
            print(f"🔌 Connecting to WebSocket at {API_BASE_URL}...")
            await self.sio.connect(f"{API_BASE_URL}?user_id={USER_ID}")
            print("✅ WebSocket connection successful")
            return True
        except Exception as e:
            print(f"❌ WebSocket connection failed: {str(e)}")
            return False
    
    async def test_ping(self):
        """Test ping/pong functionality."""
        print("\n🏓 Testing ping/pong...")
        await self.sio.emit('ping')
        await asyncio.sleep(1)  # Wait for pong response
    
    async def start_blueprint_generation(self):
        """Start a real-time blueprint generation."""
        print(f"\n🚀 Starting blueprint generation for keyword: '{TEST_KEYWORD}'")
        
        try:
            # Make HTTP request to start generation
            response = requests.post(
                f"{API_BASE_URL}/api/blueprints/generate-realtime",
                headers={
                    "Content-Type": "application/json",
                    "X-User-ID": USER_ID
                },
                json={
                    "keyword": TEST_KEYWORD,
                    "enable_websocket": True
                }
            )
            
            if response.status_code == 202:
                data = response.json()
                self.blueprint_id = data.get('blueprint_id')
                websocket_room = data.get('websocket_room')
                estimated_time = data.get('estimated_time', 0)
                
                print(f"✅ Generation started successfully")
                print(f"   Blueprint ID: {self.blueprint_id}")
                print(f"   WebSocket Room: {websocket_room}")
                print(f"   Estimated Time: {estimated_time}s")
                
                # Join the blueprint room for real-time updates
                await self.sio.emit('join_blueprint_room', {
                    'blueprint_id': self.blueprint_id,
                    'user_id': USER_ID
                })
                
                return True
            else:
                print(f"❌ Failed to start generation: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting generation: {str(e)}")
            return False
    
    async def wait_for_completion(self, timeout=120):
        """Wait for blueprint generation to complete."""
        print(f"\n⏳ Waiting for generation to complete (timeout: {timeout}s)...")
        
        start_time = time.time()
        completed = False
        
        while time.time() - start_time < timeout:
            # Check if we received completion or failure events
            completion_events = [
                event for event in self.events_received 
                if event['event'] in ['generation_complete', 'generation_failed']
            ]
            
            if completion_events:
                completed = True
                break
            
            await asyncio.sleep(1)
        
        if completed:
            final_event = completion_events[-1]
            if final_event['event'] == 'generation_complete':
                print("✅ Blueprint generation completed successfully!")
                return True
            else:
                print("❌ Blueprint generation failed")
                return False
        else:
            print("⏰ Generation timed out")
            return False
    
    async def test_status_endpoint(self):
        """Test the status endpoint."""
        if not self.blueprint_id:
            print("⚠️ No blueprint ID available for status test")
            return
        
        print(f"\n📊 Testing status endpoint...")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/blueprints/{self.blueprint_id}/status",
                headers={"X-User-ID": USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status endpoint working")
                print(f"   Status: {data.get('status')}")
                print(f"   Progress: {data.get('progress')}%")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"❌ Status endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing status endpoint: {str(e)}")
    
    async def test_websocket_status(self):
        """Test WebSocket status endpoint."""
        print(f"\n🔍 Testing WebSocket status endpoint...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/websocket/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ WebSocket status endpoint working")
                print(f"   Enabled: {data.get('enabled')}")
                print(f"   Active Sessions: {data.get('active_sessions')}")
            else:
                print(f"❌ WebSocket status endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing WebSocket status: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources."""
        if self.blueprint_id:
            print(f"\n🧹 Cleaning up...")
            await self.sio.emit('leave_blueprint_room', {
                'blueprint_id': self.blueprint_id
            })
        
        if self.sio.connected:
            await self.sio.disconnect()
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n📋 Test Summary")
        print(f"=" * 50)
        print(f"Total events received: {len(self.events_received)}")
        
        # Count events by type
        event_counts = {}
        for event in self.events_received:
            event_name = event['event']
            event_counts[event_name] = event_counts.get(event_name, 0) + 1
        
        for event_name, count in sorted(event_counts.items()):
            print(f"  {event_name}: {count}")
        
        if self.blueprint_id:
            print(f"\nBlueprint ID: {self.blueprint_id}")
        
        print(f"\nTest completed at: {datetime.now()}")

async def run_websocket_test():
    """Run the complete WebSocket test suite."""
    print("🧪 Starting WebSocket Integration Test")
    print("=" * 50)
    
    tester = WebSocketTester()
    
    try:
        # Test 1: Connect to WebSocket
        if not await tester.connect_websocket():
            print("❌ WebSocket connection failed - aborting test")
            return
        
        # Give connection time to stabilize
        await asyncio.sleep(2)
        
        # Test 2: Test ping/pong
        await tester.test_ping()
        
        # Test 3: Test WebSocket status endpoint
        await tester.test_websocket_status()
        
        # Test 4: Start blueprint generation
        if await tester.start_blueprint_generation():
            # Test 5: Wait for completion
            success = await tester.wait_for_completion(timeout=180)  # 3 minutes
            
            # Test 6: Test status endpoint
            await tester.test_status_endpoint()
            
            if success:
                print("🎉 All tests passed!")
            else:
                print("⚠️ Some tests failed or timed out")
        else:
            print("❌ Failed to start blueprint generation")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error during test: {str(e)}")
    finally:
        # Cleanup
        await tester.cleanup()
        tester.print_summary()

def test_health_endpoint():
    """Test the health endpoint to ensure server is running."""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   WebSocket Enabled: {data.get('websocket', {}).get('enabled')}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot reach server: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 SERP Strategist WebSocket Test Suite")
    print("=" * 60)
    
    # First, test if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running or not healthy")
        print("   Please start the server with: python src/main.py")
        exit(1)
    
    print("\n🔌 Server is running, starting WebSocket tests...")
    
    # Install required packages if not available
    try:
        import socketio
    except ImportError:
        print("❌ python-socketio not installed")
        print("   Please install with: pip install python-socketio[asyncio_client]")
        exit(1)
    
    # Run the async test
    asyncio.run(run_websocket_test())