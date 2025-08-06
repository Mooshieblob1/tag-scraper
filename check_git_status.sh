#!/bin/bash

# Git Status Check Script
# Shows what files would be tracked/ignored by git

echo "🔍 Git Status Check for Danbooru Artist Scraper"
echo "=" * 50

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "⚠️  Git repository not initialized. Run 'git init' first."
    echo ""
    echo "To set up git:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

echo "📂 Files that would be tracked by git:"
echo ""

# Show files that would be added
git ls-files --others --exclude-standard | head -20
if [ $(git ls-files --others --exclude-standard | wc -l) -gt 20 ]; then
    echo "... and $(( $(git ls-files --others --exclude-standard | wc -l) - 20 )) more files"
fi

echo ""
echo "🚫 Files ignored by .gitignore:"
echo ""

# Show ignored files
git ls-files --others --ignored --exclude-standard | head -10
if [ $(git ls-files --others --ignored --exclude-standard | wc -l) -gt 10 ]; then
    echo "... and $(( $(git ls-files --others --ignored --exclude-standard | wc -l) - 10 )) more ignored files"
fi

echo ""
echo "📊 Summary:"
echo "- Tracked files: $(git ls-files | wc -l)"
echo "- Untracked files: $(git ls-files --others --exclude-standard | wc -l)"
echo "- Ignored files: $(git ls-files --others --ignored --exclude-standard | wc -l)"

echo ""
echo "✅ Repository is ready for git operations!"
echo ""
echo "Next steps:"
echo "  git add .                    # Stage all tracked files"
echo "  git commit -m 'message'      # Commit changes"
echo "  git remote add origin <url>  # Add remote repository"
echo "  git push -u origin main      # Push to remote"
