# advanced_contact_discovery.py
# Advanced Contact Discovery System for Webinar Organizers and Speakers
# This system finds decision makers, organizers, and speakers for webinar follow-up

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

class AdvancedContactDiscovery:
    """Advanced system to discover webinar organizers, speakers, and decision makers"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.google_cse_id = os.environ.get('GOOGLE_CSE_ID')
        self.serpapi_key = os.environ.get('SERPAPI_KEY')
        
        # Thread safety
        self.db_lock = Lock()
        
        # Contact discovery strategies
        self.contact_strategies = [
            'about_page_analysis',
            'team_page_discovery',
            'speaker_bio_extraction',
            'social_media_profiles',
            'press_contact_search',
            'linkedin_company_search',
            'domain_whois_lookup'
        ]
        
        # Decision maker titles and roles
        self.decision_maker_titles = [
            # C-Level
            'ceo', 'chief executive officer', 'president', 'founder',
            'cto', 'chief technology officer', 'chief technical officer',
            'cmo', 'chief marketing officer', 'chief marketing',
            'coo', 'chief operating officer', 'chief operations',
            
            # VP Level
            'vp', 'vice president', 'vice-president',
            'vp marketing', 'vp sales', 'vp business development',
            'vp events', 'vp education', 'vp training',
            
            # Director Level
            'director', 'director of marketing', 'marketing director',
            'director of events', 'events director', 'event director',
            'director of education', 'education director',
            'director of training', 'training director',
            'director of business development', 'bd director',
            
            # Manager Level
            'marketing manager', 'events manager', 'event manager',
            'program manager', 'training manager', 'education manager',
            'webinar manager', 'digital marketing manager',
            'content marketing manager', 'demand generation manager',
            
            # Specialist Roles
            'webinar coordinator', 'event coordinator', 'events coordinator',
            'marketing coordinator', 'program coordinator',
            'webinar specialist', 'events specialist', 'marketing specialist',
            'demand generation specialist', 'digital marketing specialist'
        ]
        
        # Contact information patterns (enhanced)
        self.enhanced_contact_patterns = {
            'email': [
                # Standard email patterns
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                
                # Contact-specific patterns
                r'contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'reach out[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'inquiries[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                
                # Role-specific emails
                r'marketing@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'events@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'info@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'hello@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'contact@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'sales@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'partnerships@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'business@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            
            'phone': [
                # US/International phone patterns
                r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                r'\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                r'\+[0-9]{1,3}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}',
                
                # Context-specific phone patterns
                r'phone[:\s]*(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',
                r'call[:\s]*(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',
                r'tel[:\s]*(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',
            ],
            
            'linkedin': [
                r'linkedin\.com/in/([a-zA-Z0-9-]+)',
                r'linkedin\.com/company/([a-zA-Z0-9-]+)',
                r'linkedin\.com/pub/([a-zA-Z0-9-]+)',
            ],
            
            'twitter': [
                r'twitter\.com/([a-zA-Z0-9_]+)',
                r'@([a-zA-Z0-9_]+)',
            ]
        }
        
        # Company/organization patterns
        self.organization_patterns = [
            r'hosted by[:\s]*([^,\n\.]{10,100})',
            r'presented by[:\s]*([^,\n\.]{10,100})',
            r'organized by[:\s]*([^,\n\.]{10,100})',
            r'sponsored by[:\s]*([^,\n\.]{10,100})',
            r'brought to you by[:\s]*([^,\n\.]{10,100})',
            r'in partnership with[:\s]*([^,\n\.]{10,100})',
            r'©\s*([^,\n\.]{5,50})',  # Copyright notices
            r'copyright[:\s]*([^,\n\.]{5,50})',
        ]
        
        # Page types to search for contacts
        self.contact_page_types = [
            '/about', '/about-us', '/team', '/staff', '/people',
            '/contact', '/contact-us', '/get-in-touch',
            '/leadership', '/management', '/executives',
            '/speakers', '/presenters', '/faculty',
            '/press', '/media', '/news',
            '/partnerships', '/business-development',
            '/events', '/webinars', '/training'
        ]

    def discover_webinar_contacts(self, event_id: int) -> Dict:
        """Main method to discover contacts for a specific webinar event"""
        logger.info(f"Starting contact discovery for event {event_id}")
        
        # Get event details
        event = self._get_event_details(event_id)
        if not event:
            return {'error': 'Event not found'}
        
        contacts_found = {
            'event_id': event_id,
            'event_title': event['title'],
            'organization': '',
            'decision_makers': [],
            'speakers': [],
            'general_contacts': [],
            'social_profiles': [],
            'discovery_methods': [],
            'confidence_score': 0
        }
        
        # Strategy 1: Analyze the registration/source page
        if event.get('registration_url'):
            logger.info(f"Analyzing registration page: {event['registration_url']}")
            page_contacts = self._analyze_registration_page(event['registration_url'])
            self._merge_contacts(contacts_found, page_contacts)
            contacts_found['discovery_methods'].append('registration_page_analysis')
        
        # Strategy 2: Find and analyze company pages
        if event.get('source_page'):
            logger.info(f"Analyzing source page: {event['source_page']}")
            company_contacts = self._discover_company_contacts(event['source_page'])
            self._merge_contacts(contacts_found, company_contacts)
            contacts_found['discovery_methods'].append('company_page_analysis')
        
        # Strategy 3: Search for specific event organizers
        if event.get('title'):
            logger.info(f"Searching for event organizers: {event['title']}")
            organizer_contacts = self._search_event_organizers(event['title'])
            self._merge_contacts(contacts_found, organizer_contacts)
            contacts_found['discovery_methods'].append('organizer_search')
        
        # Strategy 4: LinkedIn company search
        domain = self._extract_domain(event.get('registration_url', ''))
        if domain:
            logger.info(f"Searching LinkedIn for company: {domain}")
            linkedin_contacts = self._search_linkedin_company(domain)
            self._merge_contacts(contacts_found, linkedin_contacts)
            contacts_found['discovery_methods'].append('linkedin_search')
        
        # Calculate confidence score
        contacts_found['confidence_score'] = self._calculate_confidence_score(contacts_found)
        
        # Save to database
        self._save_contacts_to_db(contacts_found)
        
        logger.info(f"Contact discovery completed for event {event_id}. Found {len(contacts_found['decision_makers'])} decision makers, {len(contacts_found['speakers'])} speakers")
        
        return contacts_found

    def _get_event_details(self, event_id: int) -> Optional[Dict]:
        """Get event details from database"""
        with self.db_lock:
            conn = sqlite3.connect('webinar_discovery.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            event = cursor.fetchone()
            
            conn.close()
            
            return dict(event) if event else None

    def _analyze_registration_page(self, url: str) -> Dict:
        """Analyze the registration page for contact information"""
        contacts = {
            'organization': '',
            'decision_makers': [],
            'speakers': [],
            'general_contacts': [],
            'social_profiles': []
        }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return contacts
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract organization name
            contacts['organization'] = self._extract_organization_name(soup, url)
            
            # Find contact information
            emails = self._extract_emails(page_text)
            phones = self._extract_phones(page_text)
            
            # Categorize contacts by context
            for email in emails:
                contact_info = {
                    'email': email,
                    'name': '',
                    'title': '',
                    'confidence': 0.5
                }
                
                # Try to find associated name and title
                name_title = self._find_name_and_title_near_email(soup, email)
                if name_title:
                    contact_info.update(name_title)
                    contact_info['confidence'] = 0.8
                
                # Categorize by email type
                if self._is_decision_maker_email(email, contact_info.get('title', '')):
                    contacts['decision_makers'].append(contact_info)
                elif self._is_speaker_email(email, contact_info.get('title', '')):
                    contacts['speakers'].append(contact_info)
                else:
                    contacts['general_contacts'].append(contact_info)
            
            # Find social media profiles
            contacts['social_profiles'] = self._extract_social_profiles(page_text)
            
            # Look for additional contact pages
            additional_contacts = self._find_additional_contact_pages(soup, url)
            self._merge_contacts(contacts, additional_contacts)
            
        except Exception as e:
            logger.error(f"Error analyzing registration page {url}: {e}")
        
        return contacts

    def _discover_company_contacts(self, source_url: str) -> Dict:
        """Discover contacts from company website"""
        contacts = {
            'organization': '',
            'decision_makers': [],
            'speakers': [],
            'general_contacts': [],
            'social_profiles': []
        }
        
        domain = self._extract_domain(source_url)
        if not domain:
            return contacts
        
        # Try different contact page URLs
        contact_pages = [
            f"https://{domain}{page_type}"
            for page_type in self.contact_page_types
        ]
        
        for contact_url in contact_pages[:5]:  # Limit to prevent overwhelming
            try:
                page_contacts = self._analyze_contact_page(contact_url)
                self._merge_contacts(contacts, page_contacts)
                time.sleep(1)  # Be respectful
            except Exception as e:
                logger.debug(f"Could not access {contact_url}: {e}")
                continue
        
        return contacts

    def _analyze_contact_page(self, url: str) -> Dict:
        """Analyze a specific contact page"""
        contacts = {
            'organization': '',
            'decision_makers': [],
            'speakers': [],
            'general_contacts': [],
            'social_profiles': []
        }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return contacts
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for team/staff sections
            team_sections = soup.find_all(['div', 'section'], class_=re.compile(r'team|staff|people|leadership|management', re.I))
            
            for section in team_sections:
                section_contacts = self._extract_team_contacts(section)
                self._merge_contacts(contacts, section_contacts)
            
            # Look for individual contact cards
            contact_cards = soup.find_all(['div', 'article'], class_=re.compile(r'person|member|contact|bio', re.I))
            
            for card in contact_cards:
                card_contact = self._extract_contact_card_info(card)
                if card_contact:
                    if self._is_decision_maker_title(card_contact.get('title', '')):
                        contacts['decision_makers'].append(card_contact)
                    else:
                        contacts['general_contacts'].append(card_contact)
            
        except Exception as e:
            logger.debug(f"Error analyzing contact page {url}: {e}")
        
        return contacts

    def _search_event_organizers(self, event_title: str) -> Dict:
        """Search for event organizers using search APIs"""
        contacts = {
            'organization': '',
            'decision_makers': [],
            'speakers': [],
            'general_contacts': [],
            'social_profiles': []
        }
        
        if not self.google_api_key:
            return contacts
        
        # Create search queries
        search_queries = [
            f'"{event_title}" organizer contact',
            f'"{event_title}" speaker contact',
            f'"{event_title}" host contact email',
            f'"{event_title}" event manager',
        ]
        
        for query in search_queries[:2]:  # Limit queries
            try:
                search_results = self._google_search(query)
                for result in search_results[:3]:  # Top 3 results
                    result_contacts = self._analyze_search_result(result)
                    self._merge_contacts(contacts, result_contacts)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error searching for organizers with query '{query}': {e}")
        
        return contacts

    def _search_linkedin_company(self, domain: str) -> Dict:
        """Search for LinkedIn company profiles and employees"""
        contacts = {
            'organization': '',
            'decision_makers': [],
            'speakers': [],
            'general_contacts': [],
            'social_profiles': []
        }
        
        if not self.google_api_key:
            return contacts
        
        # Search for LinkedIn company page
        company_query = f'site:linkedin.com/company {domain}'
        
        try:
            search_results = self._google_search(company_query)
            for result in search_results[:2]:
                if 'linkedin.com/company' in result.get('link', ''):
                    company_name = self._extract_company_name_from_linkedin(result)
                    if company_name:
                        contacts['organization'] = company_name
                    
                    # Search for employees
                    employee_contacts = self._search_linkedin_employees(company_name, domain)
                    self._merge_contacts(contacts, employee_contacts)
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn for company {domain}: {e}")
        
        return contacts

    def _search_linkedin_employees(self, company_name: str, domain: str) -> Dict:
        """Search for LinkedIn employee profiles"""
        contacts = {
            'decision_makers': [],
            'general_contacts': []
        }
        
        # Search for employees with decision-maker titles
        for title in ['marketing director', 'events manager', 'vp marketing'][:3]:
            query = f'site:linkedin.com/in "{company_name}" "{title}"'
            
            try:
                search_results = self._google_search(query)
                for result in search_results[:2]:
                    if 'linkedin.com/in' in result.get('link', ''):
                        contact = {
                            'name': self._extract_name_from_linkedin_profile(result),
                            'title': title,
                            'linkedin_url': result.get('link', ''),
                            'company': company_name,
                            'confidence': 0.7
                        }
                        
                        if self._is_decision_maker_title(title):
                            contacts['decision_makers'].append(contact)
                        else:
                            contacts['general_contacts'].append(contact)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error searching LinkedIn employees: {e}")
        
        return contacts

    def _google_search(self, query: str) -> List[Dict]:
        """Perform Google search using Custom Search API"""
        if not self.google_api_key or not self.google_cse_id:
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Google search error for query '{query}': {e}")
            return []

    def _extract_organization_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract organization name from page"""
        # Try title tag
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # Remove common suffixes
            for suffix in [' - Webinar', ' | Webinar', ' Webinar', ' - Event', ' | Event']:
                title_text = title_text.replace(suffix, '')
            if len(title_text) < 100:
                return title_text.strip()
        
        # Try domain name
        domain = self._extract_domain(url)
        if domain:
            # Convert domain to company name
            company_name = domain.replace('.com', '').replace('.org', '').replace('.net', '')
            company_name = company_name.replace('-', ' ').replace('_', ' ')
            return company_name.title()
        
        return ''

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        emails = set()
        
        for pattern in self.enhanced_contact_patterns['email']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                email = match if isinstance(match, str) else match[0] if match else ''
                if email and '@' in email and '.' in email:
                    emails.add(email.lower())
        
        # Filter out common non-contact emails
        filtered_emails = []
        skip_patterns = ['noreply', 'no-reply', 'donotreply', 'unsubscribe', 'support@', 'help@']
        
        for email in emails:
            if not any(skip in email.lower() for skip in skip_patterns):
                filtered_emails.append(email)
        
        return filtered_emails

    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phones = set()
        
        for pattern in self.enhanced_contact_patterns['phone']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phone = ''.join(match)
                else:
                    phone = match
                
                # Clean and validate phone number
                phone = re.sub(r'[^\d+]', '', phone)
                if len(phone) >= 10:
                    phones.add(phone)
        
        return list(phones)

    def _extract_social_profiles(self, text: str) -> List[Dict]:
        """Extract social media profiles"""
        profiles = []
        
        # LinkedIn profiles
        for pattern in self.enhanced_contact_patterns['linkedin']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                profiles.append({
                    'platform': 'linkedin',
                    'url': f'https://linkedin.com/in/{match}' if 'linkedin.com' not in match else match,
                    'username': match
                })
        
        # Twitter profiles
        for pattern in self.enhanced_contact_patterns['twitter']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                profiles.append({
                    'platform': 'twitter',
                    'url': f'https://twitter.com/{match}' if 'twitter.com' not in match else match,
                    'username': match
                })
        
        return profiles

    def _find_name_and_title_near_email(self, soup: BeautifulSoup, email: str) -> Optional[Dict]:
        """Find name and title near an email address"""
        # Find the element containing the email
        email_elements = soup.find_all(text=re.compile(re.escape(email), re.IGNORECASE))
        
        for email_element in email_elements:
            parent = email_element.parent
            if parent:
                # Look in the same element and nearby elements
                context_text = parent.get_text()
                
                # Try to extract name and title from context
                name_title = self._parse_name_title_from_context(context_text, email)
                if name_title:
                    return name_title
        
        return None

    def _parse_name_title_from_context(self, context: str, email: str) -> Optional[Dict]:
        """Parse name and title from context text"""
        # Remove the email from context to avoid confusion
        context = context.replace(email, '')
        
        # Look for patterns like "John Smith, Marketing Director"
        name_title_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+),?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        matches = re.findall(name_title_pattern, context)
        
        for name, title in matches:
            if any(dm_title.lower() in title.lower() for dm_title in self.decision_maker_titles):
                return {
                    'name': name.strip(),
                    'title': title.strip(),
                    'confidence': 0.8
                }
        
        return None

    def _is_decision_maker_email(self, email: str, title: str) -> bool:
        """Check if email/title indicates a decision maker"""
        email_lower = email.lower()
        title_lower = title.lower()
        
        # Check email patterns
        dm_email_patterns = ['marketing@', 'events@', 'partnerships@', 'business@', 'sales@']
        if any(pattern in email_lower for pattern in dm_email_patterns):
            return True
        
        # Check title
        if any(dm_title.lower() in title_lower for dm_title in self.decision_maker_titles):
            return True
        
        return False

    def _is_speaker_email(self, email: str, title: str) -> bool:
        """Check if email/title indicates a speaker"""
        title_lower = title.lower()
        speaker_indicators = ['speaker', 'presenter', 'instructor', 'trainer', 'expert', 'consultant']
        
        return any(indicator in title_lower for indicator in speaker_indicators)

    def _is_decision_maker_title(self, title: str) -> bool:
        """Check if title indicates a decision maker"""
        title_lower = title.lower()
        return any(dm_title.lower() in title_lower for dm_title in self.decision_maker_titles)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ''

    def _merge_contacts(self, target: Dict, source: Dict):
        """Merge contact information from source into target"""
        if source.get('organization') and not target.get('organization'):
            target['organization'] = source['organization']
        
        for key in ['decision_makers', 'speakers', 'general_contacts', 'social_profiles']:
            if key in source:
                target[key].extend(source[key])

    def _calculate_confidence_score(self, contacts: Dict) -> float:
        """Calculate confidence score for contact discovery"""
        score = 0.0
        
        # Organization found
        if contacts.get('organization'):
            score += 0.2
        
        # Decision makers found
        dm_count = len(contacts.get('decision_makers', []))
        if dm_count > 0:
            score += min(0.4, dm_count * 0.2)
        
        # General contacts found
        gc_count = len(contacts.get('general_contacts', []))
        if gc_count > 0:
            score += min(0.2, gc_count * 0.1)
        
        # Social profiles found
        sp_count = len(contacts.get('social_profiles', []))
        if sp_count > 0:
            score += min(0.1, sp_count * 0.05)
        
        # Multiple discovery methods used
        method_count = len(contacts.get('discovery_methods', []))
        if method_count > 1:
            score += 0.1
        
        return min(1.0, score)

    def _save_contacts_to_db(self, contacts: Dict):
        """Save discovered contacts to database"""
        with self.db_lock:
            conn = sqlite3.connect('webinar_discovery.db')
            cursor = conn.cursor()
            
            # Create contacts table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    contact_type TEXT,
                    name TEXT,
                    title TEXT,
                    email TEXT,
                    phone TEXT,
                    linkedin_url TEXT,
                    company TEXT,
                    confidence REAL,
                    discovery_method TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            ''')
            
            # Create organizations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    organization_name TEXT,
                    confidence_score REAL,
                    discovery_methods TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            ''')
            
            event_id = contacts['event_id']
            
            # Save organization
            if contacts.get('organization'):
                cursor.execute('''
                    INSERT OR REPLACE INTO event_organizations 
                    (event_id, organization_name, confidence_score, discovery_methods)
                    VALUES (?, ?, ?, ?)
                ''', (
                    event_id,
                    contacts['organization'],
                    contacts['confidence_score'],
                    json.dumps(contacts['discovery_methods'])
                ))
            
            # Save contacts
            for contact_type in ['decision_makers', 'speakers', 'general_contacts']:
                for contact in contacts.get(contact_type, []):
                    cursor.execute('''
                        INSERT INTO event_contacts 
                        (event_id, contact_type, name, title, email, phone, linkedin_url, company, confidence, discovery_method)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_id,
                        contact_type,
                        contact.get('name', ''),
                        contact.get('title', ''),
                        contact.get('email', ''),
                        contact.get('phone', ''),
                        contact.get('linkedin_url', ''),
                        contact.get('company', contacts.get('organization', '')),
                        contact.get('confidence', 0.5),
                        ','.join(contacts['discovery_methods'])
                    ))
            
            conn.commit()
            conn.close()

    def bulk_discover_contacts(self, limit: int = 10) -> Dict:
        """Discover contacts for multiple events"""
        logger.info(f"Starting bulk contact discovery for up to {limit} events")
        
        # Get events that don't have contact discovery yet
        with self.db_lock:
            conn = sqlite3.connect('webinar_discovery.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.id, e.title, e.registration_url, e.source_page
                FROM events e
                LEFT JOIN event_contacts ec ON e.id = ec.event_id
                WHERE ec.event_id IS NULL
                AND (e.registration_url IS NOT NULL OR e.source_page IS NOT NULL)
                LIMIT ?
            ''', (limit,))
            
            events = cursor.fetchall()
            conn.close()
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'total_contacts_found': 0,
            'total_decision_makers': 0
        }
        
        for event in events:
            event_id, title, reg_url, source_url = event
            
            try:
                logger.info(f"Processing event {event_id}: {title}")
                contacts = self.discover_webinar_contacts(event_id)
                
                results['processed'] += 1
                
                if contacts.get('confidence_score', 0) > 0.3:
                    results['successful'] += 1
                    results['total_contacts_found'] += len(contacts.get('decision_makers', [])) + len(contacts.get('general_contacts', []))
                    results['total_decision_makers'] += len(contacts.get('decision_makers', []))
                else:
                    results['failed'] += 1
                
                # Be respectful with timing
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing event {event_id}: {e}")
                results['failed'] += 1
        
        logger.info(f"Bulk contact discovery completed: {results['successful']} successful, {results['failed']} failed")
        return results

    # Additional helper methods for specific platforms and contact extraction
    def _find_additional_contact_pages(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Find links to additional contact pages"""
        contacts = {'decision_makers': [], 'speakers': [], 'general_contacts': [], 'social_profiles': []}
        
        # Look for links to contact pages
        contact_links = soup.find_all('a', href=re.compile(r'(about|contact|team|staff|leadership)', re.I))
        
        for link in contact_links[:3]:  # Limit to prevent overwhelming
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                try:
                    additional_contacts = self._analyze_contact_page(full_url)
                    self._merge_contacts(contacts, additional_contacts)
                    time.sleep(1)
                except:
                    continue
        
        return contacts

    def _extract_team_contacts(self, section) -> Dict:
        """Extract contacts from team/staff sections"""
        contacts = {'decision_makers': [], 'speakers': [], 'general_contacts': []}
        
        # Look for individual team member elements
        members = section.find_all(['div', 'article', 'li'], class_=re.compile(r'member|person|staff|team', re.I))
        
        for member in members:
            contact = self._extract_contact_card_info(member)
            if contact:
                if self._is_decision_maker_title(contact.get('title', '')):
                    contacts['decision_makers'].append(contact)
                else:
                    contacts['general_contacts'].append(contact)
        
        return contacts

    def _extract_contact_card_info(self, card) -> Optional[Dict]:
        """Extract contact information from a contact card element"""
        contact = {
            'name': '',
            'title': '',
            'email': '',
            'phone': '',
            'linkedin_url': '',
            'confidence': 0.6
        }
        
        card_text = card.get_text()
        
        # Extract name (usually in h1, h2, h3, or strong tags)
        name_elem = card.find(['h1', 'h2', 'h3', 'h4', 'strong', '.name'])
        if name_elem:
            contact['name'] = name_elem.get_text().strip()
        
        # Extract title (usually after name or in specific class)
        title_elem = card.find(['p', 'span', '.title', '.position', '.role'])
        if title_elem:
            contact['title'] = title_elem.get_text().strip()
        
        # Extract email
        emails = self._extract_emails(card_text)
        if emails:
            contact['email'] = emails[0]
        
        # Extract LinkedIn
        linkedin_link = card.find('a', href=re.compile(r'linkedin\.com', re.I))
        if linkedin_link:
            contact['linkedin_url'] = linkedin_link.get('href')
        
        # Only return if we have at least name or email
        if contact['name'] or contact['email']:
            return contact
        
        return None

    def _analyze_search_result(self, result: Dict) -> Dict:
        """Analyze a search result for contact information"""
        contacts = {'decision_makers': [], 'speakers': [], 'general_contacts': [], 'social_profiles': []}
        
        # Extract information from snippet
        snippet = result.get('snippet', '')
        title = result.get('title', '')
        
        # Look for contact information in snippet
        emails = self._extract_emails(snippet + ' ' + title)
        
        for email in emails:
            contact = {
                'email': email,
                'name': '',
                'title': '',
                'confidence': 0.4,
                'source_url': result.get('link', '')
            }
            
            # Try to extract name/title from snippet
            name_title = self._parse_name_title_from_context(snippet, email)
            if name_title:
                contact.update(name_title)
                contact['confidence'] = 0.7
            
            if self._is_decision_maker_email(email, contact.get('title', '')):
                contacts['decision_makers'].append(contact)
            else:
                contacts['general_contacts'].append(contact)
        
        return contacts

    def _extract_company_name_from_linkedin(self, result: Dict) -> str:
        """Extract company name from LinkedIn search result"""
        title = result.get('title', '')
        
        # LinkedIn company pages usually have format "Company Name | LinkedIn"
        if '|' in title:
            company_name = title.split('|')[0].strip()
            return company_name
        
        return ''

    def _extract_name_from_linkedin_profile(self, result: Dict) -> str:
        """Extract person name from LinkedIn profile search result"""
        title = result.get('title', '')
        
        # LinkedIn profiles usually have format "Name - Title | LinkedIn"
        if '-' in title and '|' in title:
            name_part = title.split('-')[0].strip()
            return name_part
        
        return ''

