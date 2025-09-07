# app.py
# Enhanced Backend API for the Enders Consulting application with Webinar Discovery Tool
# This Flask app handles API requests from the Next.js frontend and includes password-protected webinar discovery

from flask import Flask, request, jsonify, session, render_template_string
from flask_cors import CORS
import hashlib
import os
from datetime import datetime, timedelta
import sqlite3
import json
import logging

# Initialize the Flask application
app = Flask(__name__)

# Set a secret key for sessions (change this to a random secret key in production)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CORS Configuration ---
# This is crucial for allowing the Next.js frontend to make requests to this Flask backend.
# Updated to allow both localhost (development) and production domain
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
# Change these credentials for production use
WEBINAR_TOOL_USERNAME = os.environ.get('WEBINAR_USERNAME', 'renders')
WEBINAR_TOOL_PASSWORD = os.environ.get('WEBINAR_PASSWORD', 'Navigator2-Utmost-Lumpiness-Hatchet-Shrill')  # Change this!

# --- Database Setup ---
def init_webinar_db():
    """Initialize the webinar database"""
    conn = sqlite3.connect('webinar_discovery.db')
    cursor = conn.cursor()
    
    # Create events table
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    # Create collection_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_type TEXT,
            events_found INTEGER DEFAULT 0,
            events_new INTEGER DEFAULT 0,
            events_updated INTEGER DEFAULT 0,
            execution_time REAL DEFAULT 0,
            status TEXT DEFAULT 'completed',
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

# --- Webinar Discovery Tool Routes ---

@app.route('/webinar-tool')
def webinar_tool_login():
    """Login page for webinar discovery tool"""
    if is_authenticated():
        return render_template_string(WEBINAR_TOOL_HTML)
    
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
    """Get webinar events with filtering"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    topic = request.args.get('topic', '')
    platform = request.args.get('platform', '')
    is_free = request.args.get('is_free', '')
    
    # Build SQL query
    conn = sqlite3.connect('webinar_discovery.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])
    
    if topic:
        where_conditions.append("topic_category = ?")
        params.append(topic)
    
    if platform:
        where_conditions.append("platform = ?")
        params.append(platform)
    
    if is_free:
        where_conditions.append("is_free = ?")
        params.append(1 if is_free.lower() == 'true' else 0)
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM events WHERE {where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Get events with pagination
    offset = (page - 1) * per_page
    events_query = f"""
        SELECT * FROM events 
        WHERE {where_clause}
        ORDER BY event_date ASC, created_at DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(events_query, params + [per_page, offset])
    events = [dict(row) for row in cursor.fetchall()]
    
    # Get speakers for each event
    for event in events:
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

@app.route('/api/webinars/collect/run', methods=['POST'])
def run_webinar_collection():
    """Run webinar collection (simulated)"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    logger.info("Starting manual webinar collection...")
    
    # Simulate collection process
    import time
    start_time = time.time()
    
    # Add some sample data if database is empty
    conn = sqlite3.connect('webinar_discovery.db')
    cursor = conn.cursor()
    
    # Check if we have any events
    cursor.execute("SELECT COUNT(*) as count FROM events")
    event_count = cursor.fetchone()[0]
    
    events_new = 0
    events_updated = 0
    
    if event_count == 0:
        # Add sample events
        sample_events = [
            {
                'title': 'Cybersecurity Best Practices 2025',
                'description': 'Learn about the latest cybersecurity threats and how to protect your organization. This comprehensive webinar covers threat detection, incident response, and security frameworks.',
                'event_date': '2025-09-20 14:00:00',
                'registration_url': 'https://example.com/register/cybersecurity',
                'platform': 'ON24',
                'topic_category': 'cybersecurity',
                'is_free': 1
            },
            {
                'title': 'Digital Marketing Strategies for 2025',
                'description': 'Discover new digital marketing strategies and trends that will dominate 2025. Learn about AI-powered marketing, personalization, and customer engagement.',
                'event_date': '2025-10-05 15:00:00',
                'registration_url': 'https://example.com/register/marketing',
                'platform': 'LinkedIn',
                'topic_category': 'marketing',
                'is_free': 0
            },
            {
                'title': 'AI in Marketing: Future Trends',
                'description': 'Join us for an exclusive webinar on AI trends in marketing. Explore how artificial intelligence is transforming customer experiences and marketing automation.',
                'event_date': '2025-10-15 16:00:00',
                'registration_url': 'https://example.com/register/ai-marketing',
                'platform': 'BrightTalk',
                'topic_category': 'artificial-intelligence',
                'is_free': 0
            }
        ]
        
        for event in sample_events:
            cursor.execute("""
                INSERT INTO events (title, description, event_date, registration_url, platform, topic_category, is_free)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event['title'], event['description'], event['event_date'],
                event['registration_url'], event['platform'], event['topic_category'], event['is_free']
            ))
            events_new += 1
            
            # Add sample speakers
            event_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO speakers (event_id, name, company)
                VALUES (?, ?, ?)
            """, (event_id, 'Expert Speaker', 'Example Corp'))
    
    execution_time = time.time() - start_time
    
    # Log the collection
    cursor.execute("""
        INSERT INTO collection_logs (collection_type, events_found, events_new, events_updated, execution_time)
        VALUES (?, ?, ?, ?, ?)
    """, ('manual', events_new + events_updated, events_new, events_updated, execution_time))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Collection completed: {events_new} new, {events_updated} updated")
    
    return jsonify({
        'status': 'success',
        'data': {
            'events_found': events_new + events_updated,
            'events_new': events_new,
            'events_updated': events_updated,
            'execution_time': execution_time
        }
    })

@app.route('/api/webinars/analytics/summary', methods=['GET'])
def get_webinar_analytics():
    """Get webinar analytics summary"""
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
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'data': {
            'event_statistics': {
                'total_events': total_events,
                'upcoming_events': upcoming_events,
                'free_events': free_events
            }
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
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'data': {
            'summary': {
                'last_collection': last_collection[7] if last_collection else None  # created_at field
            }
        }
    })

# --- HTML Templates ---

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webinar Discovery Tool - Login</title>
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
            max-width: 400px;
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
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>Webinar Discovery Tool</h1>
            <p>Please enter your credentials to access the tool</p>
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

WEBINAR_TOOL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webinar Discovery Tool - Enders Consulting</title>
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
            max-width: 1200px;
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

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

        .event-description {
            color: #666;
            margin-bottom: 1rem;
            line-height: 1.5;
        }

        .event-actions {
            display: flex;
            gap: 0.5rem;
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
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <button class="logout-btn" onclick="logout()">Logout</button>
            <h1>Webinar Discovery Tool</h1>
            <p>Discover upcoming webinars from multiple platforms with enhanced search capabilities</p>
        </div>

        <div class="controls">
            <h2>Search & Collection Controls</h2>
            
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
                    </select>
                </div>
                <div class="control-item">
                    <label for="freeOnly">Free Events Only</label>
                    <select id="freeOnly">
                        <option value="">All Events</option>
                        <option value="true">Free Only</option>
                        <option value="false">Paid Only</option>
                    </select>
                </div>
            </div>

            <div class="control-group">
                <div class="control-item">
                    <button onclick="searchEvents()">Search Events</button>
                </div>
                <div class="control-item">
                    <button onclick="runCollection()" id="collectBtn">Run Collection</button>
                </div>
                <div class="control-item">
                    <button onclick="loadStats()">Refresh Stats</button>
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
                <div class="stat-number" id="upcomingEvents">-</div>
                <div class="stat-label">Upcoming Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="freeEvents">-</div>
                <div class="stat-label">Free Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="lastCollection">-</div>
                <div class="stat-label">Last Collection</div>
            </div>
        </div>

        <div class="events-container">
            <div class="events-header">
                <h2>Discovered Webinars</h2>
                <p>Click "Search Events" to load webinars or "Run Collection" to discover new ones</p>
            </div>
            <div id="eventsContainer">
                <div class="loading">Click "Search Events" to load webinars</div>
            </div>
            <div id="paginationContainer"></div>
        </div>
    </div>

    <script>
        let currentPage = 1;
        const perPage = 10;

        // Load initial stats
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
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

        async function loadStats() {
            try {
                const response = await fetch('/api/webinars/analytics/summary', {
                    credentials: 'include'
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    const stats = data.data;
                    document.getElementById('totalEvents').textContent = stats.event_statistics.total_events;
                    document.getElementById('upcomingEvents').textContent = stats.event_statistics.upcoming_events;
                    document.getElementById('freeEvents').textContent = stats.event_statistics.free_events;
                    
                    // Get collection status for last collection time
                    const statusResponse = await fetch('/api/webinars/collect/status', {
                        credentials: 'include'
                    });
                    const statusData = await statusResponse.json();
                    if (statusData.status === 'success' && statusData.data.summary.last_collection) {
                        const lastCollection = new Date(statusData.data.summary.last_collection);
                        document.getElementById('lastCollection').textContent = lastCollection.toLocaleDateString();
                    } else {
                        document.getElementById('lastCollection').textContent = 'Never';
                    }
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function searchEvents() {
            const searchTerm = document.getElementById('searchTerm').value;
            const topic = document.getElementById('topicFilter').value;
            const platform = document.getElementById('platformFilter').value;
            const freeOnly = document.getElementById('freeOnly').value;

            const params = new URLSearchParams({
                page: currentPage,
                per_page: perPage
            });

            if (searchTerm) params.append('search', searchTerm);
            if (topic) params.append('topic', topic);
            if (platform) params.append('platform', platform);
            if (freeOnly) params.append('is_free', freeOnly);

            try {
                showLoading();
                const response = await fetch(`/api/webinars/events?${params}`, {
                    credentials: 'include'
                });
                const data = await response.json();

                if (data.status === 'success') {
                    displayEvents(data.data.events);
                    displayPagination(data.data.pagination);
                    clearMessage();
                } else {
                    showError('Failed to load events');
                }
            } catch (error) {
                showError('Error loading events: ' + error.message);
            }
        }

        async function runCollection() {
            const collectBtn = document.getElementById('collectBtn');
            collectBtn.disabled = true;
            collectBtn.textContent = 'Collecting...';

            try {
                showMessage('Starting webinar collection...', 'info');
                
                const response = await fetch('/api/webinars/collect/run', {
                    method: 'POST',
                    credentials: 'include'
                });
                const data = await response.json();

                if (data.status === 'success') {
                    const result = data.data;
                    showMessage(
                        `Collection completed! Found ${result.events_found} events, ` +
                        `${result.events_new} new, ${result.events_updated} updated. ` +
                        `Execution time: ${result.execution_time.toFixed(2)}s`,
                        'success'
                    );
                    
                    // Refresh stats and events
                    loadStats();
                    searchEvents();
                } else {
                    showError('Collection failed');
                }
            } catch (error) {
                showError('Error running collection: ' + error.message);
            } finally {
                collectBtn.disabled = false;
                collectBtn.textContent = 'Run Collection';
            }
        }

        function displayEvents(events) {
            const container = document.getElementById('eventsContainer');
            
            if (events.length === 0) {
                container.innerHTML = '<div class="loading">No events found. Try running a collection first.</div>';
                return;
            }

            const eventsHtml = events.map(event => {
                const eventDate = event.event_date ? new Date(event.event_date).toLocaleDateString() : 'TBD';
                const registrationDeadline = event.registration_deadline ? 
                    new Date(event.registration_deadline).toLocaleDateString() : null;

                return `
                    <div class="event-card">
                        <div class="event-title">${event.title}</div>
                        <div class="event-meta">
                            <span class="platform">${event.platform || 'Unknown'}</span>
                            <span>📅 ${eventDate}</span>
                            ${event.is_free ? '<span class="free">FREE</span>' : '<span>💰 Paid</span>'}
                            ${event.topic_category ? `<span>🏷️ ${event.topic_category}</span>` : ''}
                            ${registrationDeadline ? `<span>⏰ Deadline: ${registrationDeadline}</span>` : ''}
                        </div>
                        <div class="event-description">
                            ${event.description ? event.description.substring(0, 200) + '...' : 'No description available'}
                        </div>
                        <div class="event-actions">
                            ${event.registration_url ? 
                                `<a href="${event.registration_url}" target="_blank" class="btn-small">Register</a>` : 
                                ''
                            }
                            ${event.speakers && event.speakers.length > 0 ? 
                                `<span class="btn-small" style="background: #6c757d;">👤 ${event.speakers[0].company || 'Speaker'}</span>` : 
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
            
            // Previous button
            if (pagination.has_prev) {
                paginationHtml += `<button onclick="changePage(${pagination.page - 1})">Previous</button>`;
            }

            // Page numbers
            for (let i = Math.max(1, pagination.page - 2); i <= Math.min(pagination.pages, pagination.page + 2); i++) {
                const activeClass = i === pagination.page ? 'active' : '';
                paginationHtml += `<button class="${activeClass}" onclick="changePage(${i})">${i}</button>`;
            }

            // Next button
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
            document.getElementById('eventsContainer').innerHTML = '<div class="loading">Loading events...</div>';
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
        setInterval(loadStats, 5 * 60 * 1000);
    </script>
</body>
</html>
'''

# This allows the script to be run directly using `python app.py`
if __name__ == '__main__':
    # The API will run on port 5001 to avoid conflict with Next.js (port 3000)
    app.run(host='0.0.0.0', port=5001, debug=True)
