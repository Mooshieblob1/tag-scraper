#!/usr/bin/env python3
"""
Test script to verify 429 rate limiting detection and handling
"""

import requests
import time
import logging
from scraper import DanbooruArtistScraper

def test_rate_limiting():
    print("🧪 Testing 429 Rate Limiting Detection")
    print("=" * 50)
    
    # Create scraper instance with debug logging
    logging.basicConfig(level=logging.DEBUG)
    scraper = DanbooruArtistScraper()
    
    print(f"Initial rate limit: {1/scraper.min_request_interval:.1f} req/sec")
    print(f"Initial wait time: {scraper.rate_limit_wait_time:.1f} seconds")
    print("")
    
    # Test 1: Normal operation
    print("1. Testing normal operation...")
    try:
        artists = scraper.get_page("a0")
        if artists is not None:
            print(f"✅ Normal request successful - got {len(artists)} artists")
        else:
            print("❌ Normal request failed")
    except Exception as e:
        print(f"❌ Error in normal request: {e}")
    
    time.sleep(1)
    
    # Test 2: Rapid requests to potentially trigger rate limiting
    print("\n2. Testing rapid requests (may trigger 429)...")
    
    # Temporarily reduce rate limiting to make it more likely to hit 429
    original_interval = scraper.min_request_interval
    scraper.min_request_interval = 0.05  # 20 req/sec - likely to trigger 429
    
    print(f"Temporarily increased rate to {1/scraper.min_request_interval:.1f} req/sec")
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(5):
        print(f"\nRequest {i+1}/5:")
        try:
            artists = scraper.get_page(f"a{i}")
            if artists is not None:
                success_count += 1
                print(f"  ✅ Success - got {len(artists)} artists")
            else:
                print("  ❌ Failed")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Check if rate limiting was adjusted
        if scraper.min_request_interval > original_interval:
            rate_limited_count += 1
            print(f"  📉 Rate limiting detected and adjusted to {1/scraper.min_request_interval:.1f} req/sec")
    
    # Test 3: Manual 429 simulation
    print("\n3. Testing manual 429 response handling...")
    
    # Create a mock response object to test 429 handling
    class MockResponse:
        def __init__(self, status_code, headers=None):
            self.status_code = status_code
            self.headers = headers or {}
    
    # Test with Retry-After header
    mock_429_with_header = MockResponse(429, {'Retry-After': '2.5'})
    should_retry = scraper.handle_rate_limit_response(mock_429_with_header, 0)
    print(f"  429 with Retry-After header: should_retry={should_retry}")
    
    # Test without Retry-After header
    mock_429_no_header = MockResponse(429, {})
    should_retry = scraper.handle_rate_limit_response(mock_429_no_header, 1)
    print(f"  429 without Retry-After header: should_retry={should_retry}")
    
    # Test successful response
    mock_200 = MockResponse(200)
    should_retry = scraper.handle_rate_limit_response(mock_200, 0)
    print(f"  200 success response: should_retry={should_retry}")
    
    # Restore original rate limiting
    scraper.min_request_interval = original_interval
    
    print(f"\n📊 Test Results:")
    print(f"  Successful requests: {success_count}/5")
    print(f"  Rate limiting adjustments: {rate_limited_count}")
    print(f"  Final rate limit: {1/scraper.min_request_interval:.1f} req/sec")
    print(f"  Final wait time: {scraper.rate_limit_wait_time:.1f} seconds")
    
    print("\n✅ Rate limiting test completed!")
    print("\nKey features implemented:")
    print("  • 429 status code detection")
    print("  • Retry-After header parsing")
    print("  • Exponential backoff")
    print("  • Dynamic rate adjustment")
    print("  • Gradual rate recovery")

if __name__ == "__main__":
    test_rate_limiting()
