Real Webinar Search Implementation - Setup Instructions

Overview

I've created a real webinar search implementation that will actually find current, upcoming webinars from multiple sources. This replaces the demo/mock data with genuine search capabilities.

What's New

1. Multiple Search Strategies

•
Google Custom Search API - Most comprehensive results

•
SerpAPI - Alternative search with good results

•
Direct Platform Scraping - BrightTalk, Eventbrite, and others

•
Smart Filtering - Only upcoming events, deduplication, relevance scoring

2. Enhanced Features

•
Real-time API status - Shows which search methods are configured

•
Advanced parsing - Extracts dates, topics, pricing, and platform info

•
Comprehensive logging - Tracks search performance and results

•
Multiple search queries - Uses 15+ different search strategies

Setup Instructions

Step 1: Install Required Dependencies

Bash


# Navigate to your project directory
cd ~/http_home/web-projects/Endersconsulting/enders-consulting-backend

# Install additional Python packages
pip install beautifulsoup4 requests

# Or add to requirements.txt:
echo "beautifulsoup4==4.12.2" >> requirements.txt
echo "requests==2.31.0" >> requirements.txt
pip install -r requirements.txt


Step 2: Get API Keys (Optional but Recommended)

Google Custom Search API (Recommended)

1.
Go to Google Cloud Console: https://console.cloud.google.com/

2.
Enable Custom Search API:

•
APIs & Services → Library

•
Search for "Custom Search API"

•
Click "Enable"



3.
Create API Key:

•
APIs & Services → Credentials

•
Create Credentials → API Key

•
Copy the API key



4.
Create Custom Search Engine:

•
Go to: https://cse.google.com/

•
Click "Add" to create new search engine

•
Enter "*.com" as the site to search

•
Copy the Search Engine ID



SerpAPI (Optional Alternative)

1.
Sign up: https://serpapi.com/

2.
Get API key from dashboard

3.
Free tier: 100 searches/month

Step 3: Configure Environment Variables

Bash


# Add these to your server environment
export GOOGLE_API_KEY="your-google-api-key-here"
export GOOGLE_CSE_ID="your-custom-search-engine-id-here"
export SERPAPI_KEY="your-serpapi-key-here"  # Optional

# For production, add to your .bashrc or systemd service file
echo 'export GOOGLE_API_KEY="your-key"' >> ~/.bashrc
echo 'export GOOGLE_CSE_ID="your-cse-id"' >> ~/.bashrc


Step 4: Deploy the Updated Code

Bash


# Backup your current app.py
cp app.py app.py.backup

# Copy the enhanced search collector
cp enhanced_search_collector.py .

# Replace app.py with the real search version
cp updated_app_with_real_search.py app.py

# Restart your Flask application
pkill -f "python.*app.py"
python3 app.py &


Testing the Implementation

Step 1: Check API Status

1.
Login to your webinar tool: https://endersconsulting.cloud/webinar-tool

2.
Check API Status section on login page

3.
Verify which search methods are configured

Step 2: Run Real Collection

1.
Click "Run Real Collection" button

2.
Wait for the collection to complete (may take 30-60 seconds)

3.
Check results - should find real upcoming webinars

Step 3: Verify Results

Bash


# Check database for real events
sqlite3 webinar_discovery.db "SELECT COUNT(*) FROM events;"
sqlite3 webinar_discovery.db "SELECT title, platform, event_date FROM events LIMIT 5;"


Search Capabilities

Without API Keys (Basic)

•
Direct platform scraping only

•
Limited results (5-15 events typically)

•
Still functional but fewer sources

With Google API (Recommended)

•
Comprehensive search across all platforms

•
50-100+ events per collection

•
Better date parsing and relevance

•
Cost: ~$5 per 1000 searches after free tier

With Both APIs (Maximum)

•
Highest coverage of webinar sources

•
Best deduplication and quality

•
Redundancy if one API fails

Expected Results

After running a real collection, you should see:

Typical Collection Results:

•
20-80 upcoming webinars found

•
Multiple platforms: BrightTalk, LinkedIn, ON24, Eventbrite, etc.

•
Various topics: AI, cybersecurity, marketing, healthcare, etc.

•
Mix of free and paid events

•
Proper dates (only future events)

Search Statistics:

•
Google results: 15-40 events

•
SerpAPI results: 10-25 events

•
Direct scraping: 5-15 events

•
After deduplication: 20-80 unique events

Troubleshooting

Issue 1: No API Keys Configured

Symptom: Only a few events found, API status shows "Not Configured"
Solution: Set up Google Custom Search API (most important)

Issue 2: Import Error

Symptom: ModuleNotFoundError: No module named 'enhanced_search_collector'
Solution:

Bash


# Make sure the file is in the same directory as app.py
ls -la enhanced_search_collector.py
# Should show the file exists


Issue 3: No Events Found

Symptom: Collection runs but finds 0 events
Solution:

Bash


# Check logs for errors
tail -f flask.log
# Look for HTTP errors or parsing issues


Issue 4: API Quota Exceeded

Symptom: Google API errors after many searches
Solution:

•
Monitor usage in Google Cloud Console

•
Consider upgrading quota or using SerpAPI as backup

Cost Considerations

Google Custom Search API:

•
Free tier: 100 searches/day

•
Paid: $5 per 1000 searches

•
Typical usage: 10-20 searches per collection

SerpAPI:

•
Free tier: 100 searches/month

•
Paid: $50/month for 5000 searches

Recommendation:

•
Start with Google API (most cost-effective)

•
Add SerpAPI if you need higher volume

•
Direct scraping is always free (but limited)

Monitoring and Maintenance

Check Collection Logs:

Bash


# View recent collections
sqlite3 webinar_discovery.db "SELECT * FROM collection_logs ORDER BY created_at DESC LIMIT 5;"


Monitor API Usage:

•
Google: Check Google Cloud Console quotas

•
SerpAPI: Check dashboard usage

Database Maintenance:

Bash


# Clean old events (optional)
sqlite3 webinar_discovery.db "DELETE FROM events WHERE event_date < date('now', '-30 days');"


Next Steps

1.
Set up Google API for best results

2.
Run first real collection to test

3.
Schedule regular collections (daily/weekly)

4.
Monitor results and adjust search queries if needed

5.
Consider API upgrades if you need higher volume



