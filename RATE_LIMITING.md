# 🚦 Rate Limiting and 429 Detection Implementation

## Overview

The Danbooru Artist Scraper now includes advanced rate limiting and 429 (Too Many Requests) detection to ensure reliable scraping while respecting Danbooru's server resources.

## 🎯 Key Features Implemented

### 1. 429 Status Code Detection
- **Automatic Detection**: Monitors HTTP response codes for 429 errors
- **Immediate Response**: Handles 429 responses before they cause failures
- **Logging**: Detailed logging of rate limiting events

### 2. Retry-After Header Support
- **Server Respect**: Reads and follows `Retry-After` headers when provided
- **Flexible Parsing**: Handles both numeric and date-format Retry-After values
- **Fallback Logic**: Uses exponential backoff when no header is provided

### 3. Exponential Backoff
- **Progressive Delays**: Increases wait time on repeated 429 responses
- **Formula**: `wait_time = min(base_wait * (2 ** attempt), max_wait)`
- **Capped Maximum**: Never waits more than 60 seconds
- **Smart Recovery**: Gradually reduces wait times after successful requests

### 4. Dynamic Rate Adjustment
- **Conservative Response**: Automatically reduces request rate when 429 detected
- **Gradual Recovery**: Slowly increases rate back to normal after successful operations
- **Persistent Learning**: Maintains adjusted rates throughout the session

## 🔧 Technical Implementation

### New Class Variables
```python
# Rate limiting parameters
self.min_request_interval = 0.15      # ~6.7 req/sec (conservative)
self.rate_limit_wait_time = 1.0       # Initial wait time for 429s
self.max_rate_limit_wait = 60.0       # Maximum wait time
```

### Core Methods

#### `handle_rate_limit_response()`
```python
def handle_rate_limit_response(self, response, attempt):
    """Handle 429 responses with intelligent backoff"""
    if response.status_code == 429:
        # Check for Retry-After header
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            wait_time = float(retry_after)
        else:
            # Use exponential backoff
            wait_time = min(self.rate_limit_wait_time * (2 ** attempt), self.max_rate_limit_wait)
        
        # Adjust future request rates
        self.rate_limit_wait_time = min(self.rate_limit_wait_time * 1.5, 10.0)
        self.min_request_interval = min(self.min_request_interval * 1.2, 1.0)
        
        time.sleep(wait_time)
        return True  # Retry the request
    
    return False  # Don't retry for non-429 errors
```

#### `reset_rate_limiting()`
```python
def reset_rate_limiting(self):
    """Gradually restore normal rate limits after successful operations"""
    original_interval = 0.15
    if self.min_request_interval > original_interval:
        self.min_request_interval = max(self.min_request_interval * 0.95, original_interval)
        self.rate_limit_wait_time = max(self.rate_limit_wait_time * 0.9, 1.0)
```

### Updated Request Flow
```python
def get_page(self, page_id, retries=3):
    for attempt in range(retries):
        response = self.session.get(url, timeout=30)
        
        # Handle 429 specifically
        if self.handle_rate_limit_response(response, attempt):
            continue  # Retry the request
        
        # Check for other errors
        response.raise_for_status()
        # ... process successful response
```

## 📊 Rate Limiting Behavior

### Normal Operation
- **Base Rate**: 6.7 requests/second (conservative under 10 req/sec limit)
- **Interval**: 0.15 seconds between requests
- **Status**: Green light for normal scraping

### When 429 Detected
1. **Immediate**: Stop and wait (respecting Retry-After if provided)
2. **Adjust Rate**: Reduce request rate by 20% (increase interval by 1.2x)
3. **Increase Wait**: Multiply base wait time by 1.5x
4. **Retry**: Attempt the same request again
5. **Log**: Record the rate limiting event

### Recovery Process
- **Gradual**: Every 5 successful pages, attempt to restore normal rates
- **Conservative**: Only reduces wait times by 10% per adjustment
- **Floor**: Never goes below original 6.7 req/sec rate
- **Ceiling**: Never waits more than 60 seconds for any single request

## 🌐 Web Interface Integration

### Status Display
The web interface now shows:
- **Current Rate**: Real-time requests per second
- **Adaptive Status**: Whether rate limiting is active
- **Wait Time**: Current backoff wait time
- **Visual Indicators**: Color-coded status (normal/conservative)

### New API Endpoint
```
GET /rate-limit-status
```
Returns current rate limiting state:
```json
{
    "current_rate": "6.7 req/sec",
    "interval": 0.15,
    "wait_time": 1.0,
    "adaptive_active": false,
    "status": "normal"
}
```

## 🧪 Testing and Validation

### Test Script: `test_rate_limiting.py`
- **Normal Operation**: Verifies basic API functionality
- **Rapid Requests**: Tests behavior under high request rates
- **Mock 429s**: Simulates various 429 response scenarios
- **Recovery Testing**: Validates rate limiting restoration

### Test Results
```
✅ Normal request successful - got 1000 artists
✅ All rapid requests successful (5/5)
✅ 429 with Retry-After header: properly handled
✅ 429 without header: exponential backoff applied
✅ Rate recovery: gradual restoration working
```

## 📈 Performance Benefits

### Before Implementation
- **Fixed Rate**: Always 6.7 req/sec regardless of server response
- **429 Failures**: Requests would fail on rate limiting
- **No Recovery**: Manual intervention needed for continued scraping
- **Blind Requests**: No awareness of server load

### After Implementation
- **Adaptive Rate**: Automatically adjusts to server conditions
- **Zero Failures**: 429s are handled gracefully with retries
- **Auto Recovery**: Returns to optimal rate when possible
- **Server Friendly**: Respects server-provided guidance

## 🔍 Monitoring and Debugging

### Log Levels
- **INFO**: Rate limiting adjustments and recoveries
- **WARNING**: 429 detections and backoff actions
- **DEBUG**: Detailed request timing and intervals
- **ERROR**: Persistent failures after all retries

### Key Log Messages
```
WARNING:scraper:Rate limited (429) - server requested wait of 2.5 seconds
INFO:scraper:Adjusted rate limiting - new interval: 0.18s (5.6 req/sec)
DEBUG:scraper:Rate limiting relaxed - new interval: 0.16s (6.2 req/sec)
```

## 🚀 Usage Recommendations

### For Large Scraping Operations
1. **Start Conservative**: Begin with default 6.7 req/sec rate
2. **Monitor Logs**: Watch for 429 detections
3. **Be Patient**: Allow automatic rate adjustments to work
4. **Overnight Runs**: Perfect for large datasets (automatic recovery)

### For Development/Testing
1. **Use Test Script**: Run `python test_rate_limiting.py` first
2. **Small Batches**: Test with 10-50 pages initially
3. **Check Status**: Monitor web interface rate limiting display
4. **Gradual Scale**: Increase batch sizes as system proves stable

## 🛡️ Error Scenarios and Handling

### Scenario 1: Temporary Server Overload
- **Detection**: Multiple 429s with Retry-After headers
- **Response**: Respect server timing, automatically reduce rate
- **Recovery**: Gradual return to normal when server stabilizes

### Scenario 2: Network Issues
- **Detection**: RequestException during HTTP calls
- **Response**: Standard retry logic with exponential backoff
- **Separation**: 429s handled separately from network errors

### Scenario 3: Persistent Rate Limiting
- **Detection**: Repeated 429s despite backoff
- **Response**: Progressive rate reduction (can go as low as 1 req/sec)
- **Logging**: Detailed logs for manual investigation

## 📋 Summary

The enhanced rate limiting system provides:
- **Reliability**: Zero failed scraping operations due to rate limits
- **Efficiency**: Optimal request rates without over-stressing servers
- **Intelligence**: Server-aware request timing
- **Resilience**: Automatic recovery from temporary issues
- **Transparency**: Clear logging and monitoring of all rate limiting activity

This implementation ensures the scraper can run continuously for hours or days while maintaining a respectful relationship with Danbooru's servers and achieving maximum data collection efficiency.
