from browser_use import Agent
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
import os
import logging
import json
import requests
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self):
        # Load environment variables from parent directory
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        logger.info(f"Loading .env from: {dotenv_path}")
        load_dotenv(dotenv_path)
        
        # Check if OPENAI_API_KEY is set
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.agent = None
        self.api_url = "http://localhost:5000"
        
    async def initialize(self):
        self.agent = Agent(
            task="Handle distractions by closing them and redirecting to productive sites",
            llm=ChatOpenAI(model="gpt-4"),
        )
        logger.info("Browser controller initialized")
    
    def get_latest_analysis(self) -> Optional[dict]:
        """Get the latest analysis from the focus monitoring API."""
        try:
            response = requests.get(f"{self.api_url}/api/analysis")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None
    
    async def handle_distraction(self, url: str):
        """Handle a distraction by redirecting to productive content."""
        if not self.agent:
            await self.initialize()
        
        logger.info(f"Handling distraction: {url}")
        # Create a task to handle the distraction
        task = f"""
        The user is distracted by {url}. Follow these steps:
        1. Open a new browser window
        2. Navigate to {url} to understand what's distracting them
        3. Close that tab
        4. Open a new tab with a productive alternative (like todoist.com or coursera.org)
        5. Explain to the user why this switch will help them be more productive
        """
        await self.agent.run(task)
        logger.info(f"Finished handling distraction: {url}")
        return {"status": "success"}

async def monitor_and_handle_distractions():
    """Monitor the focus API and handle distractions when detected."""
    controller = BrowserController()
    await controller.initialize()
    
    logger.info("Starting distraction monitoring...")
    while True:
        try:
            # Get latest analysis
            analysis = controller.get_latest_analysis()
            if analysis and not analysis.get("focused", True):
                # Extract the main content and active distractions
                main_content = analysis.get("mainContent", "")
                active_distractions = analysis.get("activeDistractions", "")
                
                # If there are active distractions, handle them
                if active_distractions and active_distractions.lower() != "none":
                    # Extract URLs from the distractions
                    # This is a simple implementation - you might want to make it more robust
                    urls = [word for word in active_distractions.split() if word.startswith(("http://", "https://"))]
                    for url in urls:
                        await controller.handle_distraction(url)
            
            # Wait before checking again
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(5)  # Wait longer on error

async def main():
    await monitor_and_handle_distractions()

if __name__ == "__main__":
    asyncio.run(main()) 