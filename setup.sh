#!/bin/bash

# Danbooru Artist Scraper Setup Script

echo "🎨 Setting up Danbooru Artist Scraper..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the web application: python app.py"
echo "3. Open your browser to: http://localhost:5000"
echo ""
echo "📖 Usage Tips:"
echo "- Start by scraping a few pages (1-10) to test"
echo "- Use the search functionality to find specific artists"
echo "- The full database (1000 pages) will take several hours to scrape"
echo "- Results are saved to artists.db SQLite database"
echo ""
echo "🔧 Development Notes:"
echo "- Database files (*.db) are gitignored and won't be committed"
echo "- Virtual environment (venv/) is gitignored"
echo "- Create a .env file for API credentials (also gitignored)"
echo "- Use 'pip install -r requirements-dev.txt' for development tools"
