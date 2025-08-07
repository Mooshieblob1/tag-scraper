#!/usr/bin/env python3
"""
Hugging Face Spaces entry point for Danbooru Artist Scraper
"""
import os
from app import app

if __name__ == "__main__":
    # Hugging Face Spaces runs on port 7860 by default
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
