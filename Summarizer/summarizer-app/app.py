from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from summarizer import summarize_text, generate_essay

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/essay-writer')
def essay_writer_page():
    return render_template('essay_writer.html')

@app.route('/summarize', methods=['POST'])
@limiter.limit("10/minute")
def summarize_endpoint():
    """API endpoint for the summarizer."""
    data = request.get_json()
    text = data.get('text', '')
    length = data.get('length', 'medium') 

    summary = summarize_text(text, length)
    
    if summary.startswith("Error:"):
        return jsonify({"error": summary}), 500
    return jsonify({"summary": summary})

# --- THIS BLOCK WAS MISSING ---
@app.route('/generate-essay', methods=['POST'])
@limiter.limit("5/minute")
def generate_essay_endpoint():
    """API endpoint for the essay writer."""
    data = request.get_json()
    topic = data.get('topic', '')
    essay = generate_essay(topic)
    if essay.startswith("Error:"):
        return jsonify({"error": essay}), 500
    return jsonify({"essay": essay})
# -----------------------------

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error=f"Rate limit exceeded: {e.description}."), 429

if __name__ == '__main__':
    app.run(debug=True)