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

# Load environment variables
load_dotenv()
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Create screenshots directory if it doesn't exist
SCREENSHOT_DIR = Path("screenshots")
if SCREENSHOT_DIR.exists():
    shutil.rmtree(SCREENSHOT_DIR)
SCREENSHOT_DIR.mkdir(exist_ok=True)

# The task we're supposed to be working on
CURRENT_TASK = "Working on a math project - solving calculus problems"

def take_screenshot():
    with mss.mss() as sct:
        # Get the bounds of all monitors combined
        left = min(monitor["left"] for monitor in sct.monitors[1:])  # Skip the "all-in-one" monitor
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
        
        print(f"Capturing region: {monitor}")  # Debug info
        screenshot = sct.grab(monitor)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SCREENSHOT_DIR / f"screen_{timestamp}.png"
        
        # Save the screenshot
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filename))
        print(f"Captured screenshot: {filename}")
        return filename

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
- Presence of unrelated tabs/apps alone is NOT a distraction
- Small UI elements (dock, menubar apps) are NOT distractions
- If math/calculus content is visible and dominant, consider it FOCUSED regardless of other UI elements
- Only mark as unfocused if the main content is clearly unrelated to math/calculus OR if there are major active distractions

For example:
- Math work visible with social media tabs = FOCUSED
- Math work visible with small chat window = FOCUSED
- YouTube playing with math work = NOT FOCUSED
- Full-screen social media = NOT FOCUSED

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
    
    return message.content[0].text

def main():
    print(f"Starting distraction monitor for task: {CURRENT_TASK}")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            # Take and analyze screenshot
            screenshot_path = take_screenshot()
            analysis = analyze_screenshot(screenshot_path)
            print("\nClaude's Analysis:")
            print(analysis)
            print("\nWaiting 2 seconds...")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping distraction monitor...")
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    main() 