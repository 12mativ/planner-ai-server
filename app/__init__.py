from flask import Flask
from app.prompt.controller import prompt_bp
from app.ai_planner.controller import ai_planner_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(prompt_bp, url_prefix="/api")
    app.register_blueprint(ai_planner_bp, url_prefix="/api")
    return app
