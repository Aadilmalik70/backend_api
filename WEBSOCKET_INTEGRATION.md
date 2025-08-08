# WebSocket Integration Guide for Frontend

This document provides comprehensive guidance for integrating the real-time blueprint generation WebSocket features with the Next.js frontend.

## Overview

The SERP Strategist backend now supports real-time blueprint generation with WebSocket communication, providing live progress updates during the ~60-second generation process.

## Architecture

### Backend Components

1. **WebSocket Service** (`src/services/websocket_service.py`)
   - Manages WebSocket connections and real-time communication
   - Handles session management and room-based messaging
   - Provides progress tracking and status updates

2. **Realtime Blueprint Generator** (`src/services/realtime_blueprint_generator.py`)
   - Extended blueprint generator with WebSocket integration
   - Provides real-time progress updates during generation
   - Supports both full and quick generation modes

3. **Realtime Routes** (`src/routes/realtime_blueprints.py`)
   - RESTful endpoints with WebSocket integration
   - Background processing with immediate response
   - Session status and management endpoints

### Frontend Integration Points

The frontend needs to implement:
1. WebSocket client connection
2. Real-time progress tracking components
3. Optimistic UI updates with rollback capability
4. Automatic reconnection logic

## API Endpoints

### Realtime Blueprint Generation

#### `POST /api/blueprints/generate-realtime`

Generate a blueprint with real-time WebSocket updates.

**Request:**
```json
{
  "keyword": "content marketing",
  "project_id": "optional-project-id",
  "enable_websocket": true
}
```

**Response (202 Accepted):**
```json
{
  "blueprint_id": "uuid",
  "keyword": "content marketing",
  "status": "started",
  "websocket_enabled": true,
  "websocket_room": "blueprint_uuid",
  "estimated_time": 45,
  "message": "Blueprint generation started. Connect to WebSocket for real-time updates.",
  "websocket_events": [
    "progress_update",
    "step_completed", 
    "generation_complete",
    "generation_failed"
  ],
  "connection_info": {
    "join_room_event": "join_blueprint_room",
    "room_data": {
      "blueprint_id": "uuid",
      "user_id": "user-123"
    }
  }
}
```

#### `POST /api/blueprints/generate-quick-realtime`

Generate a quick blueprint with real-time updates (faster processing).

**Request:**
```json
{
  "keyword": "content marketing",
  "enable_websocket": true
}
```

**Response (202 Accepted):**
```json
{
  "blueprint_id": "uuid",
  "keyword": "content marketing", 
  "status": "started",
  "websocket_enabled": true,
  "websocket_room": "blueprint_uuid",
  "estimated_time": 15,
  "blueprint_type": "quick"
}
```

### Status and Management

#### `GET /api/blueprints/{blueprint_id}/status`

Get current status of a blueprint generation session.

**Response:**
```json
{
  "blueprint_id": "uuid",
  "status": "in_progress",
  "progress": 65,
  "current_step": 3,
  "total_steps": 6,
  "message": "Generating topic clusters...",
  "websocket_session_active": true,
  "started_at": "2025-01-01T12:00:00Z",
  "last_updated": "2025-01-01T12:02:30Z"
}
```

#### `GET /api/websocket/active-sessions`

Get active WebSocket sessions for the current user.

**Response:**
```json
{
  "user_sessions": [
    {
      "blueprint_id": "uuid",
      "status": "in_progress",
      "progress": 45,
      "current_step": 2,
      "total_steps": 6,
      "started_at": "2025-01-01T12:00:00Z",
      "websocket_room": "blueprint_uuid"
    }
  ],
  "total_active": 1
}
```

## WebSocket Events

### Connection Management

#### Client Events (Send to Server)

**`connect`**
- Establishes WebSocket connection
- Automatically handled by Socket.IO client

**`join_blueprint_room`**
```javascript
socket.emit('join_blueprint_room', {
  blueprint_id: 'uuid',
  user_id: 'user-123'
});
```

**`leave_blueprint_room`**
```javascript
socket.emit('leave_blueprint_room', {
  blueprint_id: 'uuid'
});
```

**`ping`**
```javascript
socket.emit('ping');
```

#### Server Events (Receive from Server)

**`connection_status`**
```json
{
  "status": "connected",
  "client_id": "socket-id",
  "timestamp": "2025-01-01T12:00:00Z",
  "server": "SERP Strategist API"
}
```

**`room_joined`**
```json
{
  "blueprint_id": "uuid",
  "room": "blueprint_uuid",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

**`pong`**
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "server_time": 1704110400.123
}
```

### Blueprint Generation Events

**`generation_started`**
```json
{
  "blueprint_id": "uuid",
  "total_steps": 6,
  "status": "started",
  "message": "Blueprint generation started",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

**`progress_update`**
```json
{
  "blueprint_id": "uuid",
  "step": 3,
  "step_name": "topic_clusters",
  "total_steps": 6,
  "progress": 50,
  "status": "in_progress",
  "message": "Creating topic clusters and keyword groups...",
  "timestamp": "2025-01-01T12:01:30Z",
  "details": {
    "clusters_created": 4
  }
}
```

**`step_completed`**
```json
{
  "blueprint_id": "uuid",
  "step": 3,
  "step_name": "topic_clusters",
  "status": "completed",
  "message": "Completed: topic_clusters",
  "timestamp": "2025-01-01T12:01:45Z",
  "result": {
    "clusters_created": 4
  }
}
```

**`generation_complete`**
```json
{
  "blueprint_id": "uuid",
  "status": "completed",
  "progress": 100,
  "message": "Blueprint generation completed successfully",
  "generation_time": 45,
  "blueprint_data": { /* full blueprint data */ },
  "timestamp": "2025-01-01T12:00:45Z"
}
```

**`generation_failed`**
```json
{
  "blueprint_id": "uuid",
  "status": "failed",
  "message": "Blueprint generation failed: API timeout",
  "error": "API timeout",
  "timestamp": "2025-01-01T12:01:00Z",
  "error_details": {
    "error_type": "TimeoutError",
    "keyword": "content marketing",
    "user_id": "user-123"
  }
}
```

## Frontend Implementation Guide

### 1. WebSocket Client Setup

```typescript
// websocketClient.ts
import { io, Socket } from 'socket.io-client';

interface WebSocketClient {
  socket: Socket | null;
  connect: (userId: string) => Promise<void>;
  disconnect: () => void;
  joinBlueprintRoom: (blueprintId: string, userId: string) => void;
  leaveBlueprintRoom: (blueprintId: string) => void;
  onProgressUpdate: (callback: (data: ProgressUpdate) => void) => void;
  onGenerationComplete: (callback: (data: GenerationComplete) => void) => void;
  onGenerationFailed: (callback: (data: GenerationFailed) => void) => void;
}

class WebSocketService implements WebSocketClient {
  socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  async connect(userId: string): Promise<void> {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000', {
      query: { user_id: userId },
      transports: ['websocket', 'polling'],
      timeout: 10000,
      autoConnect: true
    });

    return new Promise((resolve, reject) => {
      this.socket!.on('connect', () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        resolve();
      });

      this.socket!.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        reject(error);
      });

      this.socket!.on('disconnect', () => {
        console.log('WebSocket disconnected');
        this.handleReconnection(userId);
      });

      this.socket!.on('connection_status', (data) => {
        console.log('Connection status:', data);
      });
    });
  }

  private async handleReconnection(userId: string): Promise<void> {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
      
      console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
      
      setTimeout(() => {
        this.connect(userId);
      }, delay);
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  joinBlueprintRoom(blueprintId: string, userId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('join_blueprint_room', {
        blueprint_id: blueprintId,
        user_id: userId
      });
    }
  }

  leaveBlueprintRoom(blueprintId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('leave_blueprint_room', {
        blueprint_id: blueprintId
      });
    }
  }

  onProgressUpdate(callback: (data: ProgressUpdate) => void): void {
    this.socket?.on('progress_update', callback);
  }

  onStepCompleted(callback: (data: StepCompleted) => void): void {
    this.socket?.on('step_completed', callback);
  }

  onGenerationComplete(callback: (data: GenerationComplete) => void): void {
    this.socket?.on('generation_complete', callback);
  }

  onGenerationFailed(callback: (data: GenerationFailed) => void): void {
    this.socket?.on('generation_failed', callback);
  }

  // Cleanup method to remove all listeners
  removeAllListeners(): void {
    this.socket?.removeAllListeners();
  }
}

export const websocketService = new WebSocketService();
```

### 2. React Hook for Real-time Blueprint Generation

```typescript
// hooks/useRealtimeBlueprintGeneration.ts
import { useState, useEffect, useCallback } from 'react';
import { websocketService } from '../services/websocketClient';

interface BlueprintGenerationState {
  blueprintId: string | null;
  status: 'idle' | 'starting' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  currentStep: number;
  totalSteps: number;
  message: string;
  error: string | null;
  blueprintData: any | null;
  estimatedTime: number;
}

export const useRealtimeBlueprintGeneration = (userId: string) => {
  const [state, setState] = useState<BlueprintGenerationState>({
    blueprintId: null,
    status: 'idle',
    progress: 0,
    currentStep: 0,
    totalSteps: 0,
    message: '',
    error: null,
    blueprintData: null,
    estimatedTime: 0
  });

  const [isConnected, setIsConnected] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const initializeConnection = async () => {
      try {
        await websocketService.connect(userId);
        setIsConnected(true);
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        setIsConnected(false);
      }
    };

    initializeConnection();

    return () => {
      websocketService.disconnect();
      setIsConnected(false);
    };
  }, [userId]);

  // Setup event listeners
  useEffect(() => {
    if (!isConnected) return;

    websocketService.onProgressUpdate((data) => {
      setState(prev => ({
        ...prev,
        progress: data.progress,
        currentStep: data.step,
        totalSteps: data.total_steps,
        message: data.message,
        status: 'in_progress'
      }));
    });

    websocketService.onStepCompleted((data) => {
      setState(prev => ({
        ...prev,
        message: `Completed: ${data.step_name}`
      }));
    });

    websocketService.onGenerationComplete((data) => {
      setState(prev => ({
        ...prev,
        status: 'completed',
        progress: 100,
        message: 'Blueprint generation completed successfully',
        blueprintData: data.blueprint_data
      }));
    });

    websocketService.onGenerationFailed((data) => {
      setState(prev => ({
        ...prev,
        status: 'failed',
        error: data.error,
        message: data.message
      }));
    });

    return () => {
      websocketService.removeAllListeners();
    };
  }, [isConnected]);

  const startGeneration = useCallback(async (keyword: string, quickMode = false) => {
    if (!isConnected) {
      throw new Error('WebSocket not connected');
    }

    setState({
      blueprintId: null,
      status: 'starting',
      progress: 0,
      currentStep: 0,
      totalSteps: 0,
      message: 'Starting blueprint generation...',
      error: null,
      blueprintData: null,
      estimatedTime: 0
    });

    try {
      const endpoint = quickMode 
        ? '/api/blueprints/generate-quick-realtime'
        : '/api/blueprints/generate-realtime';

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify({
          keyword,
          enable_websocket: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.websocket_enabled) {
        // Join the blueprint room for real-time updates
        websocketService.joinBlueprintRoom(data.blueprint_id, userId);
        
        setState(prev => ({
          ...prev,
          blueprintId: data.blueprint_id,
          status: 'in_progress',
          estimatedTime: data.estimated_time,
          message: data.message
        }));
      } else {
        // Fallback - blueprint completed synchronously
        setState(prev => ({
          ...prev,
          blueprintId: data.blueprint_id,
          status: 'completed',
          progress: 100,
          blueprintData: data.data,
          message: 'Blueprint generated successfully'
        }));
      }

      return data.blueprint_id;
    } catch (error) {
      setState(prev => ({
        ...prev,
        status: 'failed',
        error: error.message,
        message: 'Failed to start blueprint generation'
      }));
      throw error;
    }
  }, [isConnected, userId]);

  const cancelGeneration = useCallback(() => {
    if (state.blueprintId) {
      websocketService.leaveBlueprintRoom(state.blueprintId);
    }
    setState(prev => ({
      ...prev,
      status: 'idle',
      blueprintId: null,
      progress: 0,
      currentStep: 0,
      totalSteps: 0,
      message: '',
      error: null
    }));
  }, [state.blueprintId]);

  return {
    ...state,
    isConnected,
    startGeneration,
    cancelGeneration
  };
};
```

### 3. Progress Component

```typescript
// components/RealtimeProgressTracker.tsx
import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';

interface RealtimeProgressTrackerProps {
  status: 'idle' | 'starting' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  currentStep: number;
  totalSteps: number;
  message: string;
  error: string | null;
  estimatedTime: number;
  onCancel?: () => void;
}

const STEP_NAMES = {
  1: 'Comprehensive Analysis',
  2: 'Heading Structure',
  3: 'Topic Clusters',
  4: 'Content Outline',
  5: 'SEO Recommendations',
  6: 'Final Compilation'
};

export const RealtimeProgressTracker: React.FC<RealtimeProgressTrackerProps> = ({
  status,
  progress,
  currentStep,
  totalSteps,
  message,
  error,
  estimatedTime,
  onCancel
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'starting':
      case 'in_progress':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'starting':
      case 'in_progress':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (status === 'idle') {
    return null;
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          {getStatusIcon()}
          <span className={getStatusColor()}>
            {status === 'starting' && 'Starting Generation...'}
            {status === 'in_progress' && 'Generating Blueprint'}
            {status === 'completed' && 'Blueprint Complete'}
            {status === 'failed' && 'Generation Failed'}
          </span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        {status === 'in_progress' && (
          <div className="space-y-2">
            <Progress value={progress} className="w-full" />
            <div className="flex justify-between text-sm text-gray-500">
              <span>Step {currentStep} of {totalSteps}</span>
              <span>{progress}%</span>
            </div>
          </div>
        )}

        {/* Current Step */}
        {status === 'in_progress' && currentStep > 0 && (
          <div className="text-sm">
            <span className="font-medium text-gray-700">
              {STEP_NAMES[currentStep] || `Step ${currentStep}`}
            </span>
          </div>
        )}

        {/* Status Message */}
        <div className="text-sm text-gray-600">
          {message}
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
            {error}
          </div>
        )}

        {/* Estimated Time */}
        {estimatedTime > 0 && status === 'in_progress' && (
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>Est. {estimatedTime}s remaining</span>
          </div>
        )}

        {/* Cancel Button */}
        {(status === 'starting' || status === 'in_progress') && onCancel && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onCancel}
            className="w-full"
          >
            Cancel Generation
          </Button>
        )}

        {/* Step Progress Indicators */}
        {status === 'in_progress' && totalSteps > 0 && (
          <div className="flex justify-between items-center mt-4">
            {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
              <div
                key={step}
                className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-medium ${
                  step < currentStep
                    ? 'bg-green-500 border-green-500 text-white'
                    : step === currentStep
                    ? 'bg-blue-500 border-blue-500 text-white'
                    : 'bg-gray-100 border-gray-300 text-gray-500'
                }`}
              >
                {step < currentStep ? '✓' : step}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
```

### 4. Blueprint Generation Page Integration

```typescript
// pages/blueprints/generate.tsx or components/BlueprintGenerator.tsx
import React, { useState } from 'react';
import { useRealtimeBlueprintGeneration } from '@/hooks/useRealtimeBlueprintGeneration';
import { RealtimeProgressTracker } from '@/components/RealtimeProgressTracker';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const BlueprintGenerator: React.FC = () => {
  const [keyword, setKeyword] = useState('');
  const [quickMode, setQuickMode] = useState(false);
  const userId = 'user-123'; // Get from auth context

  const {
    status,
    progress,
    currentStep,
    totalSteps,
    message,
    error,
    blueprintData,
    estimatedTime,
    isConnected,
    startGeneration,
    cancelGeneration
  } = useRealtimeBlueprintGeneration(userId);

  const handleGenerate = async () => {
    if (!keyword.trim()) return;
    
    try {
      await startGeneration(keyword.trim(), quickMode);
    } catch (error) {
      console.error('Failed to start generation:', error);
    }
  };

  const isGenerating = status === 'starting' || status === 'in_progress';

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Generate Content Blueprint</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label htmlFor="keyword" className="block text-sm font-medium mb-2">
              Target Keyword
            </label>
            <Input
              id="keyword"
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Enter your target keyword..."
              disabled={isGenerating}
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              id="quickMode"
              type="checkbox"
              checked={quickMode}
              onChange={(e) => setQuickMode(e.target.checked)}
              disabled={isGenerating}
            />
            <label htmlFor="quickMode" className="text-sm">
              Quick generation (faster, fewer details)
            </label>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleGenerate}
              disabled={!keyword.trim() || isGenerating || !isConnected}
              className="flex-1"
            >
              {isGenerating ? 'Generating...' : 'Generate Blueprint'}
            </Button>
            
            {isGenerating && (
              <Button
                variant="outline"
                onClick={cancelGeneration}
              >
                Cancel
              </Button>
            )}
          </div>

          {!isConnected && (
            <div className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded">
              WebSocket disconnected. Real-time updates may not work.
            </div>
          )}
        </CardContent>
      </Card>

      <RealtimeProgressTracker
        status={status}
        progress={progress}
        currentStep={currentStep}
        totalSteps={totalSteps}
        message={message}
        error={error}
        estimatedTime={estimatedTime}
        onCancel={cancelGeneration}
      />

      {status === 'completed' && blueprintData && (
        <Card>
          <CardHeader>
            <CardTitle>Blueprint Generated Successfully</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-gray-50 p-4 rounded overflow-auto max-h-96">
              {JSON.stringify(blueprintData, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

## Production Considerations

### 1. Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:5000
# or for production:
NEXT_PUBLIC_API_URL=https://api.serpstrategist.com
```

### 2. Error Handling

- Implement comprehensive error boundaries
- Handle WebSocket connection failures gracefully
- Provide fallback to standard generation when WebSocket unavailable
- Log errors for monitoring and debugging

### 3. Performance Optimization

- Use React.memo for progress components
- Implement proper cleanup of WebSocket listeners
- Consider using React Query for API state management
- Implement proper loading states and skeleton screens

### 4. Security

- Validate user authentication on WebSocket connection
- Implement proper CORS configuration
- Use secure WebSocket connections (WSS) in production
- Sanitize all user inputs

### 5. Testing

- Unit tests for WebSocket service
- Integration tests for real-time components
- End-to-end tests for complete blueprint generation flow
- Load testing for WebSocket scalability

## Troubleshooting

### Common Issues

1. **WebSocket Connection Fails**
   - Check CORS configuration
   - Verify API URL and port
   - Check firewall settings

2. **Real-time Updates Not Working**
   - Ensure proper room joining
   - Check WebSocket event listeners
   - Verify user authentication

3. **Generation Timeouts**
   - Increase timeout values
   - Implement proper error handling
   - Add retry mechanisms

### Debug Tools

- Browser Developer Tools Network tab
- WebSocket frame inspection
- Server logs for WebSocket events
- Client-side logging for event flow

This comprehensive integration guide provides everything needed to implement real-time blueprint generation with WebSocket support in the Next.js frontend.