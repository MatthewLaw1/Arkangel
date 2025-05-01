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
        self.consecutive_distractions = 0
        self.last_reminder_time = 0
        self.driver = None
        
    def init_browser(self):
        print("Initializing browser...")
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(options=chrome_options)
            # Hide the browser initially
            self.driver.set_window_position(-2000, 0)
            time.sleep(2)  # Let the browser settle
            print("Browser initialized and hidden")
        
    def handle_distraction(self, analysis, screenshot_path):
        print("\n📝 Handling distraction...")
        current_time = time.time()
        if current_time - self.last_reminder_time >= 30:
            try:
                print("Initializing browser...")
                self.init_browser()
                
                print("Reading screenshot...")
                with open(screenshot_path, 'rb') as img_file:
                    screenshot_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                print("Creating HTML content...")
                html_content = DISTRACTION_PAGE.format(
                    task=CURRENT_TASK,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    analysis=analysis,
                    screenshot=screenshot_data
                )
                
                # Save HTML file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                html_path = LOGS_DIR / f"distraction_{timestamp}.html"
                print(f"Saving HTML to: {html_path}")
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Open the HTML file in a new tab and make visible
                file_url = f"file://{html_path.absolute()}"
                print(f"Opening URL: {file_url}")
                self.driver.switch_to.new_window('tab')
                self.driver.set_window_position(0, 0)  # Make browser visible
                self.driver.get(file_url)
                print("Browser tab opened and made visible")
                
                self.consecutive_distractions += 1
                self.last_reminder_time = current_time
                
                logging.info(f"Distraction detected! Analysis: {analysis}")
                print("\n🚨 Opening distraction report!")
                
            except Exception as e:
                print(f"❌ Error in handle_distraction: {str(e)}")
                logging.error(f"Error handling distraction: {str(e)}", exc_info=True)
    
    def cleanup(self):
        try:
            if self.driver:
                self.driver.quit()
                print("Browser cleaned up")
        except:
            pass

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
    # Resize image and get bytes
    img_bytes = resize_image(filename)
    base64_image = base64.b64encode(img_bytes).decode('utf-8')
    
    # Prepare the prompt for Claude
    prompt = f"""I am currently: {CURRENT_TASK}

Please analyze this screenshot holistically, focusing primarily on whether I am making progress on my stated task.

Key Analysis Points:
1. MAIN CONTENT (80% weight): What content dominates the screen? If it's related to the task (math/calculus), this strongly indicates focus.
2. ACTIVE DISTRACTIONS (20% weight): Only count something as a distraction if it's:
   - Actively playing (video/audio)
   - Taking up significant screen space
   - Clearly engaging attention (e.g., open chat window with new messages)
   
Important Guidelines:
- IGNORE any Chrome automation/testing messages
- Presence of unrelated tabs/apps alone is NOT a distraction
- Small UI elements (dock, menubar apps) are NOT distractions
- If math/calculus content is visible and dominant, consider it FOCUSED regardless of other UI elements
- Only mark as unfocused if the main content is clearly unrelated to math/calculus OR if there are major active distractions

Respond in this exact format:
FOCUSED: [yes/no]
MAIN CONTENT: [describe the dominant content on screen]
ACTIVE DISTRACTIONS: [none/only list major, active distractions taking significant attention]
REASONING: [2-3 sentences explaining your conclusion, weighted heavily on main content]
"""

    # Send to Claude
    message = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                }
            ]
        }]
    )
    
    response_text = message.content[0].text
    
    # Parse Claude's response
    focused = "yes" in response_text.split("FOCUSED:")[1].split("\n")[0].lower()
    main_content = response_text.split("MAIN CONTENT:")[1].split("\n")[0].strip()
    active_distractions = response_text.split("ACTIVE DISTRACTIONS:")[1].split("\n")[0].strip()
    reasoning = response_text.split("REASONING:")[1].strip()
    
    # Update the latest analysis
    global latest_analysis
    latest_analysis = {
        "focused": focused,
        "mainContent": main_content,
        "activeDistractions": active_distractions,
        "reasoning": reasoning,
        "timestamp": datetime.now().isoformat()
    }
    
    return response_text

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
    
    # Run the test first
    if not test_distraction_handler():
        print("❌ Tests failed. Please check the logs and try again.")
        return
    
    print("\n🔄 Starting main monitoring loop...")
    
    # Start the focus monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_focus)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Start the Flask API server
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 