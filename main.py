import mss
import time
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import base64
from PIL import Image
import io
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import json
import requests

# Load environment variables
load_dotenv()
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Create screenshots and logs directories
SCREENSHOT_DIR = Path("screenshots")
LOGS_DIR = Path("logs")

# Clean up and recreate directories
for directory in [SCREENSHOT_DIR, LOGS_DIR]:
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'focus_monitor.log'),
        logging.StreamHandler()
    ]
)

# The task we're supposed to be working on
CURRENT_TASK = "Working on a math project - solving calculus problems"

# Store analysis results
latest_analysis = {
    "focused": False,
    "mainContent": "",
    "activeDistractions": "",
    "reasoning": "",
    "timestamp": ""
}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Simple HTML template
DISTRACTION_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Focus Monitor - Distraction Detected</title>
    <style>
body {{ 
    font-family: Arial, sans-serif;
    margin: 20px;
    background: #f5f5f5;
    color: #333;
}}
.container {{ 
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
.header {{ 
    background: #ff4444;
    color: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}}
.content {{ 
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}
.analysis {{ 
    background: #f8f8f8;
    padding: 20px;
    border-radius: 8px;
    white-space: pre-wrap;
}}
.screenshot {{ 
    background: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}}
.screenshot img {{ 
    max-width: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
}}
pre {{ 
    margin: 0;
    font-family: monospace;
    background: #fff;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #ddd;
}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 Distraction Detected!</h1>
            <p>Current Task: {task}</p>
            <p>Time: {timestamp}</p>
        </div>
        <div class="content">
            <div class="analysis">
                <h2>Analysis Results:</h2>
                <pre>{analysis}</pre>
            </div>
            <div class="screenshot">
                <h2>Current Screenshot:</h2>
                <img src="data:image/jpeg;base64,{screenshot}" alt="Current screen capture">
            </div>
        </div>
    </div>
</body>
</html>"""

def test_distraction_handler():
    print("\n🧪 Testing distraction handler...")
    
    try:
        # Create a sample analysis
        test_analysis = """FOCUSED: no
MAIN CONTENT: Test content for debugging
ACTIVE DISTRACTIONS: none
REASONING: This is a test analysis."""
        
        # Take a real screenshot to test with
        screenshot_path = take_screenshot()
        print(f"Using screenshot: {screenshot_path}")
        
        # Create and test the distraction manager
        manager = DistractionManager()
        try:
            print("Calling handle_distraction...")
            manager.handle_distraction(test_analysis, screenshot_path)
            print("✅ Distraction handler test completed")
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")
        finally:
            manager.cleanup()
            
        return True
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

class DistractionManager:
    def __init__(self):
        self.driver = None
    
    def initialize_browser(self):
        """Initialize the browser if not already initialized"""
        if self.driver is None:
            options = webdriver.ChromeOptions()
            # Keep browser visible but move it off-screen
            options.add_argument('--window-position=-2000,0')
            self.driver = webdriver.Chrome(options=options)
    
    def handle_distraction(self, analysis, screenshot_path):
        """Handle a detected distraction by showing a report"""
        try:
            print("\n📝 Handling distraction...")
            
            # Make sure browser is initialized
            self.initialize_browser()
            
            # Create HTML content
            print("Creating HTML content...")
            html_content = self.create_distraction_report(analysis, screenshot_path)
            
            # Save HTML to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = f"logs/distraction_{timestamp}.html"
            os.makedirs("logs", exist_ok=True)
            
            print(f"Saving HTML to: {html_path}")
            with open(html_path, "w") as f:
                f.write(html_content)
            
            # Open in browser
            file_url = f"file://{os.path.abspath(html_path)}"
            print(f"Opening URL: {file_url}")
            
            # Open in new tab and bring window to front
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(file_url)
            self.driver.set_window_position(0, 0)  # Make visible
            
            print("🚨 Opening distraction report!")
            
        except Exception as e:
            print(f"❌ Error in handle_distraction: {str(e)}")
            logging.error(f"Error handling distraction: {str(e)}", exc_info=True)
            self.cleanup()  # Cleanup on error
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                print("Browser cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            
    def create_distraction_report(self, analysis, screenshot_path):
        """Create an HTML report for the distraction"""
        return f"""
        <html>
            <head>
                <title>Focus Check</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .alert {{ background: #ffe6e6; padding: 20px; border-radius: 8px; }}
                    .analysis {{ white-space: pre-wrap; background: #f5f5f5; padding: 15px; }}
                    img {{ max-width: 100%; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <h1>⚠️ Focus Check</h1>
                <div class="alert">
                    <h2>You seem to be distracted!</h2>
                    <p>The system has detected that you're not focused on your task:</p>
                    <p><strong>Current Task:</strong> {os.getenv('CURRENT_TASK', 'Not specified')}</p>
                </div>
                
                <h3>Analysis:</h3>
                <div class="analysis">{analysis}</div>
                
                <h3>Screenshot:</h3>
                <img src="file://{os.path.abspath(screenshot_path)}" alt="Screenshot">
            </body>
        </html>
        """

def take_screenshot():
    with mss.mss() as sct:
        # Get the bounds of all monitors combined
        left = min(monitor["left"] for monitor in sct.monitors[1:])
        top = min(monitor["top"] for monitor in sct.monitors[1:])
        right = max(monitor["left"] + monitor["width"] for monitor in sct.monitors[1:])
        bottom = max(monitor["top"] + monitor["height"] for monitor in sct.monitors[1:])
        
        # Create the capture region
        monitor = {
            "left": left,
            "top": top,
            "width": right - left,
            "height": bottom - top
        }
        
        print(f"Capturing region: {monitor}")
        screenshot = sct.grab(monitor)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SCREENSHOT_DIR / f"screen_{timestamp}.png"
        
        # Save the screenshot
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filename))
        print(f"Captured screenshot: {filename}")
        return filename

def analyze_screenshot(filename):
    try:
        # Open and convert image to PNG format
        with Image.open(filename) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Save as PNG in memory
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
        
        # Prepare the prompt for Claude
        prompt = f"""I am currently: {CURRENT_TASK}

Please analyze this screenshot holistically, focusing primarily on whether I am making progress on my stated task.

Key Analysis Points:
1. MAIN CONTENT (80% weight): What content dominates the screen? Consider development work on this focus monitoring system as acceptable progress.
2. ACTIVE DISTRACTIONS (20% weight): Only count something as a distraction if it's:
   - Actively playing (video/audio)
   - Taking up significant screen space
   - Clearly engaging attention away from productive work
   
Important Guidelines:
- Development work on this focus monitoring system is considered productive
- IGNORE any Chrome automation/browser-use messages as they're part of the system
- Start your response with either "FOCUSED: yes" or "FOCUSED: no"
- Be lenient - only mark as unfocused if there are clear distractions

Analyze the screenshot and tell me if I'm focused or distracted."""

        # Create the message for Claude
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]

        # Make the API call
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={"model": "claude-3-opus-20240229", "messages": messages, "max_tokens": 1024}
        )
        
        response.raise_for_status()
        result = response.json()
        return result['content'][0]['text']
        
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        print(f"Error occurred: {e}")
        return None

def resize_image(image_path, max_size_mb=4):
    # Open the image
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Start with original size
        width, height = img.size
        
        # Calculate initial quality
        quality = 95
        
        while True:
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=quality)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Check size
            size_mb = len(img_byte_arr) / (1024 * 1024)
            
            if size_mb <= max_size_mb:
                return img_byte_arr
            
            # If still too large, reduce quality or size
            if quality > 30:
                quality -= 5
            else:
                # Reduce size by 10%
                width = int(width * 0.9)
                height = int(height * 0.9)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                quality = 95

def monitor_focus():
    print(f"Starting distraction monitor for task: {CURRENT_TASK}")
    
    # Initialize the distraction manager
    distraction_manager = DistractionManager()
    
    try:
        while True:
            # Take and analyze screenshot
            screenshot_path = take_screenshot()
            analysis = analyze_screenshot(screenshot_path)
            logging.info(f"Analysis result: {analysis}")
            print("\nClaude's Analysis:")
            print(analysis)
            
            # Only proceed with analysis if we got a valid response
            if analysis:
                # Debug the detection logic
                print("\nDebug detection:")
                print(f"Analysis text: '{analysis}'")
                print(f"Lowercase analysis: '{analysis.lower()}'")
                print(f"Contains 'FOCUSED: no'? {('FOCUSED: no' in analysis)}")
                print(f"Contains 'focused: no'? {('focused: no' in analysis.lower())}")
                
                # Check if distracted and handle it
                if ('FOCUSED: no' in analysis) or ('focused: no' in analysis.lower()):
                    print("✅ Distraction detected! Handling...")
                    distraction_manager.handle_distraction(analysis, screenshot_path)
                else:
                    print("❌ No distraction detected")
            else:
                print("Failed to analyze screenshot, will try again...")
            
            print("\nWaiting 2 seconds...")
            time.sleep(2)
            
    except KeyboardInterrupt:
        logging.info("Stopping distraction monitor...")
        print("\nStopping distraction monitor...")
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        print(f"\nError occurred: {e}")
    finally:
        distraction_manager.cleanup()
        logging.info("Cleanup completed")

# API Endpoints
@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    return jsonify(latest_analysis)

@app.route('/api/task', methods=['GET'])
def get_task():
    return jsonify({"task": CURRENT_TASK})

@app.route('/api/task', methods=['POST'])
def update_task():
    global CURRENT_TASK
    data = request.json
    if 'task' in data:
        CURRENT_TASK = data['task']
        return jsonify({"success": True, "task": CURRENT_TASK})
    return jsonify({"success": False, "error": "No task provided"}), 400

@app.route('/api/analyze', methods=['POST'])
def manual_analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image provided"}), 400
    
    file = request.files['image']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = SCREENSHOT_DIR / f"manual_{timestamp}.png"
    file.save(filename)
    
    analysis = analyze_screenshot(filename)
    return jsonify({"success": True, "analysis": latest_analysis})

def main():
    logging.info(f"Starting distraction monitor for task: {CURRENT_TASK}")
    print("Press Ctrl+C to stop...")
    
    print("\n🔄 Starting main monitoring loop...")
    
    # Start the focus monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_focus)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Start the Flask API server
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 