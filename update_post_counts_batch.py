#!/usr/bin/env python3
"""
Update post counts for existing artists in small batches
"""

from scraper import DanbooruArtistScraper
import sqlite3
from tqdm import tqdm
import time

def update_post_counts_incrementally():
    """Update post counts for existing artists in manageable batches"""
    print("🔄 Incremental Post Count Update")
    print("=" * 50)
    
    # Initialize scraper
    scraper = DanbooruArtistScraper()
    
    if not scraper.authenticated:
        print("❌ API authentication required for post counts")
        print("   Add your credentials to .env file:")
        print("   DANBOORU_USERNAME=your_username")
        print("   DANBOORU_API_KEY=your_api_key")
        return
    
    print(f"✅ Authenticated as: {scraper.username}")
    
    # Get stats
    conn = sqlite3.connect(scraper.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM artists")
    total_artists = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM artists WHERE post_count = 0")
    zero_count_artists = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM artists WHERE post_count > 0")
    with_counts = cursor.fetchone()[0]
    
    print(f"📊 Database stats:")
    print(f"   Total artists: {total_artists}")
    print(f"   With post counts: {with_counts}")
    print(f"   Need updating: {zero_count_artists}")
    
    if zero_count_artists == 0:
        print("✅ All artists already have post counts!")
        conn.close()
        return
    
    # Ask user how many to update
    try:
        batch_size = int(input(f"\nHow many artists to update? (1-{min(zero_count_artists, 100)}): "))
        batch_size = max(1, min(batch_size, 100))
    except ValueError:
        batch_size = 10
        print(f"Using default batch size: {batch_size}")
    
    print(f"\n🎯 Updating {batch_size} artists...")
    print(f"   Estimated time: {batch_size * 0.4:.1f} seconds")
    
    # Get artists to update
    cursor.execute(
        "SELECT id, name FROM artists WHERE post_count = 0 ORDER BY name LIMIT ?",
        (batch_size,)
    )
    artists_to_update = cursor.fetchall()
    
    updated_count = 0
    with tqdm(total=len(artists_to_update), desc="Updating post counts") as pbar:
        for artist_id, artist_name in artists_to_update:
            try:
                # Get the post count
                post_count = scraper.get_artist_post_count(artist_name)
                
                # Update the database
                cursor.execute(
                    "UPDATE artists SET post_count = ? WHERE id = ?",
                    (post_count, artist_id)
                )
                
                updated_count += 1
                pbar.set_description(f"Updated {artist_name}: {post_count} posts")
                pbar.update(1)
                
            except Exception as e:
                print(f"\n❌ Error updating {artist_name}: {e}")
                continue
    
    # Commit changes
    conn.commit()
    
    # Show updated stats
    cursor.execute("SELECT COUNT(*) FROM artists WHERE post_count > 0")
    new_with_counts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM artists WHERE post_count = 0")
    remaining_zero = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Update completed!")
    print(f"   Updated: {updated_count} artists")
    print(f"   Now with post counts: {new_with_counts}/{total_artists}")
    print(f"   Still need updating: {remaining_zero}")
    
    if remaining_zero > 0:
        print(f"\n💡 To continue updating, run this script again")

if __name__ == "__main__":
    update_post_counts_incrementally()
