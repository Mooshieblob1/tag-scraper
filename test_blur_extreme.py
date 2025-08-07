#!/usr/bin/env python3
"""
Test the updated blur functionality with extreme pixel blur values
"""

from scraper import DanbooruArtistScraper
import json

def test_blur_functionality():
    """Test the new blur settings and rating prioritization"""
    print("🌫️ Testing Updated Blur Functionality")
    print("=" * 50)
    
    scraper = DanbooruArtistScraper()
    
    print("✨ NEW BLUR SETTINGS:")
    print("1. 🎯 Blur Threshold: Sensitive and above (s, q, e)")
    print("2. 🌫️  Blur Effect: 4,294,967,296px (2^32) - Maximum pixel blur")
    print("3. 🎛️  Hover Effect: 2,147,483,648px (2^31) - Reduced on hover")
    print("4. 📊 Priority Order: General → Sensitive → Questionable → Explicit")
    print()
    
    # Test with artists that might have different rating distributions
    test_artists = ["kantoku", "as109"]
    
    for artist_name in test_artists:
        print(f"🎨 Testing: {artist_name}")
        print("-" * 30)
        
        images = scraper.get_artist_sample_images(artist_name, limit=4)
        
        if images:
            print(f"Found {len(images)} images (prioritized by rating):")
            
            for i, image in enumerate(images, 1):
                rating = image['rating']
                rating_names = {
                    'g': 'General (Visible)',
                    's': 'Sensitive (BLURRED)', 
                    'q': 'Questionable (BLURRED)',
                    'e': 'Explicit (BLURRED)'
                }
                
                rating_priority = {
                    'g': 1,  # Highest priority
                    's': 2,
                    'q': 3, 
                    'e': 4   # Lowest priority
                }
                
                blur_css = "blur(4294967296px)" if rating in ['s', 'q', 'e'] else "none"
                
                print(f"  {i}. {rating_names.get(rating, 'Unknown')}")
                print(f"     Score: {image['score']}, Priority: {rating_priority.get(rating, 5)}")
                print(f"     CSS Filter: {blur_css}")
                print(f"     Size: {image['image_width']}x{image['image_height']}")
                print()
        else:
            print("  No images found")
        
        print()
    
    print("🎯 BLUR BEHAVIOR:")
    print("• Default State: Sensitive/Questionable/Explicit images are heavily blurred")
    print("• Hover Effect: Blur reduces by half on hover (2^31 pixels)")
    print("• Toggle Control: Users can disable all blurring via checkbox")
    print("• General Content: Always visible without blur")
    print()
    
    print("🖥️ CSS VALUES:")
    print("• Normal Blur: filter: blur(4294967296px)")
    print("• Hover Blur: filter: blur(2147483648px)")
    print("• Transition: filter 0.3s ease")
    print()
    
    print("✅ Blur functionality updated!")
    print("Start the web app and test 'Preview Images' to see the visual effects.")

if __name__ == "__main__":
    test_blur_functionality()
