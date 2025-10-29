from flask import Flask
from api.files import files_bp
from api.pipeline_routes import pipeline_bp
from api.health import health_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(files_bp)
app.register_blueprint(pipeline_bp)
app.register_blueprint(health_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
