from browser_use import Agent
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
import os
import logging

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
        
    async def initialize(self):
        self.agent = Agent(
            task="Handle distractions by closing them and redirecting to productive sites",
            llm=ChatOpenAI(model="gpt-4"),
        )
        logger.info("Browser controller initialized")
    
    async def handle_distraction(self, url):
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

async def main():
    controller = BrowserController()
    await controller.initialize()
    
    # Test handling a distraction
    await controller.handle_distraction("https://www.youtube.com")

if __name__ == "__main__":
    asyncio.run(main()) 