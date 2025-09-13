# app.py
# Enhanced Backend API with Advanced Contact Discovery for Webinar Follow-up
# This Flask app includes advanced contact discovery to find decision makers and organizers

from news_feed_backend import add_news_feed_routes

from flask import Flask, request, jsonify, session, render_template_string
from flask_cors import CORS
import hashlib
import os
from datetime import datetime, timedelta
import sqlite3
import json
import logging

# Import the enhanced search collector and contact discovery
# Note: These imports will work after you copy the files to your backend directory
try:
    from enhanced_webinar_scraper import EnhancedWebinarScraper
    from advanced_contact_discovery import AdvancedContactDiscovery
    CONTACT_DISCOVERY_AVAILABLE = True
except ImportError:
    # Fallback if contact discovery files aren't available yet
    CONTACT_DISCOVERY_AVAILABLE = False
    print("Contact discovery modules not found. Basic functionality will be available.")

# Initialize the Flask application
app = Flask(__name__)

add_news_feed_routes(app)

# Set a secret key for sessions (change this to a random secret key in production)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CORS Configuration ---
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",  # Development
            "https://endersconsulting.cloud",  # Production
            "https://www.endersconsulting.cloud"  # Production with www
        ]
    }
}, supports_credentials=True)

# --- Password Configuration ---
WEBINAR_TOOL_USERNAME = os.environ.get('WEBINAR_USERNAME', 'admin')
WEBINAR_TOOL_PASSWORD = os.environ.get('WEBINAR_PASSWORD', 'secure123')  # Change this!

# Initialize the enhanced search collector and contact discovery (if available)
if CONTACT_DISCOVERY_AVAILABLE:
    enhanced_scraper = EnhancedWebinarScraper()
    contact_discovery = AdvancedContactDiscovery()
else:
    enhanced_scraper = None
    contact_discovery = None

# Debug environment variables
print("=== Environment Variables Debug ===")
print(f"GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY', 'NOT SET')}")
print(f"GOOGLE_CSE_ID: {os.environ.get('GOOGLE_CSE_ID', 'NOT SET')}")
print(f"Contact Discovery Available: {CONTACT_DISCOVERY_AVAILABLE}")
print("===================================")

# --- Database Setup ---
def init_webinar_db():
    """Initialize the webinar database with enhanced schema including contact discovery"""
    conn = sqlite3.connect('webinar_discovery.db')
    cursor = conn.cursor()
    
    # Create events table with enhanced fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_date DATETIME,
            registration_deadline DATETIME,
            registration_url TEXT,
            platform TEXT,
            topic_category TEXT,
            is_free BOOLEAN DEFAULT 0,
            speaker TEXT,
            organizer TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            source_page TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create contact discovery tables
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
    
    # Create speakers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS speakers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            name TEXT,
            title TEXT,
            company TEXT,
            bio TEXT,
            email TEXT,
            linkedin_url TEXT,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    # Create collection_logs table with enhanced stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_type TEXT,
            events_found INTEGER DEFAULT 0,
            events_new INTEGER DEFAULT 0,
            events_updated INTEGER DEFAULT 0,
            execution_time REAL DEFAULT 0,
            status TEXT DEFAULT 'completed',
            search_stats TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_webinar_db()

# --- Authentication Helper Functions ---
def hash_password(password):
    """Hash a password for storing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against provided password"""
    return stored_password == hash_password(provided_password)

def is_authenticated():
    """Check if user is authenticated for webinar tool"""
    return session.get('webinar_authenticated', False)

def _safe_json_parse(json_string):
    """Safely parse JSON string, return None if invalid"""
    if not json_string:
        return None
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None

# --- Original Enders Consulting API Routes ---

@app.route('/api/ask', methods=['POST'])
def ask_agent():
    """
    Handles inquiries submitted by the user from the Next.js frontend.
    It processes the user's query and returns a JSON response.
    """
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided.'}), 400
    
    user_query = data.get('query', '').strip().lower()
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty.'}), 400
    
    # --- Simulated AI Agent Logic ---
    response_message = ""
    response_category = "success"
    
    if 'services' in user_query:
        response_message = "Enders Consulting offers a range of services including strategic planning, technology integration, and operational improvement. How can we help you specifically?"
    elif 'contact' in user_query:
        response_message = "You can contact us via email at contact@endersconsulting.cloud or call us at (555) 123-4567."
    elif 'about' in user_query:
        response_message = "Founded on the principles of innovation and excellence, Enders Consulting is dedicated to helping businesses navigate complex challenges and achieve sustainable growth."
    elif 'hello' in user_query or 'hi' in user_query:
        response_message = "Hello! Thank you for reaching out. How can I assist you today?"
    else:
        response_message = "Thank you for your inquiry. While I'm a simple AI, a human representative will review your question and get back to you shortly."
        response_category = "info"
    
    return jsonify({
        'message': response_message,
        'category': response_category
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'enders-consulting-api'})

# --- Enhanced Webinar Discovery Tool Routes ---

@app.route('/api/webinar-tool')
def webinar_tool_login():
    """Login page for webinar discovery tool"""
    if is_authenticated():
        return render_template_string(CONTACT_DISCOVERY_HTML)
    
    return render_template_string(LOGIN_HTML)

@app.route('/api/webinar-auth', methods=['POST'])
def webinar_authenticate():
    """Authenticate user for webinar tool"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No credentials provided'}), 400
    
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username == WEBINAR_TOOL_USERNAME and password == WEBINAR_TOOL_PASSWORD:
        session['webinar_authenticated'] = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=8)  # Session expires after 8 hours
        return jsonify({'success': True, 'message': 'Authentication successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/webinar-logout', methods=['POST'])
def webinar_logout():
    """Logout from webinar tool"""
    session.pop('webinar_authenticated', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/webinars/events', methods=['GET'])
def get_webinar_events():
    """Get webinar events with filtering and contact information"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    topic = request.args.get('topic', '')
    platform = request.args.get('platform', '')
    is_free = request.args.get('is_free', '')
    has_contact = request.args.get('has_contact', '')
    has_decision_makers = request.args.get('has_decision_makers', '')
    
    # Build SQL query
    conn = sqlite3.connect('webinar_discovery.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("(e.title LIKE ? OR e.description LIKE ? OR e.speaker LIKE ? OR e.organizer LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if topic:
        where_conditions.append("e.topic_category = ?")
        params.append(topic)
    
    if platform:
        where_conditions.append("e.platform = ?")
        params.append(platform)
    
    if is_free:
        where_conditions.append("e.is_free = ?")
        params.append(1 if is_free.lower() == 'true' else 0)
    
    if has_contact:
        where_conditions.append("(e.contact_email IS NOT NULL AND e.contact_email != '') OR (e.contact_phone IS NOT NULL AND e.contact_phone != '') OR (e.organizer IS NOT NULL AND e.organizer != '')")
    
    if has_decision_makers:
        where_conditions.append("EXISTS (SELECT 1 FROM event_contacts ec WHERE ec.event_id = e.id AND ec.contact_type = 'decision_makers')")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM events e WHERE {where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Get events with pagination
    offset = (page - 1) * per_page
    events_query = f"""
        SELECT e.*, 
               eo.organization_name,
               COUNT(DISTINCT CASE WHEN ec.contact_type = 'decision_makers' THEN ec.id END) as decision_maker_count,
               COUNT(DISTINCT ec.id) as total_contact_count
        FROM events e
        LEFT JOIN event_organizations eo ON e.id = eo.event_id
        LEFT JOIN event_contacts ec ON e.id = ec.event_id
        WHERE {where_clause}
        GROUP BY e.id
        ORDER BY e.event_date ASC, e.created_at DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(events_query, params + [per_page, offset])
    events = [dict(row) for row in cursor.fetchall()]
    
    # Get detailed contacts for each event
    for event in events:
        # Get decision makers
        cursor.execute("""
            SELECT * FROM event_contacts 
            WHERE event_id = ? AND contact_type = 'decision_makers'
            ORDER BY confidence DESC
        """, (event['id'],))
        event['decision_makers'] = [dict(row) for row in cursor.fetchall()]
        
        # Get all contacts
        cursor.execute("""
            SELECT * FROM event_contacts 
            WHERE event_id = ?
            ORDER BY contact_type, confidence DESC
        """, (event['id'],))
        event['all_contacts'] = [dict(row) for row in cursor.fetchall()]
        
        # Get speakers
        cursor.execute("SELECT * FROM speakers WHERE event_id = ?", (event['id'],))
        event['speakers'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate pagination info
    total_pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'status': 'success',
        'data': {
            'events': events,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
        }
    })

# --- Contact Discovery Routes ---

@app.route('/api/webinars/contacts/discover', methods=['POST'])
def discover_event_contacts():
    """Discover contacts for a specific event"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    if not CONTACT_DISCOVERY_AVAILABLE:
        return jsonify({'error': 'Contact discovery not available. Please deploy the contact discovery modules.'}), 503
    
    data = request.get_json()
    event_id = data.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Event ID required'}), 400
    
    try:
        logger.info(f"Starting contact discovery for event {event_id}")
        result = contact_discovery.discover_webinar_contacts(event_id)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Contact discovery error for event {event_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Contact discovery failed: {str(e)}'
        }), 500

@app.route('/api/webinars/contacts/bulk-discover', methods=['POST'])
def bulk_discover_contacts():
    """Discover contacts for multiple events"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    if not CONTACT_DISCOVERY_AVAILABLE:
        return jsonify({'error': 'Contact discovery not available. Please deploy the contact discovery modules.'}), 503
    
    data = request.get_json()
    limit = data.get('limit', 10)
    
    try:
        logger.info(f"Starting bulk contact discovery for up to {limit} events")
        result = contact_discovery.bulk_discover_contacts(limit)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Bulk contact discovery error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Bulk contact discovery failed: {str(e)}'
        }), 500

@app.route('/api/webinars/contacts/analytics', methods=['GET'])
def get_contact_analytics():
    """Get analytics about discovered contacts"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = sqlite3.connect('webinar_discovery.db')
    cursor = conn.cursor()
    
    # Get contact statistics
    cursor.execute("SELECT COUNT(DISTINCT event_id) as events_with_contacts FROM event_contacts")
    events_with_contacts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as total_contacts FROM event_contacts")
    total_contacts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as decision_makers FROM event_contacts WHERE contact_type = 'decision_makers'")
    decision_makers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as with_email FROM event_contacts WHERE email IS NOT NULL AND email != ''")
    contacts_with_email = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as with_linkedin FROM event_contacts WHERE linkedin_url IS NOT NULL AND linkedin_url != ''")
    contacts_with_linkedin = cursor.fetchone()[0]
    
    # Get contact types breakdown
    cursor.execute("""
        SELECT contact_type, COUNT(*) as count 
        FROM event_contacts 
        GROUP BY contact_type 
        ORDER BY count DESC
    """)
    contact_types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Get top titles for decision makers
    cursor.execute("""
        SELECT title, COUNT(*) as count 
        FROM event_contacts 
        WHERE contact_type = 'decision_makers' AND title IS NOT NULL AND title != ''
        GROUP BY title 
        ORDER BY count DESC
        LIMIT 10
    """)
    top_titles = [{'title': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Get organizations with most contacts
    cursor.execute("""
        SELECT company, COUNT(*) as contact_count
        FROM event_contacts 
        WHERE company IS NOT NULL AND company != ''
        GROUP BY company 
        ORDER BY contact_count DESC
        LIMIT 10
    """)
    top_organizations = [{'organization': row[0], 'contacts': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'data': {
            'summary': {
                'events_with_contacts': events_with_contacts,
                'total_contacts': total_contacts,
                'decision_makers': decision_makers,
                'contacts_with_email': contacts_with_email,
                'contacts_with_linkedin': contacts_with_linkedin
            },
            'contact_types': contact_types,
            'top_decision_maker_titles': top_titles,
            'top_organizations': top_organizations
        }
    })

@app.route('/api/webinars/contacts/export', methods=['GET'])
def export_contacts():
    """Export contacts for outreach"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    contact_type = request.args.get('type', 'decision_makers')
    format_type = request.args.get('format', 'json')
    
    conn = sqlite3.connect('webinar_discovery.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get contacts with event information
    cursor.execute("""
        SELECT 
            ec.*,
            e.title as event_title,
            e.event_date,
            e.platform,
            e.topic_category,
            e.registration_url,
            eo.organization_name
        FROM event_contacts ec
        JOIN events e ON ec.event_id = e.id
        LEFT JOIN event_organizations eo ON ec.event_id = eo.event_id
        WHERE ec.contact_type = ?
        ORDER BY ec.confidence DESC, e.event_date ASC
    """, (contact_type,))
    
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if format_type == 'csv':
        # Return CSV format for easy import into CRM systems
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'name', 'title', 'email', 'phone', 'linkedin_url', 'company',
            'event_title', 'event_date', 'platform', 'topic_category',
            'confidence', 'discovery_method'
        ])
        
        writer.writeheader()
        for contact in contacts:
            writer.writerow({
                'name': contact.get('name', ''),
                'title': contact.get('title', ''),
                'email': contact.get('email', ''),
                'phone': contact.get('phone', ''),
                'linkedin_url': contact.get('linkedin_url', ''),
                'company': contact.get('organization_name', contact.get('company', '')),
                'event_title': contact.get('event_title', ''),
                'event_date': contact.get('event_date', ''),
                'platform': contact.get('platform', ''),
                'topic_category': contact.get('topic_category', ''),
                'confidence': contact.get('confidence', ''),
                'discovery_method': contact.get('discovery_method', '')
            })
        
        csv_content = output.getvalue()
        output.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'format': 'csv',
                'content': csv_content,
                'count': len(contacts)
            }
        })
    
    else:
        # Return JSON format
        return jsonify({
            'status': 'success',
            'data': {
                'format': 'json',
                'contacts': contacts,
                'count': len(contacts)
            }
        })

# --- Enhanced Collection Routes ---

@app.route('/api/webinars/collect/enhanced', methods=['POST'])
def run_enhanced_webinar_collection():
    """Run ENHANCED webinar collection with individual event extraction"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    if not CONTACT_DISCOVERY_AVAILABLE:
        return jsonify({'error': 'Enhanced collection not available. Please deploy the enhanced scraper module.'}), 503
    
    logger.info("Starting ENHANCED webinar collection with individual event extraction...")
    
    try:
        # Use the enhanced search collector
        result = enhanced_scraper.collect_enhanced_webinars()
        
        # Log the collection
        conn = sqlite3.connect('webinar_discovery.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO collection_logs (
                collection_type, events_found, events_new, events_updated, 
                execution_time, search_stats
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'enhanced_scraping', 
            result['events_found'], 
            result['events_new'], 
            result['events_updated'],
            result['execution_time'],
            json.dumps(result['search_stats'])
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Enhanced collection completed: {result['events_new']} new, {result['events_updated']} updated")
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Enhanced collection error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Enhanced collection failed: {str(e)}'
        }), 500

@app.route('/api/webinars/analytics/enhanced', methods=['GET'])
def get_enhanced_webinar_analytics():
    """Get enhanced webinar analytics with contact information stats"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = sqlite3.connect('webinar_discovery.db')
    cursor = conn.cursor()
    
    # Get event statistics
    cursor.execute("SELECT COUNT(*) as total FROM events")
    total_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as upcoming FROM events WHERE event_date > datetime('now')")
    upcoming_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as free FROM events WHERE is_free = 1")
    free_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as with_dates FROM events WHERE event_date IS NOT NULL AND event_date != ''")
    events_with_dates = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as with_contact FROM events WHERE (contact_email IS NOT NULL AND contact_email != '') OR (contact_phone IS NOT NULL AND contact_phone != '') OR (organizer IS NOT NULL AND organizer != '')")
    events_with_contact = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as with_speakers FROM events WHERE speaker IS NOT NULL AND speaker != ''")
    events_with_speakers = cursor.fetchone()[0]
    
    # Get contact discovery statistics
    cursor.execute("SELECT COUNT(DISTINCT event_id) as events_with_discovered_contacts FROM event_contacts")
    events_with_discovered_contacts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as total_discovered_contacts FROM event_contacts")
    total_discovered_contacts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as discovered_decision_makers FROM event_contacts WHERE contact_type = 'decision_makers'")
    discovered_decision_makers = cursor.fetchone()[0]
    
    # Get platform breakdown
    cursor.execute("""
        SELECT platform, COUNT(*) as count 
        FROM events 
        GROUP BY platform 
        ORDER BY count DESC
    """)
    platform_stats = [{'platform': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Get topic breakdown
    cursor.execute("""
        SELECT topic_category, COUNT(*) as count 
        FROM events 
        GROUP BY topic_category 
        ORDER BY count DESC
    """)
    topic_stats = [{'topic': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'data': {
            'event_statistics': {
                'total_events': total_events,
                'upcoming_events': upcoming_events,
                'free_events': free_events,
                'events_with_dates': events_with_dates,
                'events_with_contact': events_with_contact,
                'events_with_speakers': events_with_speakers
            },
            'contact_discovery_statistics': {
                'events_with_discovered_contacts': events_with_discovered_contacts,
                'total_discovered_contacts': total_discovered_contacts,
                'discovered_decision_makers': discovered_decision_makers
            },
            'platform_breakdown': platform_stats,
            'topic_breakdown': topic_stats
        }
    })

@app.route('/api/webinars/collect/status', methods=['GET'])
def get_collection_status():
    """Get collection status"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = sqlite3.connect('webinar_discovery.db')
    cursor = conn.cursor()
    
    # Get last collection
    cursor.execute("""
        SELECT * FROM collection_logs 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    last_collection = cursor.fetchone()
    
    # Get API status
    api_status = {
        'google_api': bool(os.environ.get('GOOGLE_API_KEY') and os.environ.get('GOOGLE_CSE_ID')),
        'serpapi': bool(os.environ.get('SERPAPI_KEY')),
        'enhanced_scraping': CONTACT_DISCOVERY_AVAILABLE,
        'contact_discovery': CONTACT_DISCOVERY_AVAILABLE
    }
    
    conn.close()
    
    # Safe JSON parsing
    last_stats = None
    if last_collection and len(last_collection) > 6 and last_collection[-2]:
        last_stats = _safe_json_parse(last_collection[-2])
    
    return jsonify({
        'status': 'success',
        'data': {
            'summary': {
                'last_collection': last_collection[-1] if last_collection else None,
                'last_collection_stats': last_stats
            },
            'api_status': api_status
        }
    })

# --- HTML Templates ---

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Webinar Contact Discovery - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 450px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-header h1 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .login-header p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
        }
        
        .login-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        
        .back-link {
            text-align: center;
            margin-top: 1rem;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .features {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            font-size: 0.85rem;
        }
        
        .features h4 {
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .features ul {
            margin-left: 1rem;
            color: #666;
        }
        
        .features li {
            margin-bottom: 0.25rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🎯 Advanced Contact Discovery</h1>
            <p>Find decision makers & organizers for webinar follow-up</p>
        </div>
        
        <div class="features">
            <h4>🚀 Advanced Features</h4>
            <ul>
                <li>✅ Decision maker identification</li>
                <li>✅ Contact information extraction</li>
                <li>✅ LinkedIn profile discovery</li>
                <li>✅ Company organization mapping</li>
                <li>✅ Outreach-ready contact lists</li>
                <li>✅ CRM export capabilities</li>
            </ul>
        </div>
        
        <div id="error-message" style="display: none;" class="error"></div>
        
        <form id="login-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn" id="login-btn">Login</button>
        </form>
        
        <div class="back-link">
            <a href="https://endersconsulting.cloud">← Back to Enders Consulting</a>
        </div>
    </div>
    
    <script>
        document.getElementById('login-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('login-btn');
            const errorDiv = document.getElementById('error-message');
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            errorDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/webinar-auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    errorDiv.textContent = data.error || 'Login failed';
                    errorDiv.style.display = 'block';
                }
            } catch (error) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.style.display = 'block';
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Login';
            }
        });
    </script>
</body>
</html>
'''

CONTACT_DISCOVERY_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Webinar Contact Discovery - Enders Consulting</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-radius: 10px;
            text-align: center;
            position: relative;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .logout-btn {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }

        .controls {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .controls h2 {
            margin-bottom: 1rem;
            color: #333;
        }

        .control-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .control-item {
            flex: 1;
            min-width: 200px;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #555;
        }

        input, select, button {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }

        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 500;
            transition: transform 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .contact-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }

        .bulk-btn {
            background: linear-gradient(135deg, #fd7e14 0%, #e83e8c 100%);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }

        .events-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .events-header {
            background: #f8f9fa;
            padding: 1.5rem;
            border-bottom: 1px solid #eee;
        }

        .events-header h2 {
            margin-bottom: 0.5rem;
        }

        .event-card {
            padding: 1.5rem;
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
        }

        .event-card:hover {
            background-color: #f8f9fa;
        }

        .event-card:last-child {
            border-bottom: none;
        }

        .event-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }

        .event-meta {
            display: flex;
            gap: 1rem;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
        }

        .event-meta span {
            background: #e9ecef;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.85rem;
            color: #666;
        }

        .event-meta .platform {
            background: #667eea;
            color: white;
        }

        .event-meta .free {
            background: #28a745;
            color: white;
        }

        .event-meta .contact {
            background: #17a2b8;
            color: white;
        }

        .event-meta .decision-makers {
            background: #fd7e14;
            color: white;
        }

        .event-description {
            color: #666;
            margin-bottom: 1rem;
            line-height: 1.5;
        }

        .contact-section {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }

        .contact-section h4 {
            margin-bottom: 0.5rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .contact-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }

        .contact-card {
            background: white;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }

        .contact-card.decision-maker {
            border-left-color: #fd7e14;
        }

        .contact-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.25rem;
        }

        .contact-title {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

        .contact-details {
            font-size: 0.85rem;
            color: #666;
        }

        .contact-details a {
            color: #667eea;
            text-decoration: none;
        }

        .contact-details a:hover {
            text-decoration: underline;
        }

        .event-actions {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            width: auto;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.2s;
        }

        .btn-small:hover {
            background: #5a6fd8;
        }

        .btn-small.contact-btn {
            background: #28a745;
        }

        .btn-small.contact-btn:hover {
            background: #218838;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }

        .success {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }

        .info {
            background: #d1ecf1;
            color: #0c5460;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }

        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
            padding: 1rem;
        }

        .pagination button {
            width: auto;
            padding: 0.5rem 1rem;
            background: #f8f9fa;
            color: #333;
            border: 1px solid #ddd;
        }

        .pagination button.active {
            background: #667eea;
            color: white;
        }

        @media (max-width: 768px) {
            .control-group {
                flex-direction: column;
            }
            
            .event-meta {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .event-actions {
                flex-direction: column;
            }
            
            .contact-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <button class="logout-btn" onclick="logout()">Logout</button>
            <h1>🎯 Advanced Contact Discovery</h1>
            <p>Find decision makers and organizers for webinar follow-up opportunities</p>
        </div>

        <div class="controls">
            <h2>Contact Discovery & Search Controls</h2>
            
            <div class="control-group">
                <div class="control-item">
                    <label for="searchTerm">Search Term</label>
                    <input type="text" id="searchTerm" placeholder="e.g., AI, cybersecurity, marketing">
                </div>
                <div class="control-item">
                    <label for="topicFilter">Topic Category</label>
                    <select id="topicFilter">
                        <option value="">All Topics</option>
                        <option value="artificial-intelligence">Artificial Intelligence</option>
                        <option value="cybersecurity">Cybersecurity</option>
                        <option value="marketing">Marketing</option>
                        <option value="data-science">Data Science</option>
                        <option value="cloud-computing">Cloud Computing</option>
                        <option value="leadership">Leadership</option>
                        <option value="healthcare">Healthcare</option>
                        <option value="finance">Finance</option>
                        <option value="education">Education</option>
                        <option value="technology">Technology</option>
                    </select>
                </div>
                <div class="control-item">
                    <label for="platformFilter">Platform</label>
                    <select id="platformFilter">
                        <option value="">All Platforms</option>
                        <option value="BrightTalk">BrightTalk</option>
                        <option value="ON24">ON24</option>
                        <option value="LinkedIn">LinkedIn</option>
                        <option value="Zoom">Zoom</option>
                        <option value="GoToWebinar">GoToWebinar</option>
                        <option value="Eventbrite">Eventbrite</option>
                        <option value="Meetup">Meetup</option>
                    </select>
                </div>
                <div class="control-item">
                    <label for="contactFilter">Contact Discovery</label>
                    <select id="contactFilter">
                        <option value="">All Events</option>
                        <option value="true">With Decision Makers</option>
                    </select>
                </div>
            </div>

            <div class="control-group">
                <div class="control-item">
                    <button onclick="searchEvents()">Search Events</button>
                </div>
                <div class="control-item">
                    <button onclick="runEnhancedCollection()" id="enhancedCollectBtn">🚀 Run Enhanced Collection</button>
                </div>
                <div class="control-item">
                    <button onclick="bulkDiscoverContacts()" id="bulkContactBtn" class="bulk-btn">🎯 Bulk Contact Discovery</button>
                </div>
                <div class="control-item">
                    <button onclick="exportContacts()" class="contact-btn">📊 Export Contacts</button>
                </div>
            </div>
        </div>

        <div id="messageArea"></div>

        <div class="stats" id="statsContainer">
            <div class="stat-card">
                <div class="stat-number" id="totalEvents">-</div>
                <div class="stat-label">Total Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="eventsWithContacts">-</div>
                <div class="stat-label">With Discovered Contacts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalContacts">-</div>
                <div class="stat-label">Total Contacts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="decisionMakers">-</div>
                <div class="stat-label">Decision Makers</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="contactsWithEmail">-</div>
                <div class="stat-label">With Email</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="contactsWithLinkedIn">-</div>
                <div class="stat-label">With LinkedIn</div>
            </div>
        </div>

        <div class="events-container">
            <div class="events-header">
                <h2>Webinar Events with Contact Discovery</h2>
                <p>Advanced contact extraction for decision makers and organizers</p>
            </div>
            <div id="eventsContainer">
                <div class="loading">Click "Search Events" to view your existing webinar data, then "Bulk Contact Discovery" to find decision makers</div>
            </div>
            <div id="paginationContainer"></div>
        </div>
    </div>

    <script>
        let currentPage = 1;
        const perPage = 10;

        // Load initial stats and events
        document.addEventListener('DOMContentLoaded', function() {
            loadContactAnalytics();
            loadEnhancedStats();
            searchEvents(); // Load existing events immediately
        });

        async function logout() {
            try {
                await fetch('/api/webinar-logout', {
                    method: 'POST',
                    credentials: 'include'
                });
                window.location.reload();
            } catch (error) {
                console.error('Logout error:', error);
                window.location.reload();
            }
        }

        async function loadContactAnalytics() {
            try {
                const response = await fetch('/api/webinars/contacts/analytics', {
                    credentials: 'include'
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    const stats = data.data.summary;
                    document.getElementById('eventsWithContacts').textContent = stats.events_with_contacts;
                    document.getElementById('totalContacts').textContent = stats.total_contacts;
                    document.getElementById('decisionMakers').textContent = stats.decision_makers;
                    document.getElementById('contactsWithEmail').textContent = stats.contacts_with_email;
                    document.getElementById('contactsWithLinkedIn').textContent = stats.contacts_with_linkedin;
                }
            } catch (error) {
                console.error('Error loading contact analytics:', error);
            }
        }

        async function loadEnhancedStats() {
            try {
                const response = await fetch('/api/webinars/analytics/enhanced', {
                    credentials: 'include'
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    const stats = data.data;
                    document.getElementById('totalEvents').textContent = stats.event_statistics.total_events;
                }
            } catch (error) {
                console.error('Error loading enhanced stats:', error);
            }
        }

        async function searchEvents() {
            const searchTerm = document.getElementById('searchTerm').value;
            const topic = document.getElementById('topicFilter').value;
            const platform = document.getElementById('platformFilter').value;
            const hasDecisionMakers = document.getElementById('contactFilter').value;

            const params = new URLSearchParams({
                page: currentPage,
                per_page: perPage
            });

            if (searchTerm) params.append('search', searchTerm);
            if (topic) params.append('topic', topic);
            if (platform) params.append('platform', platform);
            if (hasDecisionMakers) params.append('has_decision_makers', hasDecisionMakers);

            try {
                showLoading();
                const response = await fetch(`/api/webinars/events?${params}`, {
                    credentials: 'include'
                });
                const data = await response.json();

                if (data.status === 'success') {
                    displayEventsWithContacts(data.data.events);
                    displayPagination(data.data.pagination);
                    clearMessage();
                } else {
                    showError('Failed to load events');
                }
            } catch (error) {
                showError('Error loading events: ' + error.message);
            }
        }

        async function runEnhancedCollection() {
            const collectBtn = document.getElementById('enhancedCollectBtn');
            collectBtn.disabled = true;
            collectBtn.textContent = '🚀 Running Enhanced Collection...';

            try {
                showMessage('Starting enhanced webinar collection...', 'info');
                
                const response = await fetch('/api/webinars/collect/enhanced', {
                    method: 'POST',
                    credentials: 'include'
                });
                const data = await response.json();

                if (data.status === 'success') {
                    const result = data.data;
                    showMessage(
                        `🎉 Enhanced collection completed! Found ${result.events_found} webinars, ` +
                        `${result.events_new} new, ${result.events_updated} updated.`,
                        'success'
                    );
                    
                    loadContactAnalytics();
                    loadEnhancedStats();
                    searchEvents();
                } else {
                    showError('Enhanced collection failed: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                showError('Error running enhanced collection: ' + error.message);
            } finally {
                collectBtn.disabled = false;
                collectBtn.textContent = '🚀 Run Enhanced Collection';
            }
        }

        async function bulkDiscoverContacts() {
            const bulkBtn = document.getElementById('bulkContactBtn');
            bulkBtn.disabled = true;
            bulkBtn.textContent = '🎯 Discovering Contacts...';

            try {
                showMessage('Starting bulk contact discovery for decision makers and organizers...', 'info');
                
                const response = await fetch('/api/webinars/contacts/bulk-discover', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ limit: 20 })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    const result = data.data;
                    showMessage(
                        `🎯 Contact discovery completed! Processed ${result.processed} events, ` +
                        `found ${result.total_decision_makers} decision makers and ${result.total_contacts_found} total contacts.`,
                        'success'
                    );
                    
                    loadContactAnalytics();
                    searchEvents();
                } else {
                    showError('Contact discovery failed: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                showError('Error running contact discovery: ' + error.message);
            } finally {
                bulkBtn.disabled = false;
                bulkBtn.textContent = '🎯 Bulk Contact Discovery';
            }
        }

        async function discoverEventContacts(eventId) {
            try {
                showMessage(`Discovering contacts for event ${eventId}...`, 'info');
                
                const response = await fetch('/api/webinars/contacts/discover', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ event_id: eventId })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    const result = data.data;
                    showMessage(
                        `✅ Found ${result.decision_makers.length} decision makers and ${result.general_contacts.length} contacts for this event.`,
                        'success'
                    );
                    
                    loadContactAnalytics();
                    searchEvents();
                } else {
                    showError('Contact discovery failed for this event');
                }
            } catch (error) {
                showError('Error discovering contacts: ' + error.message);
            }
        }

        async function exportContacts() {
            try {
                const response = await fetch('/api/webinars/contacts/export?type=decision_makers&format=csv', {
                    credentials: 'include'
                });
                const data = await response.json();

                if (data.status === 'success') {
                    // Create and download CSV file
                    const blob = new Blob([data.data.content], { type: 'text/csv' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'webinar_decision_makers.csv';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    showMessage(`📊 Exported ${data.data.count} decision makers to CSV file.`, 'success');
                } else {
                    showError('Export failed');
                }
            } catch (error) {
                showError('Error exporting contacts: ' + error.message);
            }
        }

        function displayEventsWithContacts(events) {
            const container = document.getElementById('eventsContainer');
            
            if (events.length === 0) {
                container.innerHTML = '<div class="loading">No events found. Try running an enhanced collection first.</div>';
                return;
            }

            const eventsHtml = events.map(event => {
                const eventDate = event.event_date ? new Date(event.event_date).toLocaleDateString() : 'TBD';
                const eventTime = event.event_date ? new Date(event.event_date).toLocaleTimeString() : '';

                // Build contact sections
                let contactsHtml = '';
                
                if (event.decision_makers && event.decision_makers.length > 0) {
                    contactsHtml += `
                        <div class="contact-section">
                            <h4>🎯 Decision Makers (${event.decision_makers.length})</h4>
                            <div class="contact-list">
                                ${event.decision_makers.map(contact => `
                                    <div class="contact-card decision-maker">
                                        <div class="contact-name">${contact.name || 'Name not available'}</div>
                                        <div class="contact-title">${contact.title || 'Title not available'}</div>
                                        <div class="contact-details">
                                            ${contact.email ? `<div>📧 <a href="mailto:${contact.email}">${contact.email}</a></div>` : ''}
                                            ${contact.phone ? `<div>📞 <a href="tel:${contact.phone}">${contact.phone}</a></div>` : ''}
                                            ${contact.linkedin_url ? `<div>💼 <a href="${contact.linkedin_url}" target="_blank">LinkedIn Profile</a></div>` : ''}
                                            ${contact.company ? `<div>🏢 ${contact.company}</div>` : ''}
                                            <div>🎯 Confidence: ${Math.round((contact.confidence || 0) * 100)}%</div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
                
                if (event.all_contacts && event.all_contacts.length > event.decision_makers.length) {
                    const otherContacts = event.all_contacts.filter(c => c.contact_type !== 'decision_makers');
                    if (otherContacts.length > 0) {
                        contactsHtml += `
                            <div class="contact-section">
                                <h4>📞 Other Contacts (${otherContacts.length})</h4>
                                <div class="contact-list">
                                    ${otherContacts.slice(0, 3).map(contact => `
                                        <div class="contact-card">
                                            <div class="contact-name">${contact.name || 'Name not available'}</div>
                                            <div class="contact-title">${contact.title || contact.contact_type}</div>
                                            <div class="contact-details">
                                                ${contact.email ? `<div>📧 <a href="mailto:${contact.email}">${contact.email}</a></div>` : ''}
                                                ${contact.linkedin_url ? `<div>💼 <a href="${contact.linkedin_url}" target="_blank">LinkedIn</a></div>` : ''}
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }
                }

                return `
                    <div class="event-card">
                        <div class="event-title">${event.title}</div>
                        <div class="event-meta">
                            <span class="platform">${event.platform || 'Unknown'}</span>
                            <span>📅 ${eventDate}${eventTime ? ' ' + eventTime : ''}</span>
                            ${event.is_free ? '<span class="free">FREE</span>' : '<span>💰 Paid</span>'}
                            ${event.topic_category ? `<span>🏷️ ${event.topic_category}</span>` : ''}
                            ${event.decision_maker_count > 0 ? `<span class="decision-makers">🎯 ${event.decision_maker_count} Decision Makers</span>` : ''}
                            ${event.total_contact_count > 0 ? `<span class="contact">📞 ${event.total_contact_count} Contacts</span>` : ''}
                        </div>
                        <div class="event-description">
                            ${event.description ? event.description.substring(0, 200) + '...' : 'No description available'}
                        </div>
                        ${event.organization_name ? `<div style="margin-bottom: 1rem;"><strong>🏢 Organization:</strong> ${event.organization_name}</div>` : ''}
                        ${contactsHtml}
                        <div class="event-actions">
                            ${event.registration_url ? 
                                `<a href="${event.registration_url}" target="_blank" class="btn-small">Register</a>` : 
                                ''
                            }
                            ${event.decision_maker_count === 0 ? 
                                `<button onclick="discoverEventContacts(${event.id})" class="btn-small contact-btn">🎯 Discover Contacts</button>` : 
                                ''
                            }
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = eventsHtml;
        }

        function displayPagination(pagination) {
            const container = document.getElementById('paginationContainer');
            
            if (pagination.pages <= 1) {
                container.innerHTML = '';
                return;
            }

            let paginationHtml = '<div class="pagination">';
            
            if (pagination.has_prev) {
                paginationHtml += `<button onclick="changePage(${pagination.page - 1})">Previous</button>`;
            }

            for (let i = Math.max(1, pagination.page - 2); i <= Math.min(pagination.pages, pagination.page + 2); i++) {
                const activeClass = i === pagination.page ? 'active' : '';
                paginationHtml += `<button class="${activeClass}" onclick="changePage(${i})">${i}</button>`;
            }

            if (pagination.has_next) {
                paginationHtml += `<button onclick="changePage(${pagination.page + 1})">Next</button>`;
            }

            paginationHtml += '</div>';
            container.innerHTML = paginationHtml;
        }

        function changePage(page) {
            currentPage = page;
            searchEvents();
        }

        function showLoading() {
            document.getElementById('eventsContainer').innerHTML = '<div class="loading">Loading events with contact discovery...</div>';
        }

        function showMessage(message, type = 'info') {
            const messageArea = document.getElementById('messageArea');
            const className = type === 'success' ? 'success' : type === 'error' ? 'error' : 'info';
            messageArea.innerHTML = `<div class="${className}">${message}</div>`;
        }

        function showError(message) {
            showMessage(message, 'error');
        }

        function clearMessage() {
            document.getElementById('messageArea').innerHTML = '';
        }

        // Auto-refresh stats every 5 minutes
        setInterval(() => {
            loadContactAnalytics();
            loadEnhancedStats();
        }, 5 * 60 * 1000);
    </script>
</body>
</html>
'''

# This allows the script to be run directly using `python app.py`
if __name__ == '__main__':
    # The API will run on port 5001 to avoid conflict with Next.js (port 3000)
    app.run(host='0.0.0.0', port=5001, debug=True)