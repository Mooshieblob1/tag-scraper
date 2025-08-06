# Git Setup Guide

This document explains the git configuration for the Danbooru Artist Scraper project.

## Files Included in Git

### Core Application Files
- `app.py` - Flask web application
- `scraper.py` - Main scraping functionality with 429 detection
- `requirements.txt` - Core Python dependencies
- `requirements-dev.txt` - Development dependencies
- `setup.sh` - Installation and setup script

### Web Interface
- `templates/index.html` - Web interface template

### Testing and Monitoring
- `rate_limit_monitor.py` - Comprehensive rate limiting test tool
- `test_enhanced_429.py` - Simple 429 detection demonstration
- `test_api.py` - API validation script

### Documentation
- `README.md` - Main project documentation
- `RATE_LIMIT_GUIDE.md` - Detailed 429 detection documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `USAGE_GUIDE.md` - User guide and examples

### Configuration
- `.gitignore` - Git ignore rules
- `check_git_status.sh` - Git status verification script

## Files Excluded from Git

### Generated/Runtime Files
- `artists.db` - SQLite database (user-specific data)
- `rate_limit_test_report.json` - Test reports
- `rate_limit_monitor.log` - Log files
- `*.log` - All log files

### Environment and Dependencies
- `venv/` - Virtual environment directory
- `.env` - Environment variables (API keys)
- `__pycache__/` - Python bytecode cache
- `*.pyc`, `*.pyo` - Compiled Python files

### IDE and OS Files
- `.vscode/`, `.idea/` - IDE configuration
- `.DS_Store`, `Thumbs.db` - OS-specific files

### Backup and Temporary Files
- `*.bak`, `*.backup`, `*.tmp` - Backup files

## Git Workflow

### Initial Setup
```bash
# Initialize git repository
git init

# Add all tracked files
git add .

# Initial commit
git commit -m "Initial commit: Danbooru Artist Scraper with enhanced 429 detection"
```

### Adding Remote Repository
```bash
# Add remote origin
git remote add origin <your-repository-url>

# Push to remote
git push -u origin main
```

### Regular Development
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push
```

## Branch Strategy

### Main Branch
- `main` - Stable, production-ready code
- All features should be tested before merging

### Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Work on feature
git add .
git commit -m "Add new feature"

# Switch back to main
git checkout main

# Merge feature
git merge feature/new-feature

# Delete feature branch
git branch -d feature/new-feature
```

## File Size Considerations

### Large Files Excluded
- Database files can grow large (100MB+) and are user-specific
- Virtual environments contain many small files
- Log files can accumulate over time

### Why These Files Are Gitignored
1. **Database Files** (`*.db`):
   - User-specific scraped data
   - Can be very large
   - Should be backed up separately

2. **Virtual Environment** (`venv/`):
   - Platform-specific compiled packages
   - Can be recreated from requirements.txt
   - Contains thousands of files

3. **Environment Files** (`.env`):
   - Contains API keys and secrets
   - Should never be committed for security

4. **Log Files** (`*.log`):
   - Runtime-generated content
   - Can grow large over time
   - User-specific debug information

## Security Considerations

### API Keys and Secrets
- Never commit `.env` files with API keys
- Use environment variables for sensitive data
- Include `.env.example` template if needed

### Database Security
- Database files may contain scraped data
- Respect data privacy and usage terms
- Don't commit user-generated databases

## Backup Strategy

### What to Backup Separately
- `artists.db` - Your scraped data
- `.env` - Your API configuration (securely)
- Custom configuration files

### What Git Handles
- All source code
- Documentation
- Configuration templates
- Test scripts

## Collaboration Guidelines

### For Contributors
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### For Maintainers
1. Review pull requests carefully
2. Test rate limiting features
3. Update documentation as needed
4. Tag releases with version numbers

## Testing Before Commit

Use the provided script to check git status:
```bash
./check_git_status.sh
```

This will show:
- Files that will be tracked
- Files that are ignored
- Summary statistics

## Version Control Best Practices

### Commit Messages
- Use clear, descriptive messages
- Reference issues when applicable
- Use conventional commit format if desired

### File Organization
- Keep related files together
- Use descriptive file names
- Maintain consistent code style

### Documentation
- Update README.md for user-facing changes
- Update technical docs for implementation changes
- Include examples for new features

---

This git configuration ensures that only necessary project files are tracked while excluding user-specific data, generated files, and sensitive information.
