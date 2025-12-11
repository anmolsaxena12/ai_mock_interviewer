"""
Flask application factory for AI Mock Interviewer

This file creates and configures the Flask application.
"""
import os
import shutil
from dotenv import load_dotenv
from flask import Flask

# Load environment variables from .env file
load_dotenv()

def create_app(config_object=None):
    """
    Application factory pattern for Flask app
    
    Args:
        config_object: Configuration object to use (defaults to Config from config.py)
    
    Returns:
        Configured Flask app instance
    """
    from config import Config
    from routes import main_bp
    from services import llm_chains
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    
    # Initialize LLM for the chains
    if not app.config.get('TESTING'):
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=Config.GOOGLE_API_KEY
        )
        llm_chains.set_llm_instance(llm)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    # Ensure necessary folders exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('CHROMA_DB_DIR', 'chroma_db'), exist_ok=True)
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
