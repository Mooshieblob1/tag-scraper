#!/usr/bin/env python3
"""
Update existing artists in the database with post counts
"""

from scraper import DanbooruArtistScraper
import sqlite3
from tqdm import tqdm

def update_post_counts():
    """Update post counts for all existing artists in the database"""
    print("🔄 Updating Post Counts for Existing Artists")
    print("=" * 60)
    
    # Initialize scraper
    scraper = DanbooruArtistScraper()
    
    if not scraper.authenticated:
        print("❌ No API authentication found - post counts cannot be updated")
        print("   Please add your credentials to .env file:")
        print("   DANBOORU_USERNAME=your_username")
        print("   DANBOORU_API_KEY=your_api_key")
        return
    
    print(f"✅ Authenticated as: {scraper.username}")
    
    # Get all artists with 0 post count
    conn = sqlite3.connect(scraper.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM artists WHERE post_count = 0")
    total_zero_count = cursor.fetchone()[0]
    
    if total_zero_count == 0:
        print("✅ All artists already have post counts!")
        conn.close()
        return
    
    print(f"📊 Found {total_zero_count} artists with post_count = 0")
    
    # Get artists to update
    cursor.execute("SELECT id, name FROM artists WHERE post_count = 0 ORDER BY name LIMIT 100")
    artists_to_update = cursor.fetchall()
    
    print(f"🎯 Updating first {len(artists_to_update)} artists...")
    print("   (This will respect rate limiting - about 1 update every 0.15 seconds)")
    
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
    artists_with_counts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM artists")
    total_artists = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Update completed!")
    print(f"   Updated: {updated_count} artists")
    print(f"   With post counts: {artists_with_counts}/{total_artists}")
    print(f"   Remaining with 0: {total_artists - artists_with_counts}")

def update_all_incrementally():
    """Update all artists incrementally in batches"""
    print("🔄 Incremental Post Count Update")
    print("=" * 40)
    
    scraper = DanbooruArtistScraper()
    
    if not scraper.authenticated:
        print("❌ Authentication required")
        return
    
    batch_size = 50
    total_updated = 0
    
    while True:
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        
        # Get next batch
        cursor.execute(
            "SELECT id, name FROM artists WHERE post_count = 0 ORDER BY name LIMIT ?",
            (batch_size,)
        )
        batch = cursor.fetchall()
        
        if not batch:
            print(f"✅ All artists updated! Total: {total_updated}")
            conn.close()
            break
        
        print(f"📦 Updating batch of {len(batch)} artists...")
        
        for artist_id, artist_name in batch:
            try:
                post_count = scraper.get_artist_post_count(artist_name)
                cursor.execute(
                    "UPDATE artists SET post_count = ? WHERE id = ?",
                    (post_count, artist_id)
                )
                total_updated += 1
                print(f"  ✅ {artist_name}: {post_count} posts")
                
            except Exception as e:
                print(f"  ❌ {artist_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"📊 Batch complete. Total updated: {total_updated}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        update_all_incrementally()
    else:
        update_post_counts()
        print("\n💡 To update ALL artists, run: python update_post_counts.py --all")
