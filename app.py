from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import sqlite3
import json
import threading
import os
from scraper import DanbooruArtistScraper

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
    start_page = int(data.get('start_page', 0))
    max_pages = data.get('max_pages')
    fetch_post_counts = data.get('fetch_post_counts', True)  # Default to True for compatibility
    
    if max_pages:
        max_pages = int(max_pages)
        end_page = start_page + max_pages - 1
    else:
        max_pages = None
        end_page = None
    
    # Validate page range
    if start_page < 0:
        return jsonify({
            'success': False,
            'error': 'start_page must be >= 0'
        }), 400
    
    if max_pages is not None and max_pages <= 0:
        return jsonify({
            'success': False,
            'error': 'max_pages must be > 0'
        }), 400
    
    # Start scraping in background thread
    scraping_status.update({
        'is_running': True,
        'current_page': start_page,
        'total_pages': max_pages if max_pages else 'Unknown (scraping until exhausted)',
        'progress': 0,
        'message': f'Starting scrape from page a{start_page}' + (f' (max {max_pages} pages)' if max_pages else ' (until exhausted)'),
        'fetch_post_counts': fetch_post_counts
    })
    
    def scrape_background():
        global scraping_status
        try:
            # Use the enhanced scrape_all_pages method
            total_artists_scraped = scraper.scrape_all_pages(
                start_page=start_page,
                max_pages=max_pages,
                fetch_post_counts=fetch_post_counts
            )
            
            scraping_status.update({
                'is_running': False,
                'progress': 100,
                'message': f'Scraping completed successfully. Total artists: {total_artists_scraped}' + 
                          (' (with post counts)' if fetch_post_counts else ' (without post counts)'),
                'total_scraped': total_artists_scraped
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
    cursor.execute("SELECT * FROM artists ORDER BY name")
    results = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    artists = [dict(zip(columns, row)) for row in results]
    
    conn.close()
    
    return jsonify({
        'artists': artists,
        'total_count': len(artists)
    })

@app.route('/export/csv')
def export_csv():
    """Export all artists data as CSV file"""
    try:
        filename = scraper.export_to_csv()
        return send_file(filename, as_attachment=True, download_name="danbooru_artists.csv")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/artist/<artist_name>/images')
def get_artist_images(artist_name):
    """Get sample images for an artist"""
    try:
        limit = min(int(request.args.get('limit', 4)), 10)  # Cap at 10 images
        images = scraper.get_artist_sample_images(artist_name, limit=limit)
        return jsonify({
            'success': True,
            'artist_name': artist_name,
            'images': images,
            'count': len(images)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
