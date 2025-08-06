import requests
import json
import time
import sqlite3
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class DanbooruArtistScraper:
    def __init__(self, db_path: str = "artists.db", username: str = None):
        self.base_url = "https://danbooru.donmai.us/artists.json"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DanbooruArtistScraper/1.0 (Contact: yourcontact@example.com)'
        })
        
        # Setup logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load API credentials from environment  
        self.api_key = os.getenv('DANBOORU_API_KEY')
        self.username = username or os.getenv('DANBOORU_USERNAME')
        
        if self.api_key and self.username:
            # Setup HTTP Basic Authentication
            self.session.auth = (self.username, self.api_key)
            self.logger.info(f"API authentication configured for user: {self.username}")
            self.authenticated = True
        elif self.api_key:
            self.logger.warning("API key found but no username provided - authentication may not work")
            self.authenticated = False
        else:
            self.logger.warning("No API credentials found - using public API (limited functionality)")
            self.authenticated = False
        
        self.db_path = db_path
        self.setup_database()
        
        # Enhanced rate limiting and 429 detection
        self.min_request_interval = 0.15  # ~6.7 requests per second to stay safe
        self.original_min_interval = 0.15  # Keep track of original setting
        self.last_request_time = 0
        
        # Advanced 429 rate limit handling
        self.rate_limit_wait_time = 1.0  # Start with 1 second wait
        self.max_rate_limit_wait = 300.0  # Maximum wait time of 5 minutes
        self.consecutive_429_count = 0  # Track consecutive 429 errors
        self.total_429_count = 0  # Track total 429 errors
        self.last_429_time = None  # Track when last 429 occurred
        
        # Rate limit statistics and adaptive behavior
        self.rate_limit_stats = {
            'total_requests': 0,
            'total_429s': 0,
            'avg_response_time': 0,
            'last_reset': datetime.now(),
            'consecutive_successes': 0,
            'adaptive_cooldown_until': None
        }
        
        # Adaptive rate limiting thresholds
        self.adaptive_threshold_429s = 3  # Start adapting after 3 429s
        self.recovery_success_threshold = 10  # Reset after 10 consecutive successes
    
    def setup_database(self):
        """Initialize SQLite database for storing artist data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                post_count INTEGER,
                other_names TEXT,
                group_name TEXT,
                url_string TEXT,
                is_active BOOLEAN,
                created_at TEXT,
                updated_at TEXT,
                is_banned BOOLEAN,
                is_deleted BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def ensure_rate_limit(self):
        """Enhanced rate limiting with adaptive behavior based on 429 responses"""
        current_time = time.time()
        
        # Check if we're in an adaptive cooldown period
        if (self.rate_limit_stats['adaptive_cooldown_until'] and 
            datetime.now() < self.rate_limit_stats['adaptive_cooldown_until']):
            remaining_cooldown = (self.rate_limit_stats['adaptive_cooldown_until'] - datetime.now()).total_seconds()
            if remaining_cooldown > 0:
                self.logger.info(f"⏸️  In adaptive cooldown for {remaining_cooldown:.1f} more seconds")
                time.sleep(min(remaining_cooldown, 5))  # Sleep in chunks of max 5 seconds
                return
        
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds (current rate: {1/self.min_request_interval:.1f} req/sec)")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def handle_rate_limit_response(self, response: requests.Response, attempt: int) -> bool:
        """
        Enhanced 429 handling with intelligent backoff and adaptive rate limiting
        Returns True if request should be retried, False otherwise
        """
        if response.status_code == 429:
            self.total_429_count += 1
            self.consecutive_429_count += 1
            self.last_429_time = datetime.now()
            self.rate_limit_stats['total_429s'] += 1
            self.rate_limit_stats['consecutive_successes'] = 0  # Reset success counter
            
            # Log detailed 429 information
            self.logger.warning(f"🚫 Rate limited (429) - Attempt {attempt + 1}")
            self.logger.info(f"📊 429 Stats: Total={self.total_429_count}, Consecutive={self.consecutive_429_count}")
            
            # Check for Retry-After header (RFC compliance)
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                try:
                    wait_time = float(retry_after)
                    self.logger.info(f"🕐 Server requested wait of {wait_time} seconds (Retry-After header)")
                except ValueError:
                    # If Retry-After is not a number, fall back to exponential backoff
                    wait_time = self._calculate_backoff_time(attempt)
                    self.logger.warning(f"⚠️  Invalid Retry-After header, using calculated backoff: {wait_time:.1f}s")
            else:
                # Use intelligent exponential backoff
                wait_time = self._calculate_backoff_time(attempt)
                self.logger.info(f"📈 Using exponential backoff: {wait_time:.1f} seconds")
            
            # Cap wait time to reasonable maximum
            wait_time = min(wait_time, self.max_rate_limit_wait)
            
            # Apply adaptive rate limiting if we're getting too many 429s
            if self.consecutive_429_count >= self.adaptive_threshold_429s:
                self._apply_adaptive_rate_limiting()
            
            self.logger.info(f"⏳ Waiting {wait_time:.1f} seconds before retry...")
            
            # Show progress for long waits
            if wait_time > 10:
                self._show_wait_progress(wait_time)
            else:
                time.sleep(wait_time)
            
            return True  # Retry the request
        
        # Handle successful responses
        if response.status_code == 200:
            self.consecutive_429_count = 0  # Reset consecutive 429 counter
            self.rate_limit_stats['consecutive_successes'] += 1
            
            # Gradually recover rate limiting after consecutive successes
            if self.rate_limit_stats['consecutive_successes'] >= self.recovery_success_threshold:
                self._gradually_recover_rate_limiting()
        
        return False  # Don't retry for non-429 errors
    
    def _calculate_backoff_time(self, attempt: int) -> float:
        """Calculate intelligent exponential backoff time"""
        # Base backoff with jitter
        base_backoff = self.rate_limit_wait_time * (2 ** attempt)
        
        # Add factor based on consecutive 429s
        consecutive_factor = 1 + (self.consecutive_429_count * 0.5)
        
        # Add some randomization to prevent thundering herd
        import random
        jitter = random.uniform(0.8, 1.2)
        
        return base_backoff * consecutive_factor * jitter
    
    def _apply_adaptive_rate_limiting(self):
        """Apply more conservative rate limiting when getting many 429s"""
        # Increase minimum request interval significantly
        old_interval = self.min_request_interval
        self.min_request_interval = min(self.min_request_interval * 2, 2.0)  # Cap at 0.5 req/sec
        
        # Set adaptive cooldown period
        cooldown_minutes = min(5 + self.consecutive_429_count, 30)  # 5-30 minutes based on consecutive 429s
        self.rate_limit_stats['adaptive_cooldown_until'] = datetime.now() + timedelta(minutes=cooldown_minutes)
        
        self.logger.warning(f"🔄 Adaptive rate limiting activated!")
        self.logger.info(f"   Rate: {1/old_interval:.1f} → {1/self.min_request_interval:.1f} req/sec")
        self.logger.info(f"   Cooldown: {cooldown_minutes} minutes")
        
        # Also increase base wait time for future 429s
        self.rate_limit_wait_time = min(self.rate_limit_wait_time * 1.5, 30.0)
    
    def _gradually_recover_rate_limiting(self):
        """Gradually recover rate limiting after consecutive successes"""
        if self.min_request_interval > self.original_min_interval:
            old_rate = 1/self.min_request_interval
            self.min_request_interval = max(self.min_request_interval * 0.9, self.original_min_interval)
            new_rate = 1/self.min_request_interval
            
            self.logger.info(f"🟢 Rate limiting recovery: {old_rate:.1f} → {new_rate:.1f} req/sec")
            
            # Reset success counter
            self.rate_limit_stats['consecutive_successes'] = 0
            
            # Gradually decrease base wait time
            self.rate_limit_wait_time = max(self.rate_limit_wait_time * 0.9, 1.0)
    
    def _show_wait_progress(self, wait_time: float):
        """Show progress bar for long waits"""
        steps = int(wait_time)
        if steps > 60:  # For very long waits, show in chunks
            chunk_size = max(1, steps // 60)
            steps = steps // chunk_size
            actual_sleep = chunk_size
        else:
            actual_sleep = 1
        
        with tqdm(total=steps, desc="⏳ Waiting for rate limit", unit="s") as pbar:
            for _ in range(steps):
                time.sleep(actual_sleep)
                pbar.update(1)
    
    def get_rate_limit_status(self) -> Dict:
        """Get detailed rate limiting status for monitoring"""
        now = datetime.now()
        return {
            'current_rate_limit': f"{1/self.min_request_interval:.1f} req/sec",
            'original_rate_limit': f"{1/self.original_min_interval:.1f} req/sec",
            'is_rate_limited': self.min_request_interval > self.original_min_interval,
            'total_requests': self.rate_limit_stats['total_requests'],
            'total_429s': self.total_429_count,
            'consecutive_429s': self.consecutive_429_count,
            'consecutive_successes': self.rate_limit_stats['consecutive_successes'],
            'last_429_time': self.last_429_time.isoformat() if self.last_429_time else None,
            'adaptive_cooldown_active': (
                self.rate_limit_stats['adaptive_cooldown_until'] and 
                now < self.rate_limit_stats['adaptive_cooldown_until']
            ),
            'adaptive_cooldown_remaining': (
                (self.rate_limit_stats['adaptive_cooldown_until'] - now).total_seconds()
                if self.rate_limit_stats['adaptive_cooldown_until'] and now < self.rate_limit_stats['adaptive_cooldown_until']
                else 0
            ),
            'current_wait_time': self.rate_limit_wait_time,
            'max_wait_time': self.max_rate_limit_wait,
            'health_status': self._get_health_status()
        }
    
    def _get_health_status(self) -> str:
        """Determine overall health status of rate limiting"""
        if self.consecutive_429_count >= 5:
            return "critical"
        elif self.consecutive_429_count >= 3:
            return "warning"
        elif self.total_429_count > 0 and self.rate_limit_stats['consecutive_successes'] < 5:
            return "recovering"
        else:
            return "healthy"

    def get_page(self, page_id: str, retries: int = 5) -> Optional[List[Dict]]:
        """Fetch a single page of artists using JSON API with enhanced 429 detection"""
        self.ensure_rate_limit()
        
        # Use maximum limit of 1000 as per API documentation
        limit = 1000
        url = f"{self.base_url}?page={page_id}&limit={limit}"
        
        for attempt in range(retries):
            try:
                self.logger.info(f"🌐 Fetching page {page_id} (attempt {attempt + 1}/{retries})")
                
                # Track request statistics
                self.rate_limit_stats['total_requests'] += 1
                request_start_time = time.time()
                
                response = self.session.get(url, timeout=30)
                
                # Track response time for monitoring
                response_time = time.time() - request_start_time
                if self.rate_limit_stats['avg_response_time'] == 0:
                    self.rate_limit_stats['avg_response_time'] = response_time
                else:
                    # Running average
                    self.rate_limit_stats['avg_response_time'] = (
                        self.rate_limit_stats['avg_response_time'] * 0.9 + response_time * 0.1
                    )
                
                # Enhanced 429 handling
                if self.handle_rate_limit_response(response, attempt):
                    self.logger.info(f"🔄 Retrying page {page_id} after rate limit handling...")
                    continue  # Retry the request
                
                # Check for other HTTP errors
                if response.status_code != 200:
                    response.raise_for_status()
                
                artists_data = response.json()
                
                if not artists_data:
                    self.logger.info(f"📄 Page {page_id} returned empty results - reached end")
                    return []
                
                self.logger.info(f"✅ Successfully fetched {len(artists_data)} artists from page {page_id}")
                self.logger.debug(f"📊 Response time: {response_time:.2f}s, Avg: {self.rate_limit_stats['avg_response_time']:.2f}s")
                
                return artists_data
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"⏰ Request timeout for page {page_id} (attempt {attempt + 1})")
                if attempt < retries - 1:
                    wait_time = min(2 ** attempt, 30)  # Cap at 30 seconds
                    self.logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                
            except requests.exceptions.RequestException as e:
                # Handle specific HTTP errors
                if hasattr(e, 'response') and e.response:
                    if e.response.status_code == 429:
                        # This should be handled by handle_rate_limit_response, but double-check
                        self.logger.warning(f"🚫 429 error not caught by handler: {e}")
                        if self.handle_rate_limit_response(e.response, attempt):
                            continue
                    elif e.response.status_code in [502, 503, 504]:
                        # Server errors - retry with backoff
                        self.logger.warning(f"🔧 Server error {e.response.status_code} for page {page_id}")
                        if attempt < retries - 1:
                            wait_time = min(5 * (2 ** attempt), 60)  # 5, 10, 20, 40, 60 seconds
                            self.logger.info(f"⏳ Waiting {wait_time} seconds for server recovery...")
                            time.sleep(wait_time)
                            continue
                
                self.logger.warning(f"⚠️  Request failed for page {page_id} (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"❌ Failed to fetch page {page_id} after {retries} attempts")
                    return None
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"📄 Failed to parse JSON response for page {page_id}: {e}")
                if attempt < retries - 1:
                    self.logger.info(f"🔄 Retrying due to JSON decode error...")
                    time.sleep(1)
                    continue
                return None
            
            except Exception as e:
                self.logger.error(f"💥 Unexpected error for page {page_id}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        self.logger.error(f"❌ All retry attempts exhausted for page {page_id}")
        return None
    
    def parse_artist_data(self, artist_json: Dict) -> Optional[Dict]:
        """Parse artist data from JSON response"""
        try:
            # Handle missing post_count field gracefully
            post_count = artist_json.get('post_count', 0)
            
            # If post_count is not available, we could potentially fetch it separately
            # but for now, we'll default to 0
            if post_count is None:
                post_count = 0
            
            return {
                'id': artist_json.get('id'),
                'name': artist_json.get('name', '').strip(),
                'post_count': post_count,
                'other_names': ', '.join(artist_json.get('other_names', [])) if artist_json.get('other_names') else "",
                'group_name': artist_json.get('group_name', '').strip() if artist_json.get('group_name') else "",
                'url_string': artist_json.get('url_string', '').strip() if artist_json.get('url_string') else "",
                'is_active': artist_json.get('is_active', True),
                'created_at': artist_json.get('created_at', ''),
                'updated_at': artist_json.get('updated_at', ''),
                'is_banned': artist_json.get('is_banned', False),
                'is_deleted': artist_json.get('is_deleted', False)
            }
        except Exception as e:
            self.logger.error(f"Error parsing artist data: {e}")
            self.logger.debug(f"Problematic data: {artist_json}")
            return None
    
    def scrape_page(self, page_id: str) -> List[Dict]:
        """Scrape artists from a single page using JSON API"""
        artists_json = self.get_page(page_id)
        if not artists_json:
            return []
        
        artists = []
        for artist_json in artists_json:
            artist_data = self.parse_artist_data(artist_json)
            if artist_data:
                artists.append(artist_data)
        
        return artists
    
    def save_artists(self, artists: List[Dict]):
        """Save artists to database"""
        if not artists:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for artist in artists:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO artists 
                    (id, name, post_count, other_names, group_name, url_string, is_active, created_at, updated_at, is_banned, is_deleted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    artist['id'],
                    artist['name'],
                    artist['post_count'],
                    artist['other_names'],
                    artist['group_name'],
                    artist['url_string'],
                    artist['is_active'],
                    artist['created_at'],
                    artist['updated_at'],
                    artist['is_banned'],
                    artist['is_deleted']
                ))
            except sqlite3.Error as e:
                self.logger.error(f"Database error saving artist {artist.get('name', 'unknown')}: {e}")
        
        conn.commit()
        conn.close()
    
    def generate_page_id(self, page_num: int) -> str:
        """Generate page ID for the API (a0, a1, a2, etc.)"""
        return f"a{page_num}"
    
    def scrape_all_pages(self, start_page: int = 0, max_pages: int = None):
        """Scrape all pages starting from start_page until no more artists are found"""
        self.logger.info(f"🚀 Starting comprehensive scrape from page {start_page}")
        
        page_num = start_page
        total_artists_scraped = 0
        consecutive_empty_pages = 0
        max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
        
        # Reset rate limiting stats at start
        self.rate_limit_stats['last_reset'] = datetime.now()
        
        with tqdm(desc="Scraping artists", unit="artists") as pbar:
            while True:
                if max_pages and page_num >= start_page + max_pages:
                    self.logger.info(f"🏁 Reached maximum page limit ({max_pages})")
                    break
                
                page_id = self.generate_page_id(page_num)
                
                # Show rate limiting status every 10 pages
                if page_num % 10 == 0 and page_num > start_page:
                    status = self.get_rate_limit_status()
                    self.logger.info(f"📊 Rate limit status: {status['health_status']} - {status['current_rate_limit']}")
                    if status['total_429s'] > 0:
                        self.logger.info(f"   429 Stats: {status['total_429s']} total, {status['consecutive_429s']} consecutive")
                
                self.logger.info(f"📄 Processing page {page_id} (page number {page_num})")
                
                artists = self.scrape_page(page_id)
                
                if not artists:
                    consecutive_empty_pages += 1
                    self.logger.warning(f"📭 Page {page_id} returned no artists (consecutive empty: {consecutive_empty_pages})")
                    
                    if consecutive_empty_pages >= max_consecutive_empty:
                        self.logger.info(f"🛑 Stopping after {consecutive_empty_pages} consecutive empty pages")
                        break
                    
                    page_num += 1
                    continue
                
                # Reset consecutive empty counter if we found artists
                consecutive_empty_pages = 0
                
                self.save_artists(artists)
                total_artists_scraped += len(artists)
                pbar.update(len(artists))
                pbar.set_description(f"Scraped {total_artists_scraped} artists (page {page_id})")
                
                self.logger.info(f"💾 Saved {len(artists)} artists from page {page_id} (total: {total_artists_scraped})")
                
                # Check if we need to slow down due to rate limiting issues
                status = self.get_rate_limit_status()
                if status['health_status'] in ['warning', 'critical']:
                    self.logger.warning(f"⚠️  Rate limiting health: {status['health_status']} - being extra cautious")
                    time.sleep(2)  # Extra delay for unhealthy rate limiting
                
                page_num += 1
        
        # Final statistics
        final_status = self.get_rate_limit_status()
        self.logger.info(f"🏁 Scraping completed. Total artists scraped: {total_artists_scraped}")
        self.logger.info(f"📊 Final rate limit stats:")
        self.logger.info(f"   Total requests: {final_status['total_requests']}")
        self.logger.info(f"   Total 429s: {final_status['total_429s']}")
        self.logger.info(f"   Final rate: {final_status['current_rate_limit']}")
        self.logger.info(f"   Health status: {final_status['health_status']}")
        
        return total_artists_scraped
    
    def get_artists_by_criteria(self, 
                              name_starts_with: str = None,
                              min_post_count: int = None,
                              max_post_count: int = None,
                              name_contains: str = None,
                              limit: int = 100) -> List[Dict]:
        """Query artists by various criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM artists WHERE 1=1"
        params = []
        
        if name_starts_with:
            query += " AND name LIKE ?"
            params.append(f"{name_starts_with}%")
        
        if name_contains:
            query += " AND (name LIKE ? OR other_names LIKE ?)"
            params.extend([f"%{name_contains}%", f"%{name_contains}%"])
        
        if min_post_count is not None:
            query += " AND post_count >= ?"
            params.append(min_post_count)
        
        if max_post_count is not None:
            query += " AND post_count <= ?"
            params.append(max_post_count)
        
        query += " ORDER BY post_count DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to dictionaries
        columns = [description[0] for description in cursor.description]
        artists = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return artists
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM artists")
        total_artists = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(post_count), MAX(post_count), MIN(post_count) FROM artists")
        avg_posts, max_posts, min_posts = cursor.fetchone()
        
        cursor.execute("SELECT name, post_count FROM artists ORDER BY post_count DESC LIMIT 10")
        top_artists = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_artists': total_artists,
            'avg_posts': avg_posts,
            'max_posts': max_posts,
            'min_posts': min_posts,
            'top_artists': top_artists
        }

if __name__ == "__main__":
    # Create scraper instance
    scraper = DanbooruArtistScraper()
    
    print("🎨 Danbooru Artist Scraper with JSON API")
    print("=" * 50)
    
    # Check authentication status
    if scraper.authenticated:
        print(f"✅ Authenticated as: {scraper.username}")
        print("📊 Using full API access (1000 artists per page)")
    else:
        print("⚠️  No authentication - using public API")
        print("📊 Limited to public access")
    
    print(f"⏱️  Rate limit: {1/scraper.min_request_interval:.1f} requests per second")
    print("")
    
    # Ask user what they want to do
    print("Choose an option:")
    print("1. Test scrape (first 3 pages)")
    print("2. Full scrape (all artists until exhausted)")
    print("3. Custom scrape (specify page range)")
    print("4. Show database stats only")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🧪 Starting test scrape (first 3 pages)...")
        total_scraped = scraper.scrape_all_pages(start_page=0, max_pages=3)
        print(f"\n✅ Test completed! Scraped {total_scraped} artists")
        
    elif choice == "2":
        confirm = input("\n⚠️  This will scrape ALL artists and may take several hours. Continue? (y/N): ").strip().lower()
        if confirm == 'y':
            print("\n🚀 Starting full scrape...")
            total_scraped = scraper.scrape_all_pages(start_page=0)
            print(f"\n🎉 Full scrape completed! Total artists: {total_scraped}")
        else:
            print("❌ Cancelled")
            
    elif choice == "3":
        try:
            start = int(input("Start page number (0-based): ").strip())
            max_pages = int(input("Maximum pages to scrape: ").strip())
            print(f"\n🎯 Starting custom scrape from page {start} for {max_pages} pages...")
            total_scraped = scraper.scrape_all_pages(start_page=start, max_pages=max_pages)
            print(f"\n✅ Custom scrape completed! Scraped {total_scraped} artists")
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
            
    elif choice == "4":
        pass  # Just show stats below
    else:
        print("❌ Invalid choice")
    
    # Show database statistics
    print("\n📊 Database Statistics:")
    print("-" * 30)
    try:
        stats = scraper.get_database_stats()
        print(f"Total artists: {stats['total_artists']:,}")
        if stats['total_artists'] > 0:
            print(f"Average posts: {stats['avg_posts']:.1f}")
            print(f"Most posts: {stats['max_posts']:,}")
            print(f"Least posts: {stats['min_posts']:,}")
            
            print(f"\n🏆 Top 10 Artists by Post Count:")
            for i, (name, count) in enumerate(stats['top_artists'], 1):
                print(f"  {i:2d}. {name:<30} {count:,} posts")
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    # Show example searches
    if scraper.get_database_stats()['total_artists'] > 0:
        print(f"\n🔍 Example Searches:")
        print("-" * 20)
        
        # Artists starting with 'A'
        artists_a = scraper.get_artists_by_criteria(name_starts_with="A", limit=5)
        if artists_a:
            print("Artists starting with 'A':")
            for artist in artists_a:
                print(f"  • {artist['name']} - {artist['post_count']:,} posts")
        
        # Popular artists (300+ posts)
        popular_artists = scraper.get_artists_by_criteria(min_post_count=300, limit=5)
        if popular_artists:
            print(f"\nPopular artists (300+ posts):")
            for artist in popular_artists:
                print(f"  • {artist['name']} - {artist['post_count']:,} posts")
