# Danbooru Artist Scraper - Deployment Guide

## 🚀 Deployment Options

### ✅ **Recommended: Railway Deployment**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Visit [railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "Deploy from GitHub repo"
   - Select this repository
   - Railway will auto-detect Python and deploy

3. **Set Environment Variables in Railway:**
   ```
   DANBOORU_USERNAME=your_username
   DANBOORU_API_KEY=your_api_key
   ```

4. **Your app will be live at:** `https://your-app-name.railway.app`

### ✅ **Alternative: Render Deployment**

1. **Push to GitHub** (same as above)

2. **Deploy on Render:**
   - Visit [render.com](https://render.com)
   - Sign up/Login with GitHub
   - Click "New Web Service"
   - Connect your repository
   - Use these settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python app.py`

3. **Set Environment Variables in Render dashboard**

### ✅ **Heroku Deployment**

1. **Install Heroku CLI**
2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set DANBOORU_USERNAME=your_username
   heroku config:set DANBOORU_API_KEY=your_api_key
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

## 🚫 **Why Not Cloudflare Pages?**

Cloudflare Pages is for **static sites** only. Your app uses:
- ✅ Flask Python backend
- ✅ SQLite database  
- ✅ Server-side processing

For Cloudflare, you'd need to completely restructure as a client-side app.

## ✅ **NEW: Hugging Face Spaces Deployment**

**Perfect for sharing your app publicly!**

1. **Prepare Files** (already added):
   ```
   README_HF.md      # Hugging Face Spaces README
   Dockerfile.hf     # Docker configuration for HF Spaces
   app_hf.py        # Entry point for HF Spaces
   ```

2. **Create Hugging Face Space:**
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space)
   - Choose "Docker" as SDK
   - Upload/sync your repository files

3. **Set Environment Variables (Optional):**
   ```
   DANBOORU_USERNAME=your_username_here
   DANBOORU_API_KEY=your_api_key_here
   ```

4. **Benefits:**
   - ✅ **Free hosting**
   - ✅ **Public sharing**
   - ✅ **Easy deployment**
   - ✅ **Built-in credential management** (users can input their own API keys)
   - ✅ **Persistent storage**

## 📁 **Files Added for Deployment**

- `Procfile` - Tells platforms how to run your app
- `runtime.txt` - Specifies Python version  
- `Dockerfile.hf` - Docker config for Hugging Face Spaces
- `app_hf.py` - Entry point for Hugging Face Spaces
- `README_HF.md` - Hugging Face Spaces description
- Updated `app.py` - Reads PORT from environment

## 🔐 **Important: Environment Variables**

Always set these in your deployment platform:
```
DANBOORU_USERNAME=your_username_here
DANBOORU_API_KEY=your_api_key_here
```

**Note for Hugging Face Spaces:** Environment variables are optional since users can input credentials directly in the web interface!

## ✅ **Ready to Deploy!**

Your repository is now ready for deployment on:
- **Hugging Face Spaces** (NEW - great for public sharing!)
- Railway (recommended - easiest)
- Render (good free tier)
- Heroku (classic choice)
- DigitalOcean App Platform
- AWS Elastic Beanstalk
