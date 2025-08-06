#!/usr/bin/env python3
"""
Simple test script to demonstrate the enhanced 429 detection system
"""

from scraper import DanbooruArtistScraper
import json

def test_enhanced_rate_limiting():
    """Test the enhanced rate limiting features"""
    print("🧪 Testing Enhanced 429 Detection System")
    print("=" * 50)
    
    # Create scraper instance
    scraper = DanbooruArtistScraper()
    
    # Show initial status
    print("📊 Initial Rate Limiting Status:")
    initial_status = scraper.get_rate_limit_status()
    print(f"   Rate Limit: {initial_status['current_rate_limit']}")
    print(f"   Health: {initial_status['health_status']}")
    print(f"   Total Requests: {initial_status['total_requests']}")
    print(f"   Total 429s: {initial_status['total_429s']}")
    print()
    
    # Test a few pages
    print("🌐 Testing API requests with enhanced monitoring...")
    for i in range(3):
        page_id = f"a{i}"
        print(f"   Fetching page {page_id}...")
        
        artists = scraper.get_page(page_id)
        status = scraper.get_rate_limit_status()
        
        if artists:
            print(f"   ✅ Success: {len(artists)} artists")
        else:
            print(f"   ❌ Failed to fetch page {page_id}")
        
        print(f"   Health: {status['health_status']}")
        if status['total_429s'] > 0:
            print(f"   🚫 429 Errors: {status['total_429s']} total, {status['consecutive_429s']} consecutive")
        
        print()
    
    # Show final status
    print("📊 Final Rate Limiting Status:")
    final_status = scraper.get_rate_limit_status()
    print(json.dumps(final_status, indent=2, default=str))
    
    print("\n🎉 Test completed successfully!")
    print(f"   Requests made: {final_status['total_requests']}")
    print(f"   429 errors: {final_status['total_429s']}")
    print(f"   Health status: {final_status['health_status']}")

if __name__ == "__main__":
    test_enhanced_rate_limiting()
