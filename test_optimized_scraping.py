#!/usr/bin/env python3
"""
Test optimized post count fetching with smaller batches
"""

from scraper import DanbooruArtistScraper
import time

def test_optimized_scraping():
    """Test the optimized scraping with batch processing"""
    print("🧪 Testing Optimized Post Count Fetching")
    print("=" * 60)
    
    # Initialize scraper
    scraper = DanbooruArtistScraper()
    
    if not scraper.authenticated:
        print("❌ No API authentication found!")
        print("   Post counts will be 0 without authentication")
        print("   Add credentials to .env file for accurate counts")
        print("")
    else:
        print(f"✅ Authenticated as: {scraper.username}")
        print("")
    
    print("📄 Testing page scraping with different modes:")
    print("")
    
    # Test 1: Fast mode (no post counts)
    print("⚡ Test 1: Fast mode (no post counts)")
    start_time = time.time()
    artists_fast = scraper.scrape_page("a0", fetch_post_counts=False, batch_size=50)
    fast_time = time.time() - start_time
    print(f"   ✅ Completed in {fast_time:.1f} seconds")
    print(f"   📊 Found {len(artists_fast)} artists")
    if artists_fast:
        print(f"   🎨 Sample: {artists_fast[0]['name']} (post_count: {artists_fast[0]['post_count']})")
    print("")
    
    # Test 2: First 10 artists with post counts
    if scraper.authenticated:
        print("📊 Test 2: First 10 artists with post counts")
        start_time = time.time()
        
        # Get just first 10 artists for testing
        artists_json = scraper.get_page("a0")
        if artists_json:
            test_artists = []
            for i, artist_json in enumerate(artists_json[:10]):
                artist_data = scraper.parse_artist_data(artist_json, fetch_post_count=True)
                if artist_data:
                    test_artists.append(artist_data)
                    print(f"   {i+1}/10: {artist_data['name']} -> {artist_data['post_count']} posts")
        
        accurate_time = time.time() - start_time
        print(f"   ✅ Completed in {accurate_time:.1f} seconds")
        print(f"   📊 Average {accurate_time/10:.2f} seconds per artist")
        print("")
        
        # Estimate full page time
        estimated_full_time = accurate_time * 100  # 1000 artists / 10 sample
        print(f"📈 Estimated time for full page (1000 artists): {estimated_full_time/60:.1f} minutes")
    else:
        print("⚠️  Skipping accurate post count test (no authentication)")
    
    print("")
    print("💡 Recommendations:")
    print("   - Use fast mode for initial data collection")
    print("   - Use post count mode only when needed")
    print("   - Consider smaller page ranges with post counts enabled")
    
if __name__ == "__main__":
    test_optimized_scraping()
