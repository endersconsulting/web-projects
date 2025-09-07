Webinar Discovery Tool Integration Guide

Overview

This guide shows you how to integrate the webinar discovery tool into your existing Flask website at endersconsulting.cloud with password protection. The tool will be accessible only to authorized users via a protected URL.

Integration Steps

1. Update Your Flask App

Replace your current app.py with the enhanced version that includes:

•
All your existing functionality (unchanged)

•
Webinar discovery tool routes

•
Session-based authentication

•
Password protection

2. Key Features Added

•
Protected Access: Tool is only accessible at /webinar-tool with login

•
Session Management: 8-hour session timeout for security

•
Complete Integration: Works seamlessly with your existing CORS and API setup

•
Responsive Design: Matches your site's professional appearance

3. Configuration

Environment Variables (Recommended for Production)

Bash


# Set these environment variables on your server
export SECRET_KEY="your-very-secure-secret-key-here"
export WEBINAR_USERNAME="your-chosen-username"
export WEBINAR_PASSWORD="your-secure-password"


Default Credentials (Change These!)

If you don't set environment variables, the defaults are:

•
Username: admin

•
Password: secure123

⚠️ IMPORTANT: Change these credentials before deployment!

4. Database Setup

The tool automatically creates a SQLite database (webinar_discovery.db) with the following tables:

•
events: Stores webinar information

•
speakers: Stores speaker details

•
collection_logs: Tracks collection history

5. New API Endpoints

The integration adds these protected endpoints:

Authentication

•
POST /api/webinar-auth - Login to webinar tool

•
POST /api/webinar-logout - Logout from webinar tool

Webinar Data

•
GET /api/webinars/events - List events with filtering

•
POST /api/webinars/collect/run - Start webinar collection

•
GET /api/webinars/analytics/summary - Get statistics

•
GET /api/webinars/collect/status - Get collection status

Web Interface

•
GET /webinar-tool - Main webinar tool interface (password protected)

6. Deployment Instructions

Option A: Replace Existing File

1.
Backup your current app.py:

2.
Replace with integrated version:

3.
Install additional dependencies:

4.
Set environment variables:

5.
Restart your Flask application

Option B: Manual Integration

If you prefer to manually integrate the code:

1.
Add imports to your existing app.py:

2.
Add session configuration:

3.
Copy the authentication functions and webinar routes from integrated_app.py

4.
Copy the HTML templates at the end of the file

7. Access Instructions

For You (Admin)

1.
Navigate to: https://endersconsulting.cloud/webinar-tool

2.
Enter your username and password

3.
Access the full webinar discovery interface

For Your Team

•
Share the URL: https://endersconsulting.cloud/webinar-tool

•
Provide them with the login credentials

•
Sessions last 8 hours before requiring re-login

8. Security Features

•
Session-based authentication: No tokens to manage

•
Automatic logout: Sessions expire after 8 hours

•
Password hashing: Passwords are hashed for security

•
CORS protection: Only your domain can access the API

•
Hidden from public: Tool is not linked from your main site

9. Usage Instructions

Once logged in, users can:

1.
Run Collection: Click "Run Collection" to discover new webinars

2.
Search Events: Use filters to find specific webinars

3.
View Details: See comprehensive webinar information

4.
Export Data: Access via API for integration with other tools

10. Customization Options

Change Login Credentials

Python


# In your app.py or via environment variables
WEBINAR_TOOL_USERNAME = "your-username"
WEBINAR_TOOL_PASSWORD = "your-password"


Modify Session Timeout

Python


app.permanent_session_lifetime = timedelta(hours=24)  # 24 hour sessions


Add More Users

You can extend the authentication to support multiple users by:

1.
Creating a users table in the database

2.
Modifying the authentication function

3.
Adding user management endpoints

11. Monitoring and Maintenance

Check Database Size

Bash


ls -lh webinar_discovery.db


View Collection Logs

The tool automatically logs all collection activities in the collection_logs table.

Backup Database

Bash


cp webinar_discovery.db webinar_discovery_backup_$(date +%Y%m%d).db


12. Troubleshooting

Common Issues

1.
"Authentication required" errors

•
Check if session cookies are enabled

•
Verify CORS settings include credentials



2.
Database errors

•
Ensure write permissions in the application directory

•
Check disk space



3.
Login not working

•
Verify credentials are set correctly

•
Check browser console for JavaScript errors



Debug Mode

For troubleshooting, you can enable debug mode:

Python


app.run(host='0.0.0.0', port=5001, debug=True)


13. Production Considerations

1.
Use HTTPS: Ensure your site uses SSL certificates

2.
Set Strong Passwords: Use complex, unique passwords

3.
Regular Backups: Backup the database regularly

4.
Monitor Access: Check logs for unauthorized access attempts

5.
Update Dependencies: Keep Flask and other packages updated

14. Integration with n8n

You can now integrate this with your n8n workflows:

JSON


{
  "nodes": [
    {
      "name": "Get Webinars",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "https://endersconsulting.cloud/api/webinars/events",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpHeaderAuth": {
          "name": "Cookie",
          "value": "session=your-session-cookie"
        }
      }
    }
  ]
}


Summary

This integration provides you with a powerful, password-protected webinar discovery tool that:

•
Seamlessly integrates with your existing website

•
Requires no changes to your frontend

•
Provides secure access for authorized users only

•
Maintains all your existing functionality

•
Can be easily customized and extended



