#!/usr/bin/env python3
"""
Wealth Agent - Din väg till ekonomisk frihet
Standalone Flask Application
"""

import os
import logging
from flask import Flask, redirect
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory."""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'wealth-agent-secret-key'),
        JSON_SORT_KEYS=False,
    )

    CORS(app)

    # Database
    from database import init_db, db_session, Base, engine
    init_db()

    from models import UserProfile, WealthGoal, ChatConversation, ChatMessage
    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # Register Wealth Agent routes
    from routes import wealth_bp
    app.register_blueprint(wealth_bp)

    # Root redirect to dashboard
    @app.route('/')
    def root():
        return redirect('/dashboard/')

    # Health check
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'app': 'Wealth Agent'}

    logger.info("Wealth Agent started")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('DEBUG', '0') == '1'
    )
