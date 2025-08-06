# 🎨 Danbooru Artist Scraper - Usage Guide

## ✨ What We've Built

A complete web-based application for scraping and searching Danbooru artist data with:

### 🏗️ Core Features
- **JSON API Integration**: Uses Danbooru's official JSON API with proper pagination (a0, a1, a2...)
- **Rate Limiting**: Respects Danbooru's 10 req/sec limit with conservative 6.7 req/sec setting
- **Web Interface**: Modern, responsive Flask-based UI
- **Database Storage**: SQLite database for efficient data storage and querying
- **Real-time Progress**: Live progress tracking during scraping
- **Advanced Search**: Filter artists by name patterns and other criteria

### 📊 Current Status
- **Working**: Successfully tested with 3000+ artists scraped
- **Authentication**: Currently using public API (no authentication required)
- **Data Fields**: id, name, other_names, group_name, created_at, updated_at, is_banned, is_deleted

## 🚀 How to Use

### 1. Quick Start
```bash
cd "/home/blob/Repositories/tag scraper"
source venv/bin/activate
python app.py
```
Then open http://localhost:5000 in your browser.

### 2. Command Line Usage
```bash
cd "/home/blob/Repositories/tag scraper"
source venv/bin/activate
python scraper.py
```
Choose from interactive options:
- Test scrape (3 pages)
- Full scrape (until exhausted)
- Custom scrape (specify range)
- Show database stats

### 3. Web Interface Features

#### Data Collection
- **Start Page**: 0-based pagination (a0 = first page)
- **Max Pages**: Optional limit (leave empty for full scrape)
- **Real-time Progress**: Live updates during scraping
- **Stop/Resume**: Can stop and resume scraping

#### Search & Filter
- **Name starts with**: Find artists like "A*"
- **Name contains**: Search within names
- **Result limits**: 50-1000 results per search
- **Export**: JSON export of all data

## 🔧 Technical Details

### Rate Limiting & 429 Detection
- **Base URL**: `https://danbooru.donmai.us/artists.json`
- **Pagination**: `?page=a0&limit=1000` (a0, a1, a2...)
- **Rate Limit**: 6.7 requests/second (conservative under 10 req/sec API limit)
- **429 Detection**: Automatic handling of "Too Many Requests" responses
- **Adaptive Backoff**: Dynamic rate adjustment based on server feedback
- **Recovery**: Gradual return to optimal rates after successful operations

### Database Schema
```sql
CREATE TABLE artists (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    post_count INTEGER,        -- Currently always 0 (API limitation)
    other_names TEXT,          -- Comma-separated alternative names
    group_name TEXT,           -- Artist group/circle
    url_string TEXT,           -- Artist URLs
    is_active BOOLEAN,
    created_at TEXT,
    updated_at TEXT,
    is_banned BOOLEAN,
    is_deleted BOOLEAN
);
```

### Files Structure
```
tag scraper/
├── scraper.py          # Core scraping functionality
├── app.py              # Flask web application
├── templates/
│   └── index.html      # Web interface
├── requirements.txt    # Dependencies
├── setup.sh           # Installation script
├── .env               # Environment variables (optional)
├── artists.db         # SQLite database (created after first run)
└── README.md          # Full documentation
```

## 🎯 Example Searches

### Find Artists Starting with "A"
1. In web interface: Set "Name starts with" to "A"
2. Command line: `scraper.get_artists_by_criteria(name_starts_with="A")`

### Find Artists with Specific Terms
1. In web interface: Set "Name contains" to "pixel"
2. Command line: `scraper.get_artists_by_criteria(name_contains="pixel")`

### Find Artists by Group
1. Search for group names in "Name contains"
2. Database query: `SELECT * FROM artists WHERE group_name LIKE '%groupname%'`

## ⚠️ Important Notes

### API Limitations
- **Post Count**: Not available in public API (shows as 0)
- **Authentication**: Available but not required for basic artist data
- **Rate Limits**: Must respect 10 req/sec maximum

### Performance
- **Full Scrape**: Can take several hours (estimated 50,000+ artists)
- **Memory**: Very efficient with SQLite storage
- **Network**: Requires stable internet connection

### Data Quality
- **Completeness**: Gets all basic artist metadata
- **Freshness**: Data is live from Danbooru
- **Duplicates**: Handled automatically by database constraints

## 🔮 Future Enhancements

### Potential Improvements
1. **Post Count Integration**: Find alternative API endpoints for post counts
2. **Image Support**: Add artist avatar/sample images
3. **Advanced Filters**: Date ranges, popularity metrics
4. **Export Formats**: CSV, Excel, XML support
5. **Scheduling**: Automated daily/weekly updates
6. **API Authentication**: Full authentication for premium features

### Authentication Setup (Optional)
To use with Danbooru account:
1. Create account on danbooru.donmai.us
2. Generate API key in profile settings
3. Update `.env` file:
   ```
   DANBOORU_API_KEY=your_api_key_here
   DANBOORU_USERNAME=your_username_here
   ```

## 🛟 Troubleshooting

### Common Issues
1. **"Module not found"**: Run `source venv/bin/activate` first
2. **"No artists found"**: Check internet connection and API status
3. **"Rate limited"**: Automatic retry with backoff
4. **"Database locked"**: Close any other database connections

### Performance Tips
- Start with small page ranges for testing
- Use specific search criteria to limit results
- Monitor system resources during large scrapes
- Consider running overnight for full collection

## 📞 Support

This is a complete, working solution for scraping Danbooru artist data. The system is designed to be respectful of Danbooru's resources while providing comprehensive artist information for research, analysis, or personal use.

**Remember to use responsibly and respect Danbooru's terms of service!**
