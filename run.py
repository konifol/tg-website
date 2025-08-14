#!/usr/bin/env python3
"""
Simple script to run the Bot Creator Platform
"""

from app import app

if __name__ == '__main__':
    print("Starting Bot Creator Platform...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")