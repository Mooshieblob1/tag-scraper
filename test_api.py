#!/usr/bin/env python3
"""
Simple test script to verify Danbooru API functionality
"""

import requests
import json
import time

def test_api():
    print("🧪 Testing Danbooru Artists API")
    print("=" * 40)
    
    # Test basic API call
    print("1. Testing basic API call...")
    try:
        response = requests.get('https://danbooru.donmai.us/artists.json?limit=5')
        response.raise_for_status()
        artists = response.json()
        print(f"✅ Success! Got {len(artists)} artists")
        
        if artists:
            print(f"   Sample artist: {artists[0]['name']}")
            print(f"   Available fields: {list(artists[0].keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test pagination
    print("\n2. Testing pagination...")
    try:
        response = requests.get('https://danbooru.donmai.us/artists.json?page=a0&limit=3')
        response.raise_for_status()
        page_a0 = response.json()
        
        time.sleep(0.2)  # Rate limiting
        
        response = requests.get('https://danbooru.donmai.us/artists.json?page=a1&limit=3')
        response.raise_for_status()
        page_a1 = response.json()
        
        print(f"✅ Page a0: {len(page_a0)} artists")
        print(f"✅ Page a1: {len(page_a1)} artists")
        
        if page_a0 and page_a1:
            print(f"   a0 first artist: {page_a0[0]['name']}")
            print(f"   a1 first artist: {page_a1[0]['name']}")
            
            # Check if pages are different
            if page_a0[0]['id'] != page_a1[0]['id']:
                print("✅ Pagination working correctly (different artists)")
            else:
                print("⚠️  Warning: Same artist on both pages")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test rate limiting
    print("\n3. Testing rate limiting...")
    start_time = time.time()
    for i in range(3):
        try:
            response = requests.get(f'https://danbooru.donmai.us/artists.json?page=a{i}&limit=1')
            response.raise_for_status()
            time.sleep(0.15)  # Small delay
        except Exception as e:
            print(f"❌ Error on request {i}: {e}")
            return False
    
    elapsed = time.time() - start_time
    rate = 3 / elapsed
    print(f"✅ Made 3 requests in {elapsed:.2f}s ({rate:.1f} req/sec)")
    
    if rate > 10:
        print("⚠️  Warning: Rate might be too high (>10 req/sec)")
    else:
        print("✅ Rate limiting looks good")
    
    print("\n🎉 All tests passed! API is working correctly.")
    print("\nReady to start scraping! Run:")
    print("  python scraper.py  (for command line)")
    print("  python app.py      (for web interface)")
    
    return True

if __name__ == "__main__":
    test_api()
