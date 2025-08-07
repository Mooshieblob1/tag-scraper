#!/bin/bash

# Script to prepare files for Hugging Face Spaces deployment
echo "🚀 Preparing files for Hugging Face Spaces..."

# Create a deployment directory
mkdir -p hf_deployment
cd hf_deployment

# Copy main application files
echo "📄 Copying application files..."
cp ../app.py .
cp ../app_hf.py .
cp ../scraper.py .
cp ../requirements.txt .

# Copy templates directory
echo "📁 Copying templates..."
cp -r ../templates .

# Rename files for Hugging Face Spaces
echo "🔄 Renaming files for HF Spaces..."
cp ../README_HF.md README.md
cp ../Dockerfile.hf Dockerfile

# Create .gitignore for HF Spaces
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
artists.db
*.log
.DS_Store
EOF

echo "✅ Files prepared in 'hf_deployment' directory!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://huggingface.co/new-space"
echo "2. Choose 'Docker' as SDK"
echo "3. Upload all files from the 'hf_deployment' directory"
echo "4. Your app will be available at https://huggingface.co/spaces/USERNAME/SPACE_NAME"
echo ""
echo "📁 Files to upload:"
ls -la

cd ..
