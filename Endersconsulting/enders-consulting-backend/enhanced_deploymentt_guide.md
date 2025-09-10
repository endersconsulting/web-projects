Enhanced Webinar Discovery Tool - Deployment Guide

Overview

This enhanced version of the webinar discovery tool extracts individual webinar events with specific dates, times, speaker information, and contact details from webinar listing pages. Instead of just finding webinar directory pages, it now scrapes those pages to extract the actual individual events.

Key Enhancements

🚀 Individual Event Extraction

•
Scrapes listing pages to find individual webinars

•
Extracts specific dates and times for each event

•
Identifies speakers and presenters

•
Captures contact information (emails, phones, organizers)

•
Determines if events are free or paid

•
Categorizes by topic (AI, cybersecurity, marketing, etc.)

🎯 Enhanced Data Fields

•
speaker - Speaker/presenter name

•
organizer - Organizing company/person

•
contact_email - Contact email address

•
contact_phone - Contact phone number

•
source_page - Original listing page URL

•
event_date - Specific date and time

•
is_free - Whether the event is free

•
topic_category - Categorized topic

🔍 Multi-Platform Support

•
BrightTalk - Professional webinars

•
ON24 - Enterprise webinar platform

•
Eventbrite - Event registration platform

•
Zoom - Zoom webinars

•
LinkedIn - LinkedIn events

•
Meetup - Meetup events

•
Generic platforms - Universal scraping patterns

Installation & Setup

Step 1: Deploy Enhanced Files

Replace your existing files with the enhanced versions:

Bash


# Navigate to your backend directory
cd ~/http_home/web-projects/Endersconsulting/enders-consulting-backend/

# Backup existing files
cp app.py app.py.backup
cp enhanced_search_collector.py enhanced_search_collector.py.backup 2>/dev/null || true

# Deploy enhanced files
# Copy enhanced_webinar_scraper.py to your backend directory
# Copy updated_app_with_enhanced_scraping.py and rename to app.py


Step 2: Install Dependencies

Bash


# Install required Python packages
pip install beautifulsoup4 requests

# Or add to requirements.txt
echo "beautifulsoup4==4.12.2" >> requirements.txt
echo "requests==2.31.0" >> requirements.txt
pip install -r requirements.txt


Step 3: Database Schema Update

The enhanced version automatically adds new columns to your database:

SQL


-- New columns added automatically:
ALTER TABLE events ADD COLUMN speaker TEXT;
ALTER TABLE events ADD COLUMN organizer TEXT;
ALTER TABLE events ADD COLUMN contact_email TEXT;
ALTER TABLE events ADD COLUMN contact_phone TEXT;
ALTER TABLE events ADD COLUMN source_page TEXT;


Step 4: Environment Variables

Set up your API keys (same as before):

Bash


# Add to ~/.bashrc or .env file
export GOOGLE_API_KEY="your-google-api-key"
export GOOGLE_CSE_ID="your-cse-id"
export SERPAPI_KEY="your-serpapi-key"  # Optional

# Security credentials
export WEBINAR_USERNAME="your-secure-username"
export WEBINAR_PASSWORD="your-secure-password"
export SECRET_KEY="your-super-secure-secret-key"


Step 5: Restart Flask Application

Bash


# Kill existing Flask process
pkill -f "python.*app.py"

# Start enhanced version
cd ~/http_home/web-projects/Endersconsulting/enders-consulting-backend/
source ~/.bashrc  # Load environment variables
python3 app.py &

# Or use nohup for persistent running
nohup python3 app.py > flask.log 2>&1 &


How It Works

Phase 1: Find Listing Pages

1.
Search APIs find webinar directory/calendar pages

2.
Platform detection identifies known webinar platforms

3.
Content analysis filters for listing pages vs individual events

Phase 2: Extract Individual Events

1.
Page scraping downloads each listing page

2.
Platform-specific parsing uses tailored CSS selectors

3.
Event extraction finds individual webinar containers

4.
Data parsing extracts titles, dates, speakers, contact info

Phase 3: Data Enhancement

1.
Date parsing handles multiple date formats

2.
Contact extraction finds emails, phones, organizers

3.
Topic categorization classifies by subject matter

4.
Platform identification determines hosting platform

5.
Deduplication removes duplicate events

Phase 4: Database Storage

1.
Schema validation ensures all fields are present

2.
Conflict resolution updates existing events

3.
Relationship mapping links speakers to events

Expected Results

Before Enhancement

•
Found 26 webinar listing pages

•
Generic titles like "Upcoming Webinars"

•
No specific dates

•
No contact information

After Enhancement

•
Extracts 100-300 individual events from those 26 listing pages

•
Specific titles like "AI in Healthcare: Practical Applications"

•
Actual dates and times: "2025-09-15 14:00:00"

•
Contact details: emails, phones, organizer names

•
Speaker information: "Dr. Jane Smith, Chief Data Scientist"

New Features in Interface

Enhanced Collection Button

•
🚀 Run Enhanced Collection - Triggers individual event extraction

•
Shows detailed progress and statistics

•
Reports listing pages found vs individual events extracted

Enhanced Event Display

•
Contact Information section with emails, phones, organizers

•
Speaker details prominently displayed

•
Specific dates and times instead of "TBD"

•
Topic categories for better filtering

•
Free/Paid indicators

Enhanced Analytics

•
Events with Dates - Shows how many have specific dates

•
Events with Contact Info - Shows contact information availability

•
Events with Speakers - Shows speaker information availability

•
Contact Statistics - Breakdown of email/phone/organizer data

Enhanced Filtering

•
Has Contact Info filter

•
Topic Category filter with 10+ categories

•
Platform filter with major webinar platforms

•
Free/Paid filtering

API Endpoints

New Enhanced Endpoints

POST /api/webinars/collect/enhanced

Runs the enhanced collection with individual event extraction.

Response:

JSON


{
  "status": "success",
  "data": {
    "events_found": 156,
    "events_new": 89,
    "events_updated": 67,
    "execution_time": 45.2,
    "search_stats": {
      "listing_pages_found": 23,
      "individual_events_extracted": 156,
      "events_with_dates": 134,
      "events_with_contact_info": 78,
      "duplicates_removed": 12
    }
  }
}


GET /api/webinars/analytics/enhanced

Get enhanced analytics with contact information statistics.

Response:

JSON


{
  "status": "success",
  "data": {
    "event_statistics": {
      "total_events": 156,
      "upcoming_events": 134,
      "events_with_dates": 134,
      "events_with_contact": 78,
      "events_with_speakers": 92,
      "free_events": 67
    },
    "contact_statistics": {
      "events_with_email": 45,
      "events_with_phone": 23,
      "events_with_organizer": 78
    }
  }
}


Enhanced Event Fields

Events now include these additional fields:

JSON


{
  "id": 123,
  "title": "AI in Healthcare: Practical Applications",
  "description": "Learn how AI is transforming healthcare...",
  "event_date": "2025-09-15 14:00:00",
  "registration_url": "https://example.com/register",
  "platform": "BrightTalk",
  "topic_category": "artificial-intelligence",
  "is_free": true,
  "speaker": "Dr. Jane Smith, Chief Data Scientist",
  "organizer": "Healthcare AI Institute",
  "contact_email": "info@healthcareai.org",
  "contact_phone": "+1-555-123-4567",
  "source_page": "https://brighttalk.com/webinars/healthcare"
}


Performance & Scalability

Threading

•
Concurrent scraping of up to 5 listing pages simultaneously

•
Rate limiting to respect website policies

•
Timeout handling for unresponsive pages

Database Optimization

•
Efficient deduplication using title and URL combinations

•
Incremental updates only modify changed events

•
Indexed queries for fast filtering and searching

Error Handling

•
Graceful failures continue processing other pages

•
Detailed logging for debugging scraping issues

•
Fallback mechanisms when specific selectors fail

Monitoring & Maintenance

Log Analysis

Bash


# Monitor collection progress
tail -f flask.log | grep "enhanced_search_collector"

# Check for errors
grep "ERROR" flask.log | tail -20

# Monitor database growth
sqlite3 webinar_discovery.db "SELECT COUNT(*) FROM events;"


Performance Metrics

•
Collection time - Should complete in 30-60 seconds

•
Success rate - Aim for 80%+ successful page scraping

•
Data quality - 70%+ events should have dates

•
Contact coverage - 50%+ events should have contact info

Regular Maintenance

•
Weekly collections to keep data fresh

•
Monthly database cleanup to remove old events

•
Quarterly selector updates as websites change

Troubleshooting

Common Issues

1. No Individual Events Found

Symptoms: Collection finds listing pages but extracts 0 events
Solutions:

•
Check if websites have changed their HTML structure

•
Update CSS selectors in platform_selectors

•
Enable debug logging to see parsing details

2. Missing Contact Information

Symptoms: Events found but no contact details
Solutions:

•
Review contact_patterns regular expressions

•
Check if websites moved contact info to different sections

•
Add new contact extraction patterns

3. Date Parsing Failures

Symptoms: Events have empty event_date fields
Solutions:

•
Update date_patterns with new formats

•
Check _parse_date_string() function

•
Add support for new date formats

4. Platform Detection Issues

Symptoms: All events show "Other" platform
Solutions:

•
Update platform_mapping with new domains

•
Check URL parsing logic

•
Add new platform identifiers

Debug Mode

Enable detailed logging:

Python


# Add to app.py
import logging
logging.basicConfig(level=logging.DEBUG)


Testing Individual Components

Python


# Test date parsing
from enhanced_webinar_scraper import EnhancedWebinarScraper
scraper = EnhancedWebinarScraper()
date = scraper._extract_enhanced_date("September 15, 2025 at 2:00 PM")
print(date)

# Test contact extraction
contact = scraper._extract_contact_information("Contact: john@example.com or call 555-123-4567")
print(contact)


Security Considerations

Rate Limiting

•
Respectful scraping with delays between requests

•
User-Agent rotation to appear as regular browser

•
Timeout limits to prevent hanging requests

Data Privacy

•
Contact information is publicly available data only

•
No personal data collection beyond what's publicly posted

•
Secure storage of collected information

Access Control

•
Password protection for the tool interface

•
Session management with automatic timeouts

•
Secure API endpoints with authentication

Future Enhancements

Planned Features

1.
Calendar Integration - Export events to Google Calendar/Outlook

2.
Email Notifications - Alert for new events in specific topics

3.
Advanced Filtering - Date ranges, location, language

4.
Bulk Export - CSV/Excel export of filtered events

5.
API Integration - Direct integration with CRM systems

Platform Expansion

1.
Microsoft Teams events

2.
WebEx webinars

3.
BigMarker events

4.
Hopin virtual events

5.
Custom corporate webinar platforms

AI Enhancement

1.
Content analysis for better topic categorization

2.
Duplicate detection using semantic similarity

3.
Quality scoring for event relevance

4.
Automatic summarization of event descriptions

Support & Updates

Getting Help

•
Check logs first for error details

•
Test individual components to isolate issues

•
Update selectors as websites change their structure

Staying Updated

•
Monitor website changes for major webinar platforms

•
Update CSS selectors quarterly

•
Add new platforms as they become popular

•
Enhance parsing patterns based on new data formats



