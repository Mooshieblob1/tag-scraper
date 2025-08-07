#!/usr/bin/env python3
"""
Test script to verify image preview functionality
"""

from scraper import DanbooruArtistScraper
import json

def test_image_previews():
    """Test the new image preview functionality"""
    print("🖼️ Testing Image Preview Functionality")
    print("=" * 50)
    
    # Initialize scraper
    scraper = DanbooruArtistScraper()
    
    # Test artists that should have images
    test_artists = ["kantoku", "yugen"]  # Popular artists
    
    for artist_name in test_artists:
        print(f"\n🎨 Testing images for: {artist_name}")
        print("-" * 30)
        
        # Get sample images
        images = scraper.get_artist_sample_images(artist_name, limit=3)
        
        if images:
            print(f"✅ Found {len(images)} sample images:")
            for i, image in enumerate(images, 1):
                print(f"  {i}. ID: {image['id']}")
                print(f"     Rating: {image['rating']} (Safe/Questionable/Explicit)")
                print(f"     Score: {image['score']}")
                print(f"     Size: {image['image_width']}x{image['image_height']}")
                print(f"     Preview: {image['preview_url'][:50]}...")
                if image['tags']:
                    print(f"     Tags: {', '.join(image['tags'][:3])}...")
                print()
        else:
            print(f"❌ No images found for {artist_name}")
    
    # Test API endpoint format
    print("\n🔗 Testing API endpoint format:")
    print("   GET /artist/<artist_name>/images?limit=4")
    print("   Example: /artist/kantoku/images?limit=4")
    
    print("\n✅ Image preview test completed!")

if __name__ == "__main__":
    test_image_previews()
