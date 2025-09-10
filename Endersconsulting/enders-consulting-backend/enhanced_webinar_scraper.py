# enhanced_webinar_scraper.py
# Enhanced webinar scraper that extracts individual events from listing pages
# This module scrapes webinar directory pages to find specific events with dates and contact info

import requests
import json
import re
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin, parse_qs
from bs4 import BeautifulSoup
import logging
import time
import os
from typing import List, Dict, Optional
import concurrent.futures
from threading import Lock

logger = logging.getLogger(__name__)

class EnhancedWebinarScraper:
    """Enhanced webinar scraper that extracts individual events from listing pages"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.google_cse_id = os.environ.get('GOOGLE_CSE_ID')
        self.serpapi_key = os.environ.get('SERPAPI_KEY')
        
        # Thread safety
        self.db_lock = Lock()
        
        # Enhanced search queries for finding webinar listing pages
        self.listing_page_queries = [
            # Time-based searches for current events
            "upcoming webinars September 2025 register",
            "webinar calendar October 2025",
            "virtual events schedule September 2025",
            "online conference registration 2025",
            
            # Platform-specific listing pages
            'site:brighttalk.com "upcoming" OR "live" webinar 2025',
            'site:on24.com "upcoming events" OR "webinar calendar"',
            'site:zoom.us/webinar "upcoming" 2025',
            'site:gotowebinar.com "upcoming webinars"',
            'site:eventbrite.com "webinar" "September 2025" OR "October 2025"',
            
            # Industry-specific webinar calendars
            "cybersecurity webinar calendar 2025",
            "marketing webinar schedule September 2025",
            "healthcare webinar events October 2025",
            "technology webinar series 2025",
            "business webinar calendar upcoming",
            
            # Educational and professional development
            "professional development webinar series 2025",
            "continuing education webinar schedule",
            "training webinar calendar September 2025",
            "certification webinar events 2025"
        ]
        
        # Patterns for extracting dates from various formats
        self.date_patterns = [
            # Standard formats
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            
            # Month name formats
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            
            # Relative dates
            r'(today|tomorrow|next week|this week)',
            r'in\s+\d+\s+(days?|weeks?|months?)',
            
            # Time formats
            r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)',
            r'\d{1,2}:\d{2}',
            
            # ISO format
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        ]
        
        # Contact information patterns
        self.contact_patterns = {
            'email': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ],
            'phone': [
                r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                r'\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                r'phone[:\s]*(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
            ],
            'organization': [
                r'hosted by[:\s]*([^,\n\.]+)',
                r'presented by[:\s]*([^,\n\.]+)',
                r'organized by[:\s]*([^,\n\.]+)',
                r'sponsor[:\s]*([^,\n\.]+)'
            ]
        }
        
        # Common webinar platforms and their specific selectors
        self.platform_selectors = {
            'brighttalk.com': {
                'event_container': '.event-card, .webinar-card, .talk-card',
                'title': 'h3, h4, .title, .event-title',
                'date': '.date, .datetime, .event-date, time',
                'description': '.description, .summary, .abstract',
                'speaker': '.speaker, .presenter, .author',
                'registration': 'a[href*="register"], a[href*="signup"]'
            },
            'on24.com': {
                'event_container': '.event-item, .webinar-item, .session',
                'title': 'h2, h3, .session-title, .event-title',
                'date': '.date, .datetime, .session-date',
                'description': '.description, .session-description',
                'speaker': '.speaker, .presenter',
                'registration': 'a[href*="register"], .register-button'
            },
            'eventbrite.com': {
                'event_container': '.event-card, .search-event-card, .event-listing',
                'title': 'h3, h2, .event-title',
                'date': '.date, .event-date, time',
                'description': '.event-description, .summary',
                'speaker': '.organizer, .host',
                'registration': 'a[href*="eventbrite.com/e/"]'
            },
            'zoom.us': {
                'event_container': '.webinar-item, .event-card',
                'title': 'h3, h2, .webinar-title',
                'date': '.date, .datetime, .webinar-date',
                'description': '.description, .webinar-description',
                'speaker': '.host, .presenter',
                'registration': 'a[href*="zoom.us/webinar/register"]'
            },
            'generic': {
                'event_container': '.event, .webinar, .session, .card, article, .listing',
                'title': 'h1, h2, h3, h4, .title, .event-title, .webinar-title',
                'date': '.date, .datetime, .event-date, .webinar-date, time, .schedule',
                'description': '.description, .summary, .abstract, .content, p',
                'speaker': '.speaker, .presenter, .author, .host, .organizer',
                'registration': 'a[href*="register"], a[href*="signup"], .register, .sign-up'
            }
        }

    def collect_enhanced_webinars(self) -> Dict:
        """Main collection method that finds and scrapes individual webinars"""
        logger.info("Starting enhanced webinar collection with individual event extraction...")
        start_time = time.time()
        
        all_events = []
        search_stats = {
            'listing_pages_found': 0,
            'individual_events_extracted': 0,
            'events_with_dates': 0,
            'events_with_contact_info': 0,
            'google_results': 0,
            'serpapi_results': 0,
            'scraping_results': 0,
            'total_found': 0,
            'duplicates_removed': 0,
            'upcoming_only': 0
        }
        
        # Step 1: Find webinar listing pages using search APIs
        listing_pages = []
        
        if self.google_api_key and self.google_cse_id:
            logger.info("Finding webinar listing pages with Google Custom Search...")
            google_pages = self._find_listing_pages_google()
            listing_pages.extend(google_pages)
            search_stats['google_results'] = len(google_pages)
        
        if self.serpapi_key:
            logger.info("Finding webinar listing pages with SerpAPI...")
            serp_pages = self._find_listing_pages_serpapi()
            listing_pages.extend(serp_pages)
            search_stats['serpapi_results'] = len(serp_pages)
        
        # Add known webinar platforms
        listing_pages.extend(self._get_known_webinar_platforms())
        
        search_stats['listing_pages_found'] = len(listing_pages)
        logger.info(f"Found {len(listing_pages)} webinar listing pages to scrape")
        
        # Step 2: Scrape individual events from each listing page
        logger.info("Extracting individual webinars from listing pages...")
        
        # Use threading for faster scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self._scrape_listing_page, page): page 
                for page in listing_pages[:20]  # Limit to prevent overwhelming
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                page = future_to_url[future]
                try:
                    events = future.result()
                    all_events.extend(events)
                    logger.info(f"Extracted {len(events)} events from {page['url']}")
                except Exception as e:
                    logger.error(f"Error scraping {page['url']}: {e}")
        
        search_stats['individual_events_extracted'] = len(all_events)
        search_stats['total_found'] = len(all_events)
        
        # Step 3: Process and enhance the events
        logger.info("Processing and enhancing extracted events...")
        
        # Count events with dates and contact info
        for event in all_events:
            if event.get('event_date'):
                search_stats['events_with_dates'] += 1
            if event.get('contact_email') or event.get('contact_phone') or event.get('organizer'):
                search_stats['events_with_contact_info'] += 1
        
        # Remove duplicates
        unique_events = self._deduplicate_events(all_events)
        search_stats['duplicates_removed'] = len(all_events) - len(unique_events)
        
        # Filter for upcoming events only
        upcoming_events = self._filter_upcoming_events(unique_events)
        search_stats['upcoming_only'] = len(upcoming_events)
        
        # Save to database
        saved_stats = self._save_enhanced_events_to_db(upcoming_events)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Enhanced collection completed: {len(upcoming_events)} individual webinars found")
        
        return {
            'events_found': len(upcoming_events),
            'events_new': saved_stats['new'],
            'events_updated': saved_stats['updated'],
            'execution_time': execution_time,
            'search_stats': search_stats
        }

    def _find_listing_pages_google(self) -> List[Dict]:
        """Find webinar listing pages using Google Custom Search"""
        pages = []
        
        for query in self.listing_page_queries[:8]:  # Limit queries
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.google_api_key,
                    'cx': self.google_cse_id,
                    'q': query,
                    'num': 10,
                    'dateRestrict': 'm1',  # Last month to current
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for item in data.get('items', []):
                    if self._is_webinar_listing_page(item):
                        pages.append({
                            'url': item['link'],
                            'title': item['title'],
                            'description': item.get('snippet', ''),
                            'source': 'google_search'
                        })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Google search error for query '{query}': {e}")
                continue
        
        return pages

    def _find_listing_pages_serpapi(self) -> List[Dict]:
        """Find webinar listing pages using SerpAPI"""
        pages = []
        
        for query in self.listing_page_queries[:5]:  # Limit for cost control
            try:
                url = "https://serpapi.com/search"
                params = {
                    'api_key': self.serpapi_key,
                    'engine': 'google',
                    'q': query,
                    'num': 10,
                    'tbs': 'qdr:m1'  # Last month
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                for result in data.get('organic_results', []):
                    if self._is_webinar_listing_page(result):
                        pages.append({
                            'url': result['link'],
                            'title': result['title'],
                            'description': result.get('snippet', ''),
                            'source': 'serpapi'
                        })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"SerpAPI error for query '{query}': {e}")
                continue
        
        return pages

    def _get_known_webinar_platforms(self) -> List[Dict]:
        """Get known webinar platform listing pages"""
        known_platforms = [
            {
                'url': 'https://www.brighttalk.com/search/?q=webinar&duration=upcoming',
                'title': 'BrightTalk Upcoming Webinars',
                'description': 'Upcoming webinars on BrightTalk platform',
                'source': 'known_platform'
            },
            {
                'url': 'https://www.eventbrite.com/d/online/webinar/',
                'title': 'Eventbrite Online Webinars',
                'description': 'Online webinars on Eventbrite',
                'source': 'known_platform'
            },
            {
                'url': 'https://www.meetup.com/find/?keywords=webinar&source=EVENTS',
                'title': 'Meetup Webinar Events',
                'description': 'Webinar events on Meetup',
                'source': 'known_platform'
            }
        ]
        
        return known_platforms

    def _is_webinar_listing_page(self, search_result: Dict) -> bool:
        """Check if search result is likely a webinar listing page"""
        title = search_result.get('title', '').lower()
        snippet = search_result.get('snippet', '').lower()
        url = search_result.get('link', '').lower()
        
        # Indicators of listing pages
        listing_indicators = [
            'upcoming webinars', 'webinar calendar', 'webinar schedule',
            'event calendar', 'upcoming events', 'webinar series',
            'training calendar', 'education events', 'virtual events'
        ]
        
        # Indicators of individual events (we want to avoid these in this step)
        individual_indicators = [
            'register now', 'join webinar', 'webinar registration',
            'single event', 'one-time webinar'
        ]
        
        text = title + ' ' + snippet + ' ' + url
        
        has_listing_indicators = any(indicator in text for indicator in listing_indicators)
        has_individual_indicators = any(indicator in text for indicator in individual_indicators)
        
        # Should have listing indicators but not be an individual event
        return has_listing_indicators and not has_individual_indicators

    def _scrape_listing_page(self, page: Dict) -> List[Dict]:
        """Scrape individual webinars from a listing page"""
        events = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(page['url'], headers=headers, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {page['url']}: {response.status_code}")
                return events
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Determine platform-specific selectors
            domain = urlparse(page['url']).netloc.lower()
            selectors = self._get_selectors_for_domain(domain)
            
            # Find event containers
            event_containers = soup.select(selectors['event_container'])
            
            logger.info(f"Found {len(event_containers)} potential events on {page['url']}")
            
            for container in event_containers[:20]:  # Limit per page
                event = self._extract_event_from_container(container, selectors, page)
                if event and self._is_valid_webinar_event(event):
                    events.append(event)
            
        except Exception as e:
            logger.error(f"Error scraping listing page {page['url']}: {e}")
        
        return events

    def _get_selectors_for_domain(self, domain: str) -> Dict:
        """Get CSS selectors based on the domain"""
        for platform_domain, selectors in self.platform_selectors.items():
            if platform_domain in domain:
                return selectors
        
        return self.platform_selectors['generic']

    def _extract_event_from_container(self, container, selectors: Dict, page: Dict) -> Optional[Dict]:
        """Extract event information from a container element"""
        try:
            # Extract title
            title_elem = container.select_one(selectors['title'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract description
            desc_elem = container.select_one(selectors['description'])
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract date and time
            date_elem = container.select_one(selectors['date'])
            date_text = date_elem.get_text(strip=True) if date_elem else ''
            
            # Also check for datetime attributes
            if date_elem and date_elem.get('datetime'):
                date_text += ' ' + date_elem.get('datetime')
            
            event_date = self._extract_enhanced_date(date_text + ' ' + title + ' ' + description)
            
            # Extract speaker/presenter information
            speaker_elem = container.select_one(selectors['speaker'])
            speaker = speaker_elem.get_text(strip=True) if speaker_elem else ''
            
            # Extract registration URL
            reg_elem = container.select_one(selectors['registration'])
            registration_url = ''
            if reg_elem:
                registration_url = reg_elem.get('href', '')
                if registration_url and not registration_url.startswith('http'):
                    registration_url = urljoin(page['url'], registration_url)
            
            # Extract contact information
            contact_info = self._extract_contact_information(container.get_text())
            
            # Determine platform
            platform = self._determine_platform_from_url(page['url'])
            
            # Extract topic category
            topic_category = self._extract_topic_category(title + ' ' + description)
            
            # Check if free
            is_free = self._is_free_event(title + ' ' + description + ' ' + container.get_text())
            
            event = {
                'title': self._clean_title(title),
                'description': description[:1000] if description else '',
                'event_date': event_date,
                'registration_url': registration_url or page['url'],
                'platform': platform,
                'topic_category': topic_category,
                'is_free': is_free,
                'speaker': speaker,
                'organizer': contact_info.get('organization', ''),
                'contact_email': contact_info.get('email', ''),
                'contact_phone': contact_info.get('phone', ''),
                'source_page': page['url'],
                'source': 'enhanced_scraping'
            }
            
            return event
            
        except Exception as e:
            logger.error(f"Error extracting event from container: {e}")
            return None

    def _extract_enhanced_date(self, text: str) -> Optional[str]:
        """Enhanced date extraction with multiple patterns and formats"""
        if not text:
            return None
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Try different date patterns
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    date_str = match if isinstance(match, str) else ' '.join(match)
                    
                    # Try to parse the date
                    parsed_date = self._parse_date_string(date_str)
                    if parsed_date and parsed_date > datetime.now():
                        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Try to find relative dates
        relative_date = self._parse_relative_date(text)
        if relative_date:
            return relative_date.strftime('%Y-%m-%d %H:%M:%S')
        
        return None

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats"""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y',
            '%B %d %Y', '%b %d %Y',
            '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M', '%m-%d-%Y %H:%M'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None

    def _parse_relative_date(self, text: str) -> Optional[datetime]:
        """Parse relative dates like 'tomorrow', 'next week', etc."""
        text_lower = text.lower()
        now = datetime.now()
        
        if 'today' in text_lower:
            return now
        elif 'tomorrow' in text_lower:
            return now + timedelta(days=1)
        elif 'next week' in text_lower:
            return now + timedelta(weeks=1)
        elif 'this week' in text_lower:
            return now + timedelta(days=3)  # Assume mid-week
        
        # Look for "in X days/weeks/months"
        relative_match = re.search(r'in\s+(\d+)\s+(days?|weeks?|months?)', text_lower)
        if relative_match:
            number = int(relative_match.group(1))
            unit = relative_match.group(2)
            
            if 'day' in unit:
                return now + timedelta(days=number)
            elif 'week' in unit:
                return now + timedelta(weeks=number)
            elif 'month' in unit:
                return now + timedelta(days=number * 30)
        
        return None

    def _extract_contact_information(self, text: str) -> Dict:
        """Extract contact information from text"""
        contact_info = {
            'email': '',
            'phone': '',
            'organization': ''
        }
        
        # Extract email
        for pattern in self.contact_patterns['email']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact_info['email'] = matches[0] if isinstance(matches[0], str) else matches[0][0]
                break
        
        # Extract phone
        for pattern in self.contact_patterns['phone']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    contact_info['phone'] = ''.join(matches[0])
                else:
                    contact_info['phone'] = matches[0]
                break
        
        # Extract organization
        for pattern in self.contact_patterns['organization']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact_info['organization'] = matches[0].strip()
                break
        
        return contact_info

    def _determine_platform_from_url(self, url: str) -> str:
        """Determine platform from URL"""
        domain = urlparse(url).netloc.lower()
        
        platform_mapping = {
            'brighttalk.com': 'BrightTalk',
            'on24.com': 'ON24',
            'linkedin.com': 'LinkedIn',
            'zoom.us': 'Zoom',
            'gotowebinar.com': 'GoToWebinar',
            'eventbrite.com': 'Eventbrite',
            'webex.com': 'Webex',
            'teams.microsoft.com': 'Microsoft Teams',
            'meetup.com': 'Meetup',
            'hopin.com': 'Hopin',
            'bigmarker.com': 'BigMarker'
        }
        
        for key, platform in platform_mapping.items():
            if key in domain:
                return platform
        
        return 'Other'

    def _extract_topic_category(self, text: str) -> str:
        """Extract topic category from text"""
        if not text:
            return 'general'
        
        text_lower = text.lower()
        
        categories = {
            'artificial-intelligence': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural network'],
            'cybersecurity': ['cybersecurity', 'cyber security', 'infosec', 'security', 'hacking', 'privacy', 'data protection'],
            'marketing': ['marketing', 'digital marketing', 'seo', 'social media', 'advertising', 'content marketing'],
            'data-science': ['data science', 'analytics', 'big data', 'data analysis', 'statistics', 'business intelligence'],
            'cloud-computing': ['cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'devops'],
            'leadership': ['leadership', 'management', 'executive', 'ceo', 'strategy', 'business strategy'],
            'healthcare': ['healthcare', 'medical', 'health', 'pharma', 'clinical', 'telemedicine'],
            'finance': ['finance', 'fintech', 'banking', 'investment', 'trading', 'cryptocurrency'],
            'education': ['education', 'training', 'learning', 'teaching', 'academic', 'university'],
            'technology': ['technology', 'tech', 'software', 'programming', 'development', 'innovation']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'general'

    def _is_free_event(self, text: str) -> bool:
        """Determine if event is free"""
        if not text:
            return False
        
        text_lower = text.lower()
        free_indicators = ['free', 'no cost', 'complimentary', 'no charge', 'at no cost', 'free registration']
        paid_indicators = ['$', 'price', 'cost', 'fee', 'paid', 'premium', 'purchase', 'buy']
        
        has_free = any(indicator in text_lower for indicator in free_indicators)
        has_paid = any(indicator in text_lower for indicator in paid_indicators)
        
        # If both indicators present, check which is more prominent
        if has_free and has_paid:
            free_count = sum(text_lower.count(indicator) for indicator in free_indicators)
            paid_count = sum(text_lower.count(indicator) for indicator in paid_indicators)
            return free_count > paid_count
        
        return has_free

    def _is_valid_webinar_event(self, event: Dict) -> bool:
        """Check if extracted event is a valid webinar"""
        if not event.get('title') or len(event['title']) < 10:
            return False
        
        title = event['title'].lower()
        description = event.get('description', '').lower()
        
        # Must contain webinar-related keywords
        webinar_keywords = [
            'webinar', 'webcast', 'online event', 'virtual event',
            'online seminar', 'digital event', 'live stream',
            'virtual conference', 'online workshop', 'training session'
        ]
        
        text = title + ' ' + description
        has_webinar_keywords = any(keyword in text for keyword in webinar_keywords)
        
        # Should not be generic listing pages
        generic_titles = [
            'webinars', 'events', 'upcoming webinars', 'webinar calendar',
            'event calendar', 'training calendar'
        ]
        
        is_generic = any(generic in title for generic in generic_titles)
        
        return has_webinar_keywords and not is_generic

    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """Remove duplicate events based on title and URL similarity"""
        unique_events = []
        seen_combinations = set()
        
        for event in events:
            # Create a unique identifier
            title = event.get('title', '').lower().strip()
            url = event.get('registration_url', '').lower().strip()
            date = event.get('event_date', '')
            
            # Normalize title
            normalized_title = re.sub(r'[^\w\s]', '', title)
            normalized_title = ' '.join(normalized_title.split())
            
            # Create identifier
            identifier = f"{normalized_title}|{url}|{date}"
            
            if identifier not in seen_combinations:
                unique_events.append(event)
                seen_combinations.add(identifier)
        
        return unique_events

    def _filter_upcoming_events(self, events: List[Dict]) -> List[Dict]:
        """Filter events to only include upcoming ones"""
        upcoming_events = []
        current_date = datetime.now()
        
        for event in events:
            event_date_str = event.get('event_date')
            
            if event_date_str:
                try:
                    event_date = datetime.strptime(event_date_str, '%Y-%m-%d %H:%M:%S')
                    # Include events up to 1 year in the future
                    if current_date <= event_date <= current_date + timedelta(days=365):
                        upcoming_events.append(event)
                except ValueError:
                    # If we can't parse the date, include it anyway
                    upcoming_events.append(event)
            else:
                # If no date, include it (might be upcoming)
                upcoming_events.append(event)
        
        return upcoming_events

    def _save_enhanced_events_to_db(self, events: List[Dict]) -> Dict:
        """Save enhanced events to database with contact information"""
        with self.db_lock:
            conn = sqlite3.connect('webinar_discovery.db')
            cursor = conn.cursor()
            
            # Add new columns if they don't exist
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN speaker TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN organizer TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN contact_email TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN contact_phone TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN source_page TEXT")
            except sqlite3.OperationalError:
                pass
            
            new_count = 0
            updated_count = 0
            
            for event in events:
                # Check if event already exists
                cursor.execute("""
                    SELECT id FROM events 
                    WHERE title = ? AND registration_url = ?
                """, (event['title'], event['registration_url']))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing event
                    cursor.execute("""
                        UPDATE events SET
                            description = ?, event_date = ?, platform = ?,
                            topic_category = ?, is_free = ?, speaker = ?,
                            organizer = ?, contact_email = ?, contact_phone = ?,
                            source_page = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        event['description'], event['event_date'], event['platform'],
                        event['topic_category'], event['is_free'], event.get('speaker', ''),
                        event.get('organizer', ''), event.get('contact_email', ''),
                        event.get('contact_phone', ''), event.get('source_page', ''),
                        existing[0]
                    ))
                    updated_count += 1
                else:
                    # Insert new event
                    cursor.execute("""
                        INSERT INTO events (
                            title, description, event_date, registration_url,
                            platform, topic_category, is_free, speaker,
                            organizer, contact_email, contact_phone, source_page
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event['title'], event['description'], event['event_date'],
                        event['registration_url'], event['platform'],
                        event['topic_category'], event['is_free'], event.get('speaker', ''),
                        event.get('organizer', ''), event.get('contact_email', ''),
                        event.get('contact_phone', ''), event.get('source_page', '')
                    ))
                    new_count += 1
            
            conn.commit()
            conn.close()
            
            return {'new': new_count, 'updated': updated_count}

    def _clean_title(self, title: str) -> str:
        """Clean and normalize title"""
        if not title:
            return ''
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['webinar:', 'webcast:', 'event:', 'live:', 'upcoming:']
        for prefix in prefixes_to_remove:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
        
        # Remove dates from titles (they should be in the date field)
        title = re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b', '', title)
        title = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', '', title, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        title = ' '.join(title.split())
        
        return title[:200]  # Limit length