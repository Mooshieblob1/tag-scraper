# 🎨 Danbooru Artist Scraper

A comprehensive web application for scraping and searching artist data from Danbooru. Features a modern web interface for easy searching and filtering of artists by various criteria, with advanced 429 rate limit detection and adaptive rate limiting.

## ✨ Features

- **Web-based Interface**: Modern, responsive UI for easy interaction
- **Artist Scraping**: Collect artist data from Danbooru pages 1-1000 (free tier limit)
- **Advanced Search**: Filter artists by:
  - Name (starts with, contains)
  - Post count (minimum/maximum)
  - Multiple criteria combinations
- **Real-time Progress**: Live progress tracking during scraping
- **Enhanced 429 Detection**: Intelligent rate limiting with automatic adaptation
- **Health Monitoring**: Real-time rate limiting status with color-coded health indicators
- **Database Storage**: SQLite database for efficient data storage and querying
- **Export Functionality**: Export search results as JSON
- **Statistics Dashboard**: View database statistics and top artists

## 🚫 Advanced Rate Limiting

This scraper includes sophisticated 429 (Too Many Requests) detection and adaptive rate limiting:

### � Adaptive Features
- **Automatic 429 Detection**: Detects and handles rate limiting automatically
- **Intelligent Backoff**: Uses exponential backoff with jitter to avoid thundering herd
- **Health Monitoring**: Tracks rate limiting health (🟢 Healthy, 🟡 Warning, 🔴 Critical)
- **Progressive Recovery**: Gradually returns to normal speed after successful requests
- **Cooldown Management**: Implements temporary cooldowns during heavy rate limiting

### 📊 Monitoring Dashboard
- **Real-time Status**: Live rate limiting status updates every 10 seconds
- **429 Error Tracking**: Total and consecutive 429 error counts
- **Adaptive Indicators**: Visual indicators when adaptive rate limiting is active
- **Health Status**: Color-coded health status with detailed information

## �🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Internet connection

### Installation

1. **Clone or download this repository**
2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Set up the project structure

3. **Start the application:**
   ```bash
   source venv/bin/activate
   python app.py
   ```

4. **Open your browser to:** http://localhost:5000

## 📊 How to Use

### 1. Data Collection
- Navigate to the "Data Collection" section
- Set your page range (start with 1-10 for testing)
- Click "Start Scraping" to begin collecting artist data
- Monitor progress with the real-time progress bar
- Watch the rate limiting health status for any issues
- **Note**: Scraping all 1000 pages takes several hours

### 2. Searching Artists
Use the search interface to find artists by:

**Example Searches:**
- **Artists starting with "A"**: Set "Name starts with" to "A"
- **Popular artists**: Set "Minimum posts" to "300"
- **Specific artist**: Set "Name contains" to search for partial matches
- **Range filtering**: Combine minimum and maximum post counts

### 3. Results Management
- View results in an organized grid layout
- See artist names, post counts, and alternative names
- Export results as JSON for external use
- Clear results and start new searches

## 🔧 Technical Details

### Architecture
- **Backend**: Flask web framework
- **Frontend**: Modern HTML/CSS/JavaScript
- **Database**: SQLite for local data storage
- **Scraping**: BeautifulSoup for HTML parsing
- **HTTP Requests**: Requests library with session management

### Database Schema
```sql
CREATE TABLE artists (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    post_count INTEGER,
    other_names TEXT,
    group_name TEXT,
    url_string TEXT,
    is_active BOOLEAN,
    created_at TEXT,
    updated_at TEXT,
    is_banned BOOLEAN
)
```

### API Endpoints
- `GET /`: Main interface
- `POST /search`: Search artists with criteria
- `POST /scrape`: Start scraping process
- `GET /scrape/status`: Get scraping progress
- `POST /scrape/stop`: Stop scraping
- `GET /stats`: Get database statistics
- `GET /export`: Export all data as JSON

## 🛠️ Advanced Usage

### Command Line Scraping
You can also use the scraper directly from Python:

```python
from scraper import DanbooruArtistScraper

# Initialize scraper
scraper = DanbooruArtistScraper()

# Scrape specific pages
scraper.scrape_all_pages(start_page=1, end_page=50)

# Search for artists
artists = scraper.get_artists_by_criteria(
    name_starts_with="A",
    min_post_count=100,
    limit=50
)

# Get statistics
stats = scraper.get_database_stats()
print(f"Total artists: {stats['total_artists']}")
```

### Rate Limiting
The scraper includes advanced rate limiting with 429 detection:
- **Base Rate**: 6.7 requests per second (conservative)
- **429 Detection**: Automatic detection and handling of rate limit responses
- **Exponential Backoff**: Smart retry logic with increasing delays
- **Retry-After Support**: Respects server-provided timing guidance
- **Dynamic Adjustment**: Automatically reduces rate when needed
- **Gradual Recovery**: Returns to optimal rate after successful operations

See `RATE_LIMITING.md` for detailed technical documentation.

### Database Management
The SQLite database (`artists.db`) stores all scraped data:
- **Location**: Same directory as the application
- **Backup**: Copy the `.db` file to backup your data
- **Reset**: Delete the `.db` file to start fresh

## 🚨 Important Notes

### Danbooru API Limits
- **Free tier**: Limited to pages 1-1000
- **Rate limiting**: Built-in delays to respect server resources
- **Content**: Public artist information only

### Performance Considerations
- **Initial scrape**: Can take 2-4 hours for all 1000 pages
- **Memory usage**: Efficient SQLite storage
- **Network**: Requires stable internet connection
- **Updates**: Re-run scraper to get latest data

### Legal and Ethical Use
- Respect Danbooru's terms of service
- Don't overload their servers
- Use data responsibly
- Consider supporting Danbooru if you find the service valuable

## 🧪 Rate Limiting Testing

### Test Tools

**Rate Limit Monitor**: Comprehensive testing of 429 detection
```bash
python rate_limit_monitor.py
```
Options:
- **Quick Test**: Normal rate limiting behavior
- **Aggressive Test**: Trigger 429s to test adaptive behavior
- **Full Test Suite**: Comprehensive testing with recovery monitoring
- **Status Monitor**: Check current rate limiting status

**Enhanced 429 Test**: Simple demonstration script
```bash
python test_enhanced_429.py
```

### Test Reports

The rate limit monitor generates detailed reports:
- `rate_limit_test_report.json`: Comprehensive test results
- `rate_limit_monitor.log`: Detailed logging of test execution

### API Endpoint

Check rate limiting status programmatically:
```bash
curl http://localhost:5000/rate-limit-status
```

Returns comprehensive status including:
- Current rate limit and health status
- 429 error counts and patterns
- Adaptive rate limiting status
- Cooldown information

## 🔧 Troubleshooting

### Common Issues

**"Import could not be resolved" errors:**
- Make sure you've activated the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Scraping fails or stops:**
- Check your internet connection
- Monitor rate limiting health status (🟢🟡🔴)
- If seeing 429s, wait for adaptive recovery
- Restart the scraping from the last successful page
- Some pages might be temporarily unavailable

**Rate limiting issues:**
- Check the rate limiting health status in web interface
- 🔴 Critical status indicates server overload - wait before retrying
- Use the rate limit monitor to diagnose issues: `python rate_limit_monitor.py`
- Review logs for 429 error patterns

**Search returns no results:**
- Ensure you've scraped some data first
- Check your search criteria aren't too restrictive
- Verify the database contains data: check the statistics section

**Web interface not loading:**
- Ensure Flask is running: `python app.py`
- Check the correct URL: http://localhost:5000
- Look for error messages in the terminal

### Performance Optimization

**For faster searching:**
- Use specific criteria to limit result sets
- Consider the result limit setting

**For efficient scraping:**
- Monitor rate limiting health status
- Start with smaller page ranges for testing
- Let adaptive rate limiting handle server load automatically
- Monitor system resources during large scrapes
- Consider running overnight for full database collection

### Rate Limiting Best Practices

**Normal Operation:**
- Monitor the web interface health indicators
- 🟢 Healthy: Normal operation
- 🟡 Warning: Some 429s detected, system adapting
- 🔴 Critical: Multiple 429s, heavily rate limited

**When Issues Occur:**
- Don't restart immediately after 429 errors
- Let the adaptive system recover naturally
- Check server status if persistent issues occur
- Use test tools to diagnose rate limiting problems

## 📁 File Structure

```
tag scraper/
├── app.py                      # Flask web application
├── scraper.py                  # Core scraping functionality with enhanced 429 detection
├── rate_limit_monitor.py       # Rate limiting test and monitoring tool
├── test_enhanced_429.py        # Simple 429 detection test
├── requirements.txt            # Core Python dependencies
├── requirements-dev.txt        # Development dependencies (optional)
├── setup.sh                   # Installation script
├── .gitignore                 # Git ignore file
├── README.md                  # This documentation
├── RATE_LIMIT_GUIDE.md        # Detailed 429 detection documentation
├── IMPLEMENTATION_SUMMARY.md  # Technical implementation details
├── templates/
│   └── index.html             # Web interface template with rate limiting status
├── artists.db                 # SQLite database (created after first run, gitignored)
├── rate_limit_test_report.json # Test reports (created by monitor, gitignored)
└── venv/                      # Virtual environment (gitignored)
```

### Files Excluded from Git

The `.gitignore` file excludes the following:
- **Virtual environments**: `venv/`, `env/`, `.venv`
- **Database files**: `*.db`, `artists.db`
- **Log files**: `*.log`, `rate_limit_monitor.log`
- **Test reports**: `rate_limit_test_report.json`
- **Environment files**: `.env`
- **Python cache**: `__pycache__/`, `*.pyc`
- **IDE files**: `.vscode/`, `.idea/`
- **OS files**: `.DS_Store`, `Thumbs.db`

## 🔧 Development Setup

### For Contributors

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "tag scraper"
   ```

2. **Install dependencies:**
   ```bash
   # Production dependencies
   pip install -r requirements.txt
   
   # Or for development (includes testing tools)
   pip install -r requirements-dev.txt
   ```

3. **Set up environment (optional):**
   ```bash
   # Create .env file for API credentials
   echo "DANBOORU_API_KEY=your_api_key_here" > .env
   echo "DANBOORU_USERNAME=your_username_here" >> .env
   ```

### Git Best Practices

- The database file (`artists.db`) is gitignored - each user maintains their own local data
- Log files and test reports are excluded from version control
- Virtual environments are not tracked
- Environment files with API keys are excluded for security

### Quick Git Setup

```bash
# Initialize repository
git init

# Add all files (respects .gitignore)
git add .

# Initial commit
git commit -m "Initial commit: Danbooru Artist Scraper"

# Add remote and push
git remote add origin <your-repository-url>
git push -u origin main
```

Check what files will be tracked:
```bash
./git_setup_summary.sh
````

## 🔧 Troubleshooting

### Common Issues

**"Import could not be resolved" errors:**
- Make sure you've activated the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Scraping fails or stops:**
- Check your internet connection
- Restart the scraping from the last successful page
- Some pages might be temporarily unavailable

**Search returns no results:**
- Ensure you've scraped some data first
- Check your search criteria aren't too restrictive
- Verify the database contains data: check the statistics section

**Web interface not loading:**
- Ensure Flask is running: `python app.py`
- Check the correct URL: http://localhost:5000
- Look for error messages in the terminal

### Performance Optimization

**For faster searching:**
- Use specific criteria to limit result sets
- Consider the result limit setting

**For efficient scraping:**
- Start with smaller page ranges for testing
- Monitor system resources during large scrapes
- Consider running overnight for full database collection

## 📁 File Structure

```
tag scraper/
├── app.py              # Flask web application
├── scraper.py          # Core scraping functionality
├── requirements.txt    # Python dependencies
├── setup.sh           # Installation script
├── README.md          # This documentation
├── templates/
│   └── index.html     # Web interface template
├── artists.db         # SQLite database (created after first run)
└── venv/              # Virtual environment (created by setup)
```

## 🤝 Contributing

Feel free to improve this project by:
- Adding new search criteria
- Improving the UI/UX
- Optimizing scraping performance
- Adding data export formats
- Enhancing error handling

## 📄 License

This project is for educational and personal use. Please respect Danbooru's terms of service and API guidelines.

---

**Happy scraping! 🎨✨**
