# Manual API Testing Guide

Your server is running at `http://127.0.0.1:5000`. Here are manual tests you can run to validate your blueprint APIs.

## 1. Health Check Test

### Test Server Status
```bash
curl http://127.0.0.1:5000/api/health
```

**Expected Response:**
```json
{
  "status": "ok|degraded|error",
  "version": "2.0.0",
  "timestamp": "2025-01-02T...",
  "features": {
    "enhanced_processing": true/false,
    "database": true/false,
    "blueprint_routes": true/false
  },
  "services": {
    "keyword_processor": true/false,
    "serp_optimizer": true/false,
    "content_analyzer": true/false,
    "competitor_analyzer": true/false,
    "export_integration": true/false
  },
  "api_keys": {
    "serpapi": true/false,
    "gemini": true/false,
    "google_api": true/false
  }
}
```

## 2. Blueprint Generation Tests

### Test 1: Valid Blueprint Generation
```bash
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "content marketing"}'
```

**Expected Response (201 Created):**
```json
{
  "blueprint_id": "uuid-string",
  "keyword": "content marketing",
  "status": "completed",
  "generation_time": 25,
  "data": {
    "competitor_analysis": {...},
    "heading_structure": {...},
    "topic_clusters": {...},
    "serp_features": {...}
  }
}
```

### Test 2: Missing Keyword Error
```bash
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{}'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": "Keyword is required"
}
```

### Test 3: Missing Authentication
```bash
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -d '{"keyword": "test"}'
```

**Expected Response (401 Unauthorized):**
```json
{
  "error": "Authentication required"
}
```

### Test 4: Additional Keywords to Test
```bash
# SEO Strategy
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "SEO strategy"}'

# Digital Transformation
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "digital transformation"}'

# Artificial Intelligence
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "artificial intelligence"}'
```

## 3. Blueprint Retrieval Tests

### Test 1: List All Blueprints
```bash
curl http://127.0.0.1:5000/api/blueprints \
  -H "X-User-ID: test-user-1"
```

**Expected Response:**
```json
{
  "blueprints": [
    {
      "id": "uuid",
      "keyword": "content marketing",
      "status": "completed",
      "created_at": "2025-01-02T...",
      "user_id": "test-user-1"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Test 2: Get Specific Blueprint (use ID from generation response)
```bash
# Replace BLUEPRINT_ID with actual ID from generation response
curl http://127.0.0.1:5000/api/blueprints/BLUEPRINT_ID \
  -H "X-User-ID: test-user-1"
```

**Expected Response:**
```json
{
  "id": "uuid",
  "keyword": "content marketing",
  "user_id": "test-user-1",
  "competitor_analysis": {
    "keyword": "content marketing",
    "competitors": [...],
    "insights": {...}
  },
  "heading_structure": {
    "h1": "Complete Guide to Content Marketing...",
    "h2_sections": [...]
  },
  "topic_clusters": [...],
  "serp_features": {...},
  "created_at": "2025-01-02T...",
  "status": "completed"
}
```

### Test 3: Pagination
```bash
curl "http://127.0.0.1:5000/api/blueprints?limit=2&offset=0" \
  -H "X-User-ID: test-user-1"
```

### Test 4: Search Blueprints
```bash
curl "http://127.0.0.1:5000/api/blueprints?search=marketing" \
  -H "X-User-ID: test-user-1"
```

## 4. Error Handling Tests

### Test 1: Non-existent Blueprint
```bash
curl http://127.0.0.1:5000/api/blueprints/non-existent-id \
  -H "X-User-ID: test-user-1"
```

**Expected Response (404 Not Found):**
```json
{
  "error": "Blueprint not found"
}
```

### Test 2: Invalid Endpoint
```bash
curl http://127.0.0.1:5000/api/invalid-endpoint
```

**Expected Response (404 Not Found):**
```json
{
  "error": "Endpoint not found",
  "available_endpoints": [
    "/api/blueprints/generate",
    "/api/blueprints",
    "/api/health",
    "/api/user/stats"
  ]
}
```

## 5. Edge Cases

### Test 1: Very Long Keyword (should fail)
```bash
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "'$(printf 'a%.0s' {1..300})'"}'
```

### Test 2: Empty Keyword (should fail)
```bash
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": ""}'
```

### Test 3: Special Characters
```bash
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "e-commerce & digital marketing!"}'
```

## 6. Performance Tests

### Test 1: Concurrent Requests (run multiple in parallel)
```bash
# Run these simultaneously in different terminals
curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-1" \
  -d '{"keyword": "performance test 1"}' &

curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-2" \
  -d '{"keyword": "performance test 2"}' &

curl -X POST http://127.0.0.1:5000/api/blueprints/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-3" \
  -d '{"keyword": "performance test 3"}' &
```

## Expected Behavior Summary

### Blueprint Generation API
- ✅ **Success Case**: Returns 201 with blueprint data, ID, and generation time
- ✅ **Fallback Mode**: If API keys missing, returns fallback blueprint with note
- ✅ **Timeout Protection**: 2.5 minute timeout with fallback
- ✅ **Validation**: Rejects empty keywords, too-long keywords
- ✅ **Authentication**: Requires X-User-ID header

### Blueprint Retrieval API
- ✅ **Success Case**: Returns 200 with full blueprint data
- ✅ **Security**: Only returns blueprints for authenticated user
- ✅ **Error Handling**: 404 for non-existent blueprints
- ✅ **Data Integrity**: Complete blueprint structure with all sections

### Blueprint Listing API
- ✅ **Pagination**: Supports limit/offset parameters
- ✅ **Search**: Keyword search functionality
- ✅ **Filtering**: Project-based filtering
- ✅ **Performance**: Efficient listing with metadata

## Test Results Interpretation

### Health Check Results
- **"ok"**: All systems operational
- **"degraded"**: Some features unavailable but core functionality works
- **"error"**: Significant issues detected

### API Key Status Impact
- **No API Keys**: Uses fallback blueprint generation (limited features)
- **SerpAPI Only**: Real search data, limited AI analysis
- **Gemini Only**: AI analysis available, limited search data  
- **Both APIs**: Full functionality with real data and AI insights

### Performance Expectations
- **Generation Time**: 15-45 seconds with APIs, 3-5 seconds fallback
- **Retrieval Time**: <1 second for existing blueprints
- **Listing Time**: <2 seconds for paginated results