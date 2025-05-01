from browser_use import Agent
from langchain_anthropic import ChatAnthropic
import asyncio
from dotenv import load_dotenv
import os
import logging
import json
import requests
from typing import Optional
import time
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self):
        # Load environment variables from parent directory
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        logger.info(f"Loading .env from: {dotenv_path}")
        load_dotenv(dotenv_path)
        
        # Check if ANTHROPIC_API_KEY is set
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Initialize browser-use agent with Claude
        self.agent = Agent(
            task="Help me stay focused by identifying and closing distracting tabs or windows",
            llm=ChatAnthropic(model="claude-3-opus-20240229")
        )
        self.api_url = "http://localhost:5000"
        self.last_check = 0
        self.check_interval = 2  # seconds
        
    async def check_for_distractions(self):
        """Check the API for any detected distractions"""
        try:
            while True:
                current_time = time.time()
                if current_time - self.last_check >= self.check_interval:
                    response = requests.get(f"{self.api_url}/api/analysis")
                    if response.status_code == 200:
                        analysis = response.json().get('analysis')
                        if analysis and ('FOCUSED: no' in analysis or 'focused: no' in analysis.lower()):
                            logger.info("Distraction detected! Taking action...")
                            await self.handle_distraction(analysis)
                    self.last_check = current_time
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
        except Exception as e:
            logger.error(f"Error in check_for_distractions: {e}", exc_info=True)
    
    async def handle_distraction(self, analysis: str):
        """Handle a detected distraction using browser-use"""
        try:
            # Check if the distraction is browser-based
            browser_keywords = ["tab", "browser", "chrome", "firefox", "safari", "website", "url", "web page", "youtube", "social media", "facebook", "twitter", "instagram", "tiktok", "reddit"]
            is_browser_distraction = any(keyword in analysis.lower() for keyword in browser_keywords)
            
            if is_browser_distraction:
                logger.info("Browser-based distraction detected. Using browser-use to manage tabs...")
                # Use browser-use to help guide focus by closing distracting tabs
                await self.agent.run(
                    task="Help me stay focused by identifying and closing distracting tabs or windows",
                    max_steps=3
                )
            else:
                logger.info("Non-browser distraction detected. Opening report...")
                # Create HTML content
                print("Creating HTML content...")
                html_content = self.create_distraction_report(analysis)
                
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
            logger.error(f"Error handling distraction: {e}", exc_info=True)
            
    def create_distraction_report(self, analysis: str):
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
            </body>
        </html>
        """

async def main():
    logger.info("Browser controller initialized")
    controller = BrowserController()
    logger.info("Starting distraction monitoring...")
    await controller.check_for_distractions()

if __name__ == "__main__":
    asyncio.run(main()) 