#!/usr/bin/env python3
"""
Test script to verify post count fetching functionality
"""

from scraper import DanbooruArtistScraper
import json

def test_post_count_fetching():
    """Test the new post count fetching functionality"""
    print("🧪 Testing Post Count Fetching")
    print("=" * 50)
    
    # Initialize scraper
    scraper = DanbooruArtistScraper()
    
    # Test getting post count for a known artist
    test_artists = ["kantoku", "k-on!", "ntr"]  # These should have posts
    
    print("Testing individual post count fetching:")
    for artist_name in test_artists:
        print(f"  🎨 {artist_name}: ", end="", flush=True)
        post_count = scraper.get_artist_post_count(artist_name)
        print(f"{post_count} posts")
    
    print("\nTesting page scraping with post counts:")
    
    # Test scraping one page with post counts
    print("📄 Scraping page a0 WITH post counts...")
    artists_with_counts = scraper.scrape_page("a0", fetch_post_counts=True)
    
    print("📄 Scraping page a0 WITHOUT post counts...")
    artists_without_counts = scraper.scrape_page("a0", fetch_post_counts=False)
    
    print(f"\n📊 Results:")
    print(f"  With post counts: {len(artists_with_counts)} artists")
    print(f"  Without post counts: {len(artists_without_counts)} artists")
    
    if artists_with_counts:
        print(f"\nSample artist with post count:")
        sample = artists_with_counts[0]
        print(f"  Name: {sample['name']}")
        print(f"  Post count: {sample['post_count']}")
        print(f"  Other names: {sample['other_names']}")
        print(f"  Is active: {sample['is_active']}")
    
    if artists_without_counts:
        print(f"\nSample artist without post count:")
        sample = artists_without_counts[0]
        print(f"  Name: {sample['name']}")
        print(f"  Post count: {sample['post_count']} (should be 0)")
        print(f"  Other names: {sample['other_names']}")
        print(f"  Is active: {sample['is_active']}")
    
    print("\n✅ Post count fetching test completed!")

if __name__ == "__main__":
    test_post_count_fetching()
