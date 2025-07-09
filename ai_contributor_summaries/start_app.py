"""Script to start the Streamlit app."""

import subprocess
import sys
import time
import webbrowser
import os

def start_app():
    """Start the Streamlit app."""
    print("🚀 Starting Weaviate Contributor Analysis App...")
    
    # Check if streamlit is available
    try:
        import streamlit
        print("✅ Streamlit is available")
    except ImportError:
        print("❌ Streamlit not found. Please install it with: pip install streamlit")
        return False
    
    # Check if data is available
    try:
        from utils.weaviate_client import WeaviateClient
        client = WeaviateClient()
        contributors = client.query_data("Contributor", limit=1)
        if contributors:
            print(f"✅ Data available: {len(client.query_data('Contributor', limit=1000))} contributors")
        else:
            print("❌ No data found. Please run data ingestion first.")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Start the app
    print("🌐 Starting Streamlit server...")
    print("📱 App will be available at: http://localhost:8501")
    print("⏳ Please wait for the app to start...")
    
    try:
        # Start streamlit in a new process
        cmd = [sys.executable, "-m", "streamlit", "run", "simple_chatbot.py", "--server.port=8501"]
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ App started successfully!")
            print("🌐 Open your browser and go to: http://localhost:8501")
            print("🔍 Features available:")
            print("  • Search tab: Find contributors by name, technology, or skills")
            print("  • Analytics tab: Interactive charts and statistics")
            print("  • Contributors tab: Browse all 912 contributor profiles")
            print("⚠️  Press Ctrl+C to stop the app")
            
            # Try to open browser
            try:
                webbrowser.open("http://localhost:8501")
            except:
                pass
            
            # Wait for the process to finish
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n⏹️  Stopping app...")
                process.terminate()
                process.wait()
                print("✅ App stopped")
            
            return True
        else:
            # Process failed to start
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start app:")
            print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return False

if __name__ == "__main__":
    start_app()