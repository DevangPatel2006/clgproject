from flask import Flask
from api.files import files_bp
from api.pipeline_routes import pipeline_bp
from api.health import health_bp
import os

app = Flask(__name__)

# Configure CORS manually (no flask-cors dependency needed for local development)
@app.after_request
def after_request(response):
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
    origin = "*" if allowed_origins == "*" else allowed_origins.split(",")[0]
    response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# Configure max content length (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Register blueprints
app.register_blueprint(files_bp)
app.register_blueprint(pipeline_bp)
app.register_blueprint(health_bp)

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return {
        "status": "error",
        "message": "File too large. Maximum size is 16MB"
    }, 413

@app.errorhandler(500)
def internal_server_error(error):
    return {
        "status": "error",
        "message": "Internal server error occurred"
    }, 500

@app.errorhandler(404)
def not_found(error):
    return {
        "status": "error",
        "message": "Resource not found"
    }, 404

if __name__ == "__main__":
    # Get configuration from environment variables
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Flask server on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)