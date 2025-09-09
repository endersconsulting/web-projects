# enhanced_search_collector.py
# Real webinar search implementation with multiple APIs and strategies

import requests
import json
import re
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging
import time
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class WebinarSearchCollector:
    """Enhanced webinar collector with real search capabilities"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.google_cse_id = os.environ.get('GOOGLE_CSE_ID')
        self.serpapi_key = os.environ.get('SERPAPI_KEY')
        
        # Search configurations
        self.search_queries = [
            # Time-based searches
            "upcoming webinars 2025",
            "webinar registration open 2025",
            "virtual events September 2025",
            "online conference October 2025",
            
            # Platform-specific searches
            'site:linkedin.com/events "webinar" "register"',
            'site:brighttalk.com "upcoming webcast"',
            'site:on24.com "register now" webinar',
            'site:zoom.us/webinar "upcoming"',
            'site:gotowebinar.com "register"',
            
            # Topic-specific searches
            "cybersecurity webinar 2025 register",
            "AI artificial intelligence webinar upcoming",
            "marketing webinar September October 2025",
            "data science webinar registration",
            "cloud computing webinar 2025",
            
            # Industry searches
            "business webinar upcoming registration",
            "technology webinar September 2025",
            "healthcare webinar register now",
            "finance webinar upcoming 2025"
        ]
        
        # Date patterns for parsing
        self.date_patterns = [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        ]
        
        # Keywords that indicate upcoming events
        self.upcoming_keywords = [
            'register now', 'registration open', 'upcoming', 'join us',
            'save the date', 'register today', 'sign up', 'reserve your spot',
            'coming soon', 'next week', 'this month', 'don\'t miss'
        ]
        
        # Keywords that indicate past events (to filter out)
        self.past_keywords = [
            'replay', 'recording', 'watch now', 'on-demand', 'archived',
            'missed', 'recap', 'highlights', 'summary'
        ]

    def collect_webinars(self) -> Dict:
        """Main collection method that orchestrates all search strategies"""
        logger.info("Starting comprehensive webinar collection...")
        start_time = time.time()
        
        all_events = []
        search_stats = {
            'google_results': 0,
            'serpapi_results': 0,
            'direct_scraping': 0,
            'total_found': 0,
            'duplicates_removed': 0,
            'upcoming_only': 0
        }
        
        # Strategy 1: Google Custom Search API
        if self.google_api_key and self.google_cse_id:
            logger.info("Using Google Custom Search API...")
            google_events = self._search_google_custom()
            all_events.extend(google_events)
            search_stats['google_results'] = len(google_events)
        
        # Strategy 2: SerpAPI (if available)
        if self.serpapi_key:
            logger.info("Using SerpAPI...")
            serp_events = self._search_serpapi()
            all_events.extend(serp_events)
            search_stats['serpapi_results'] = len(serp_events)
        
        # Strategy 3: Direct platform scraping
        logger.info("Direct platform scraping...")
        scraped_events = self._scrape_platforms()
        all_events.extend(scraped_events)
        search_stats['direct_scraping'] = len(scraped_events)
        
        # Process and clean results
        search_stats['total_found'] = len(all_events)
        
        # Remove duplicates
        unique_events = self._deduplicate_events(all_events)
        search_stats['duplicates_removed'] = len(all_events) - len(unique_events)
        
        # Filter for upcoming events only
        upcoming_events = self._filter_upcoming_events(unique_events)
        search_stats['upcoming_only'] = len(upcoming_events)
        
        # Save to database
        saved_stats = self._save_events_to_db(upcoming_events)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Collection completed: {len(upcoming_events)} upcoming events found")
        
        return {
            'events_found': len(upcoming_events),
            'events_new': saved_stats['new'],
            'events_updated': saved_stats['updated'],
            'execution_time': execution_time,
            'search_stats': search_stats
        }

    def _search_google_custom(self) -> List[Dict]:
        """Search using Google Custom Search API"""
        events = []
        
        for query in self.search_queries[:10]:  # Limit to avoid quota issues
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.google_api_key,
                    'cx': self.google_cse_id,
                    'q': query,
                    'num': 10,
                    'dateRestrict': 'm3',  # Last 3 months to current
                    'sort': 'date'
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for item in data.get('items', []):
                    event = self._parse_search_result(item)
                    if event and self._is_likely_webinar(event):
                        events.append(event)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Google search error for query '{query}': {e}")
                continue
        
        return events

    def _search_serpapi(self) -> List[Dict]:
        """Search using SerpAPI"""
        events = []
        
        for query in self.search_queries[:5]:  # Limit for cost control
            try:
                url = "https://serpapi.com/search"
                params = {
                    'api_key': self.serpapi_key,
                    'engine': 'google',
                    'q': query,
                    'num': 10,
                    'tbs': 'qdr:m3'  # Last 3 months
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                for result in data.get('organic_results', []):
                    event = self._parse_search_result(result)
                    if event and self._is_likely_webinar(event):
                        events.append(event)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"SerpAPI error for query '{query}': {e}")
                continue
        
        return events

    def _scrape_platforms(self) -> List[Dict]:
        """Direct scraping of known webinar platforms"""
        events = []
        
        # Platform-specific scrapers
        scrapers = [
            self._scrape_brighttalk,
            self._scrape_linkedin_events,
            self._scrape_eventbrite,
        ]
        
        for scraper in scrapers:
            try:
                platform_events = scraper()
                events.extend(platform_events)
            except Exception as e:
                logger.error(f"Scraper error: {e}")
                continue
        
        return events

    def _scrape_brighttalk(self) -> List[Dict]:
        """Scrape BrightTalk for upcoming webinars"""
        events = []
        
        try:
            # BrightTalk upcoming events page
            url = "https://www.brighttalk.com/search/?q=webinar&duration=upcoming"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse BrightTalk event cards
                event_cards = soup.find_all('div', class_=['event-card', 'webinar-card'])
                
                for card in event_cards:
                    event = self._parse_brighttalk_card(card)
                    if event:
                        events.append(event)
        
        except Exception as e:
            logger.error(f"BrightTalk scraping error: {e}")
        
        return events

    def _scrape_linkedin_events(self) -> List[Dict]:
        """Scrape LinkedIn events (limited due to authentication requirements)"""
        events = []
        
        # LinkedIn requires authentication, so we'll use search results instead
        # This is a placeholder for when LinkedIn API access is available
        
        return events

    def _scrape_eventbrite(self) -> List[Dict]:
        """Scrape Eventbrite for webinars"""
        events = []
        
        try:
            # Eventbrite search for webinars
            url = "https://www.eventbrite.com/d/online/webinar/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse Eventbrite event cards
                event_cards = soup.find_all('div', class_=['event-card', 'search-event-card'])
                
                for card in event_cards:
                    event = self._parse_eventbrite_card(card)
                    if event:
                        events.append(event)
        
        except Exception as e:
            logger.error(f"Eventbrite scraping error: {e}")
        
        return events

    def _parse_search_result(self, result: Dict) -> Optional[Dict]:
        """Parse a search result into event data"""
        try:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            
            # Extract date from title or snippet
            event_date = self._extract_date(title + ' ' + snippet)
            
            # Determine platform from URL
            platform = self._determine_platform(link)
            
            # Extract topic category
            topic_category = self._extract_topic_category(title + ' ' + snippet)
            
            # Check if it's free
            is_free = self._is_free_event(title + ' ' + snippet)
            
            return {
                'title': self._clean_title(title),
                'description': snippet[:500] if snippet else '',
                'event_date': event_date,
                'registration_url': link,
                'platform': platform,
                'topic_category': topic_category,
                'is_free': is_free,
                'source': 'search'
            }
            
        except Exception as e:
            logger.error(f"Error parsing search result: {e}")
            return None

    def _parse_brighttalk_card(self, card) -> Optional[Dict]:
        """Parse a BrightTalk event card"""
        try:
            title_elem = card.find(['h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            desc_elem = card.find('p', class_=['description', 'summary'])
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            link_elem = card.find('a', href=True)
            link = link_elem['href'] if link_elem else ''
            if link and not link.startswith('http'):
                link = 'https://www.brighttalk.com' + link
            
            date_elem = card.find(['time', 'span'], class_=['date', 'datetime'])
            event_date = self._extract_date(date_elem.get_text() if date_elem else '')
            
            return {
                'title': self._clean_title(title),
                'description': description[:500],
                'event_date': event_date,
                'registration_url': link,
                'platform': 'BrightTalk',
                'topic_category': self._extract_topic_category(title + ' ' + description),
                'is_free': self._is_free_event(title + ' ' + description),
                'source': 'brighttalk_scrape'
            }
            
        except Exception as e:
            logger.error(f"Error parsing BrightTalk card: {e}")
            return None

    def _parse_eventbrite_card(self, card) -> Optional[Dict]:
        """Parse an Eventbrite event card"""
        try:
            title_elem = card.find(['h3', 'h2', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            desc_elem = card.find('p', class_=['event-description', 'summary'])
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            link_elem = card.find('a', href=True)
            link = link_elem['href'] if link_elem else ''
            
            date_elem = card.find(['time', 'span'], class_=['date', 'datetime'])
            event_date = self._extract_date(date_elem.get_text() if date_elem else '')
            
            # Check for free indicator
            price_elem = card.find(['span', 'div'], class_=['price', 'cost'])
            is_free = 'free' in (price_elem.get_text().lower() if price_elem else '')
            
            return {
                'title': self._clean_title(title),
                'description': description[:500],
                'event_date': event_date,
                'registration_url': link,
                'platform': 'Eventbrite',
                'topic_category': self._extract_topic_category(title + ' ' + description),
                'is_free': is_free,
                'source': 'eventbrite_scrape'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Eventbrite card: {e}")
            return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text using various patterns"""
        if not text:
            return None
            
        # Try different date patterns
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Try to parse the first match
                    date_str = matches[0] if isinstance(matches[0], str) else ' '.join(matches[0])
                    
                    # Try different parsing formats
                    for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%d %B %Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            # Only return future dates
                            if parsed_date > datetime.now():
                                return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            continue
                            
                except Exception:
                    continue
        
        return None

    def _determine_platform(self, url: str) -> str:
        """Determine platform from URL"""
        if not url:
            return 'Unknown'
            
        domain = urlparse(url).netloc.lower()
        
        platform_mapping = {
            'brighttalk.com': 'BrightTalk',
            'on24.com': 'ON24',
            'linkedin.com': 'LinkedIn',
            'zoom.us': 'Zoom',
            'gotowebinar.com': 'GoToWebinar',
            'eventbrite.com': 'Eventbrite',
            'webex.com': 'Webex',
            'teams.microsoft.com': 'Microsoft Teams'
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
            'artificial-intelligence': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning'],
            'cybersecurity': ['cybersecurity', 'cyber security', 'infosec', 'security', 'hacking', 'privacy'],
            'marketing': ['marketing', 'digital marketing', 'seo', 'social media', 'advertising'],
            'data-science': ['data science', 'analytics', 'big data', 'data analysis', 'statistics'],
            'cloud-computing': ['cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker'],
            'leadership': ['leadership', 'management', 'executive', 'ceo', 'strategy'],
            'healthcare': ['healthcare', 'medical', 'health', 'pharma', 'clinical'],
            'finance': ['finance', 'fintech', 'banking', 'investment', 'trading']
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
        free_indicators = ['free', 'no cost', 'complimentary', 'no charge', 'at no cost']
        paid_indicators = ['$', 'price', 'cost', 'fee', 'paid', 'premium']
        
        has_free = any(indicator in text_lower for indicator in free_indicators)
        has_paid = any(indicator in text_lower for indicator in paid_indicators)
        
        # If both indicators present, default to paid
        if has_free and not has_paid:
            return True
        
        return False

    def _is_likely_webinar(self, event: Dict) -> bool:
        """Check if event is likely a webinar"""
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        text = title + ' ' + description
        
        webinar_keywords = [
            'webinar', 'webcast', 'online event', 'virtual event',
            'online seminar', 'digital event', 'live stream',
            'virtual conference', 'online workshop'
        ]
        
        # Must contain webinar-related keywords
        has_webinar_keywords = any(keyword in text for keyword in webinar_keywords)
        
        # Should contain upcoming indicators
        has_upcoming = any(keyword in text for keyword in self.upcoming_keywords)
        
        # Should not contain past event indicators
        has_past = any(keyword in text for keyword in self.past_keywords)
        
        return has_webinar_keywords and (has_upcoming or not has_past)

    def _clean_title(self, title: str) -> str:
        """Clean and normalize title"""
        if not title:
            return ''
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['webinar:', 'webcast:', 'event:', 'live:']
        for prefix in prefixes_to_remove:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
        
        return title[:200]  # Limit length

    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """Remove duplicate events based on title and URL similarity"""
        unique_events = []
        seen_titles = set()
        seen_urls = set()
        
        for event in events:
            title = event.get('title', '').lower().strip()
            url = event.get('registration_url', '').lower().strip()
            
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', title)
            normalized_title = ' '.join(normalized_title.split())
            
            # Check for duplicates
            is_duplicate = False
            
            if normalized_title in seen_titles or url in seen_urls:
                is_duplicate = True
            
            # Check for similar titles (fuzzy matching)
            for seen_title in seen_titles:
                if self._titles_similar(normalized_title, seen_title):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_events.append(event)
                seen_titles.add(normalized_title)
                if url:
                    seen_urls.add(url)
        
        return unique_events

    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two titles are similar using simple word overlap"""
        if not title1 or not title2:
            return False
        
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold

    def _filter_upcoming_events(self, events: List[Dict]) -> List[Dict]:
        """Filter events to only include upcoming ones"""
        upcoming_events = []
        current_date = datetime.now()
        
        for event in events:
            event_date_str = event.get('event_date')
            
            if event_date_str:
                try:
                    event_date = datetime.strptime(event_date_str, '%Y-%m-%d %H:%M:%S')
                    if event_date > current_date:
                        upcoming_events.append(event)
                except ValueError:
                    # If we can't parse the date, include it anyway
                    upcoming_events.append(event)
            else:
                # If no date, include it (might be upcoming)
                upcoming_events.append(event)
        
        return upcoming_events

    def _save_events_to_db(self, events: List[Dict]) -> Dict:
        """Save events to database"""
        conn = sqlite3.connect('webinar_discovery.db')
        cursor = conn.cursor()
        
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
                        topic_category = ?, is_free = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    event['description'], event['event_date'], event['platform'],
                    event['topic_category'], event['is_free'], existing[0]
                ))
                updated_count += 1
            else:
                # Insert new event
                cursor.execute("""
                    INSERT INTO events (
                        title, description, event_date, registration_url,
                        platform, topic_category, is_free
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['title'], event['description'], event['event_date'],
                    event['registration_url'], event['platform'],
                    event['topic_category'], event['is_free']
                ))
                new_count += 1
        
        conn.commit()
        conn.close()
        
        return {'new': new_count, 'updated': updated_count}