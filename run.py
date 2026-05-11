"""
Bank Management System - Application Entry Point
This file starts the Flask application server
"""

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the development server
    # Debug=True enables auto-reload and detailed error pages
    # Host='0.0.0.0' makes it accessible from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
