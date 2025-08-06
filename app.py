from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from scraper import DanbooruArtistScraper
import threading
import os

app = Flask(__name__)

# Initialize scraper with proper authentication
scraper = DanbooruArtistScraper()

# Global variable to track scraping progress
scraping_status = {
    'is_running': False,
    'current_page': 0,
    'total_pages': 0,
    'progress': 0,
    'message': 'Ready to start scraping',
    'total_scraped': 0
}

@app.route('/')
def index():
    """Main page with search interface"""
    stats = scraper.get_database_stats()
    auth_status = {
        'authenticated': scraper.authenticated,
        'username': getattr(scraper, 'username', None),
        'rate_limit_status': scraper.get_rate_limit_status()
    }
    return render_template('index.html', stats=stats, auth=auth_status)

@app.route('/search', methods=['POST'])
def search_artists():
    """Search artists based on criteria"""
    data = request.get_json()
    
    # Extract search parameters
    name_starts_with = data.get('name_starts_with', '').strip() or None
    name_contains = data.get('name_contains', '').strip() or None
    min_post_count = data.get('min_post_count')
    max_post_count = data.get('max_post_count')
    limit = min(int(data.get('limit', 100)), 1000)  # Cap at 1000 results
    
    # Convert empty strings to None for numeric fields
    if min_post_count == '':
        min_post_count = None
    else:
        min_post_count = int(min_post_count) if min_post_count else None
    
    if max_post_count == '':
        max_post_count = None
    else:
        max_post_count = int(max_post_count) if max_post_count else None
    
    try:
        artists = scraper.get_artists_by_criteria(
            name_starts_with=name_starts_with,
            name_contains=name_contains,
            min_post_count=min_post_count,
            max_post_count=max_post_count,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'artists': artists,
            'count': len(artists)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/scrape', methods=['POST'])
def start_scraping():
    """Start the scraping process in a background thread"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'Scraping is already in progress'
        }), 400
    
    data = request.get_json()
    start_page = int(data.get('start_page', 0))  # Changed default to 0
    end_page = int(data.get('end_page', 100))     # More reasonable default
    
    # Validate page range
    if start_page < 0 or end_page < start_page:
        return jsonify({
            'success': False,
            'error': 'Invalid page range. start_page must be >= 0 and start_page <= end_page'
        }), 400
    
    # Start scraping in background thread
    scraping_status.update({
        'is_running': True,
        'current_page': start_page,
        'total_pages': end_page - start_page + 1,
        'progress': 0,
        'message': f'Starting scrape from page a{start_page} to a{end_page}'
    })
    
    def scrape_background():
        global scraping_status
        try:
            # Use the new scrape_all_pages method with max_pages
            max_pages = end_page - start_page + 1
            
            page_num = start_page
            total_artists_scraped = 0
            
            while page_num <= end_page and scraping_status['is_running']:
                page_id = scraper.generate_page_id(page_num)
                
                scraping_status['current_page'] = page_num
                scraping_status['progress'] = ((page_num - start_page + 1) / scraping_status['total_pages']) * 100
                scraping_status['message'] = f'Scraping page {page_id} ({page_num}/{end_page})'
                
                artists = scraper.scrape_page(page_id)
                if artists:
                    scraper.save_artists(artists)
                    total_artists_scraped += len(artists)
                else:
                    # If no artists found, we might have reached the end
                    scraping_status['message'] = f'No artists found on page {page_id} - might have reached end'
                
                page_num += 1
                
                # Rate limiting is handled in the scraper
            
            scraping_status.update({
                'is_running': False,
                'progress': 100,
                'message': f'Scraping completed successfully. Total artists: {total_artists_scraped}'
            })
        
        except Exception as e:
            scraping_status.update({
                'is_running': False,
                'message': f'Scraping failed: {str(e)}'
            })
    
    thread = threading.Thread(target=scrape_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Scraping started'
    })

@app.route('/scrape/status')
def scraping_status_endpoint():
    """Get current scraping status"""
    global scraping_status
    return jsonify(scraping_status)

@app.route('/scrape/stop', methods=['POST'])
def stop_scraping():
    """Stop the scraping process"""
    global scraping_status
    scraping_status['is_running'] = False
    scraping_status['message'] = 'Scraping stopped by user'
    return jsonify({'success': True, 'message': 'Scraping stopped'})

@app.route('/stats')
def get_stats():
    """Get database statistics"""
    stats = scraper.get_database_stats()
    return jsonify(stats)

@app.route('/rate-limit-status')
def get_rate_limit_status():
    """Get current rate limiting status with enhanced 429 detection info"""
    return jsonify(scraper.get_rate_limit_status())

@app.route('/export')
def export_data():
    """Export all artists data as JSON"""
    conn = sqlite3.connect(scraper.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artists ORDER BY post_count DESC")
    results = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    artists = [dict(zip(columns, row)) for row in results]
    
    conn.close()
    
    return jsonify({
        'artists': artists,
        'total_count': len(artists)
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
