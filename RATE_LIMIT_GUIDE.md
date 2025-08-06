# Enhanced 429 Rate Limit Detection

## Overview

The Danbooru Artist Scraper now includes sophisticated 429 (Too Many Requests) detection and adaptive rate limiting to prevent rate limiting issues and automatically recover when they occur.

## Features

### 🚫 Advanced 429 Detection

- **Real-time Detection**: Automatically detects 429 HTTP responses
- **Retry-After Header Support**: Respects server-provided retry timing (RFC compliant)
- **Intelligent Exponential Backoff**: Uses smart algorithms when no server guidance is provided
- **Consecutive 429 Tracking**: Monitors patterns of rate limiting to adjust behavior

### 🔄 Adaptive Rate Limiting

- **Dynamic Rate Adjustment**: Automatically slows down when 429s are detected
- **Progressive Recovery**: Gradually returns to normal speed after successful requests
- **Cooldown Periods**: Implements temporary cooldowns after multiple 429s
- **Jitter Prevention**: Adds randomization to prevent thundering herd problems

### 📊 Health Monitoring

The system tracks four health states:

- **🟢 Healthy**: Normal operation, no recent 429s
- **🔄 Recovering**: Had 429s but making progress
- **🟡 Warning**: Some 429s detected, being cautious
- **🔴 Critical**: Multiple consecutive 429s, heavily rate limited

### 📈 Statistics and Monitoring

- **Total Request Count**: Track all API requests made
- **429 Error Count**: Total and consecutive 429 errors
- **Response Time Tracking**: Monitor API performance
- **Success Rate Monitoring**: Track consecutive successful requests

## How It Works

### Normal Operation

1. **Base Rate Limiting**: Starts at ~6.7 requests per second (conservative)
2. **Pre-request Checks**: Ensures proper spacing between requests
3. **Response Monitoring**: Tracks each response for 429 status codes

### When 429 is Detected

1. **Immediate Response**: 
   - Check for `Retry-After` header
   - Calculate appropriate wait time
   - Log detailed information

2. **Adaptive Behavior**:
   - Increase minimum request interval
   - Apply exponential backoff for retries
   - Set cooldown period if multiple 429s

3. **Recovery Process**:
   - Track consecutive successful requests
   - Gradually reduce rate limiting restrictions
   - Reset to normal operation after sufficient success

## Configuration

### Rate Limiting Parameters

```python
# Base configuration
min_request_interval = 0.15  # ~6.7 req/sec initially
max_rate_limit_wait = 300.0  # 5 minute maximum wait
adaptive_threshold_429s = 3  # Trigger adaptive after 3 429s
recovery_success_threshold = 10  # Reset after 10 successes
```

### Backoff Algorithm

The system uses intelligent exponential backoff:

```python
backoff_time = base_wait * (2 ** attempt) * consecutive_factor * jitter
```

Where:
- `base_wait`: Starting wait time (1 second)
- `attempt`: Current retry attempt number
- `consecutive_factor`: Multiplier based on consecutive 429s
- `jitter`: Random factor (0.8-1.2) to prevent thundering herd

## Usage

### Command Line Interface

The enhanced rate limiting works automatically in all scraping modes:

```bash
# Normal scraping with enhanced 429 detection
python scraper.py

# Test the rate limiting system
python rate_limit_monitor.py
```

### Web Interface

The Flask web app shows real-time rate limiting status:

- **Health indicator**: Color-coded status (🟢🟡🔴)
- **429 error count**: Total and consecutive errors
- **Adaptive status**: Shows when rate limiting is active
- **Cooldown timer**: Displays remaining cooldown time

### API Endpoints

#### `/rate-limit-status`

Returns comprehensive rate limiting status:

```json
{
  "current_rate_limit": "6.7 req/sec",
  "original_rate_limit": "6.7 req/sec", 
  "is_rate_limited": false,
  "total_requests": 1250,
  "total_429s": 3,
  "consecutive_429s": 0,
  "consecutive_successes": 15,
  "last_429_time": "2025-08-07T10:30:45",
  "adaptive_cooldown_active": false,
  "adaptive_cooldown_remaining": 0,
  "current_wait_time": 1.0,
  "max_wait_time": 300.0,
  "health_status": "healthy"
}
```

## Testing and Monitoring

### Rate Limit Monitor Tool

Use the included monitoring tool to test the system:

```bash
# Quick test
python rate_limit_monitor.py

# Choose option 1: Quick test (normal rate limiting)
# Choose option 2: Aggressive test (may trigger 429s)
# Choose option 3: Full test suite (comprehensive)
```

### Test Reports

The monitor generates detailed reports saved to `rate_limit_test_report.json`:

```json
{
  "test_summary": {
    "total_tests": 15,
    "tests_with_429s": 3,
    "max_consecutive_429s": 2,
    "test_success_rate": 80.0
  },
  "final_status": { /* detailed status */ },
  "test_results": [ /* individual test data */ ]
}
```

### Log Files

Enhanced logging provides detailed information:

```
2025-08-07 10:30:45 - INFO - 🌐 Fetching page a0 (attempt 1/5)
2025-08-07 10:30:46 - WARNING - 🚫 Rate limited (429) - Attempt 1
2025-08-07 10:30:46 - INFO - 📊 429 Stats: Total=1, Consecutive=1
2025-08-07 10:30:46 - INFO - 🕐 Server requested wait of 60 seconds
2025-08-07 10:30:46 - WARNING - 🔄 Adaptive rate limiting activated!
```

## Best Practices

### For Normal Usage

1. **Let it adapt**: The system automatically adjusts to server conditions
2. **Monitor health**: Check the web interface for health status
3. **Be patient**: During high server load, the system may slow down significantly
4. **Check logs**: Review logs for patterns of 429 errors

### For Development

1. **Test thoroughly**: Use the rate limit monitor before production runs
2. **Respect cooldowns**: Don't restart immediately after 429s
3. **Monitor statistics**: Track success rates and adjust if needed
4. **Use appropriate limits**: Don't set unrealistic page ranges

### For Troubleshooting

1. **Check health status**: 🔴 Critical status indicates serious issues
2. **Review 429 patterns**: Multiple consecutive 429s suggest server overload
3. **Wait for recovery**: Allow the system time to recover before restarting
4. **Verify API status**: Check if Danbooru is experiencing issues

## Adaptive Behavior Examples

### Scenario 1: Occasional 429s
- **Trigger**: 1-2 isolated 429 errors
- **Response**: Brief backoff, continue normal operation
- **Recovery**: Automatic after next successful request

### Scenario 2: Pattern of 429s  
- **Trigger**: 3+ 429s in short period
- **Response**: Reduce rate to ~3 req/sec, implement cooldown
- **Recovery**: Gradual over 10+ successful requests

### Scenario 3: Server Overload
- **Trigger**: 5+ consecutive 429s
- **Response**: Reduce to 0.5 req/sec, 5-30 minute cooldown
- **Recovery**: Very gradual, may take hours to fully recover

## Integration with Existing Code

The enhanced 429 detection is fully backward compatible. Existing code will automatically benefit from:

- ✅ Better error handling
- ✅ Automatic rate limit adjustment  
- ✅ Detailed logging and monitoring
- ✅ Web interface status updates
- ✅ No configuration changes required

## Technical Details

### Implementation Highlights

- **Thread-safe**: Safe for use in multi-threaded environments
- **Memory efficient**: Minimal overhead for monitoring
- **Robust error handling**: Handles network timeouts and JSON decode errors
- **Progress indication**: Shows progress bars for long waits
- **Real-time updates**: Web interface updates every 10 seconds

### Dependencies

The enhanced system uses only standard library components:
- `datetime` for time tracking
- `time` for delays and timing
- `random` for jitter in backoff calculations
- `tqdm` for progress bars during long waits

## Future Enhancements

Planned improvements include:

- 📊 **Historical Analytics**: Long-term rate limiting statistics
- 🎯 **Predictive Adjustment**: Machine learning-based rate optimization
- 🌐 **Multi-endpoint Support**: Different strategies for different API endpoints
- 📱 **Mobile Interface**: Rate limiting status on mobile devices
- 🔔 **Alert System**: Notifications for critical rate limiting events

---

For support or questions about the enhanced 429 detection system, check the logs or use the rate limit monitor tool for detailed diagnostics.
