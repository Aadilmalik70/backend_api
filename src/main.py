import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify
from flask_cors import CORS
from src.routes.api import api_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all API routes

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "name": "AI Content Strategist for SERP Dominance API",
        "version": "1.0.0",
        "endpoints": [
            "/api/process",
            "/api/analyze-url",
            "/api/export",
            "/api/publish",
            "/api/mock-data"
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
