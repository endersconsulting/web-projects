# news_feed_backend.py
# Backend API endpoint to add to your Flask app for The Hacker News RSS feed

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def add_news_feed_routes(app):
    """Add news feed routes to your existing Flask app"""
    
    @app.route('/api/news/cybersecurity', methods=['GET'])
    def get_cybersecurity_news():
        """Fetch latest cybersecurity news from The Hacker News RSS feed"""
        try:
            # Fetch RSS feed
            rss_url = "https://feeds.feedburner.com/TheHackersNews"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(rss_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Extract articles
            articles = []
            items = root.findall('.//item')
            
            for item in items[:10]:  # Get latest 10 articles
                try:
                    # Extract basic info
                    title = item.find('title').text if item.find('title') is not None else "No title"
                    link = item.find('link').text if item.find('link') is not None else ""
                    description = item.find('description').text if item.find('description') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    author = item.find('author').text if item.find('author') is not None else "The Hacker News"
                    
                    # Clean up description (remove CDATA and HTML tags)
                    if description:
                        description = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', description, flags=re.DOTALL)
                        description = re.sub(r'<[^>]+>', '', description)  # Remove HTML tags
                        description = description.strip()
                        # Limit description length
                        if len(description) > 200:
                            description = description[:200] + "..."
                    
                    # Parse publication date
                    formatted_date = ""
                    if pub_date:
                        try:
                            # Parse RSS date format: "Sat, 13 Sep 2025 14:34:00 +0530"
                            dt = datetime.strptime(pub_date.split(' +')[0], "%a, %d %b %Y %H:%M:%S")
                            formatted_date = dt.strftime("%B %d, %Y")
                        except:
                            formatted_date = pub_date.split(',')[1].strip() if ',' in pub_date else pub_date
                    
                    # Extract image URL from enclosure
                    image_url = ""
                    enclosure = item.find('enclosure')
                    if enclosure is not None and enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('url', '')
                    
                    # Clean up author
                    if author and 'info@thehackernews.com' in author:
                        author = "The Hacker News"
                    
                    # Determine category based on title/description
                    category = categorize_article(title, description)
                    
                    article = {
                        'title': title,
                        'description': description,
                        'link': link,
                        'published_date': formatted_date,
                        'author': author,
                        'image_url': image_url,
                        'category': category,
                        'source': 'The Hacker News'
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue
            
            return jsonify({
                'status': 'success',
                'data': {
                    'articles': articles,
                    'total': len(articles),
                    'source': 'The Hacker News',
                    'last_updated': datetime.now().isoformat()
                }
            })
            
        except requests.RequestException as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch news feed',
                'error': str(e)
            }), 500
            
        except ET.ParseError as e:
            logger.error(f"Error parsing RSS XML: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to parse news feed',
                'error': str(e)
            }), 500
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Internal server error',
                'error': str(e)
            }), 500

def categorize_article(title, description):
    """Categorize article based on title and description keywords"""
    content = (title + " " + description).lower()
    
    # Define category keywords
    categories = {
        'Data Breach': ['data breach', 'data theft', 'stolen data', 'leaked data', 'database breach'],
        'Ransomware': ['ransomware', 'ransom', 'encryption attack', 'crypto locker'],
        'Vulnerability': ['vulnerability', 'cve-', 'zero-day', 'exploit', 'patch', 'security flaw'],
        'Malware': ['malware', 'trojan', 'virus', 'backdoor', 'spyware', 'adware'],
        'Cyber Attack': ['cyber attack', 'cyberattack', 'hacking', 'breach', 'intrusion'],
        'Mobile Security': ['android', 'ios', 'mobile', 'smartphone', 'app security'],
        'Cloud Security': ['cloud', 'aws', 'azure', 'saas', 'cloud-native'],
        'AI Security': ['artificial intelligence', 'ai security', 'machine learning', 'deepfake'],
        'Critical Infrastructure': ['critical infrastructure', 'industrial', 'scada', 'ics security'],
        'Privacy': ['privacy', 'gdpr', 'data protection', 'surveillance'],
        'Phishing': ['phishing', 'social engineering', 'email attack', 'credential theft']
    }
    
    # Check for category matches
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return 'General Security'

# Additional utility function for caching (optional)
def get_cached_news():
    """Get cached news with simple in-memory caching"""
    import time
    
    # Simple in-memory cache (in production, use Redis or similar)
    if not hasattr(get_cached_news, 'cache'):
        get_cached_news.cache = {'data': None, 'timestamp': 0}
    
    # Cache for 15 minutes
    cache_duration = 15 * 60  # 15 minutes in seconds
    current_time = time.time()
    
    if (get_cached_news.cache['data'] is None or 
        current_time - get_cached_news.cache['timestamp'] > cache_duration):
        
        # Cache expired or doesn't exist, fetch new data
        try:
            # This would call the main function logic
            # For now, return None to indicate cache miss
            return None
        except:
            return get_cached_news.cache['data']  # Return old cache on error
    
    return get_cached_news.cache['data']

# Integration instructions:
"""
To add this to your existing Flask app (app.py), add these lines:

1. Import the function at the top of your app.py:
   from news_feed_backend import add_news_feed_routes

2. Add this line after creating your Flask app instance:
   add_news_feed_routes(app)

3. Install required dependency:
   pip install requests

4. Test the endpoint:
   curl https://endersconsulting.cloud/api/news/cybersecurity

The endpoint will return JSON with the latest cybersecurity news articles.
"""

