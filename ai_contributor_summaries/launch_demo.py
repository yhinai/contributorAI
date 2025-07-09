#!/usr/bin/env python3
"""
Launch the AI Contributor Summaries demo with mock data.
"""

import os
import subprocess
import sys

def main():
    """Launch the demo."""
    print("🚀 AI Contributor Summaries Demo")
    print("=" * 50)
    
    # Set environment variable for mock mode
    os.environ['USE_MOCK_WEAVIATE'] = 'true'
    
    print("🧪 Running in mock mode (local storage)")
    print("📁 Data stored in: mock_data/")
    print("🌐 UI will start at: http://localhost:8501")
    print("=" * 50)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'ui/streamlit_app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error launching demo: {e}")

if __name__ == '__main__':
    main()