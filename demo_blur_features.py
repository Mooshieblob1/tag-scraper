#!/usr/bin/env python3
"""
Demo script to show the new blur toggle and rating prioritization features
"""

from scraper import DanbooruArtistScraper

def demo_blur_and_rating_features():
    """Demonstrate the new blur toggle and rating prioritization"""
    print("🎨 DEMO: Blur Toggle & Rating Prioritization")
    print("=" * 60)
    
    scraper = DanbooruArtistScraper()
    
    print("✨ NEW FEATURES:")
    print("1. 🔍 Rating Priority: General → Sensitive → Questionable → Explicit")
    print("2. 🌫️  Auto-Blur: Questionable & Explicit content blurred by default")
    print("3. 🎛️  Toggle Control: Users can enable/disable blur per artist")
    print("4. 🏷️  Better Labels: Clear rating badges (General/Sensitive/Questionable/Explicit)")
    print()
    
    # Test with a few artists to show different rating distributions
    test_artists = ["kantoku", "as109"]
    
    for artist_name in test_artists:
        print(f"🎨 Artist: {artist_name}")
        print("-" * 40)
        
        images = scraper.get_artist_sample_images(artist_name, limit=4)
        
        if images:
            print(f"Found {len(images)} images (sorted by rating priority):")
            
            for i, image in enumerate(images, 1):
                rating = image['rating']
                rating_names = {
                    'g': 'General (Safe)',
                    's': 'Sensitive', 
                    'q': 'Questionable (Blurred by default)',
                    'e': 'Explicit (Blurred by default)'
                }
                
                blur_status = "🌫️ BLURRED" if rating in ['q', 'e'] else "👁️ VISIBLE"
                
                print(f"  {i}. Rating: {rating_names.get(rating, 'Unknown')} - {blur_status}")
                print(f"     Score: {image['score']}, Size: {image['image_width']}x{image['image_height']}")
        else:
            print("  No images found for this artist")
        
        print()
    
    print("🌐 WEB INTERFACE FEATURES:")
    print("• Click 'Preview Images' next to any artist in search results")
    print("• Questionable/Explicit images are blurred by default")
    print("• Use the 'Blur questionable/explicit content' checkbox to toggle")
    print("• Hover over blurred images to partially reveal them")
    print("• Click any image for full-size modal view")
    print()
    
    print("🎯 API ENDPOINT:")
    print("  GET /artist/{artist_name}/images?limit=4")
    print("  Returns images sorted by rating priority with blur recommendations")
    print()
    
    print("✅ Demo completed! Start the web app to see the visual interface.")

if __name__ == "__main__":
    demo_blur_and_rating_features()
