# app.py
# Backend API for the Enders Consulting application.
# This Flask app handles API requests from the Next.js frontend.

from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)

# --- CORS Configuration ---
# This is crucial for allowing the Next.js frontend (running on a different port)
# to make requests to this Flask backend.
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) # Adjust origin for production

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
    # This logic remains the same, but instead of flashing messages,
    # it prepares a JSON response.
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

    # Return the response as a JSON object
    return jsonify({
        'message': response_message,
        'category': response_category
    })

# This allows the script to be run directly using `python app.py`
if __name__ == '__main__':
    # The API will run on port 5001 to avoid conflict with Next.js (port 3000)
    app.run(port=5001, debug=True)
