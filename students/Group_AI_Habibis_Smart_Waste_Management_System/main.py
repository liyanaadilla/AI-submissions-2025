
import sys
import os
import subprocess

if __name__ == "__main__":
    # Ensure we are running from the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the streamlit app
    app_path = "app.py"
    
    # Run streamlit
    # using sys.executable ensures we use the same python interpreter
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass
