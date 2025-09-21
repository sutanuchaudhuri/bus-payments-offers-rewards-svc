#!/usr/bin/env python3
"""
Main application runner
"""
import sys
import os

# Add the current directory to Python path for app imports
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Create database tables
    with app.app_context():
        from app.models import db
        db.create_all()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5006)