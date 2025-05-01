import json
import logging
import asyncio
import requests
from typing import Optional
from .custom_agent import CustomAgent
from langchain_core.language_models.chat_models import BaseChatModel
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller
from .hello_world_agent import HelloWorldAgent

logger = logging.getLogger(__name__)

class DistractionDetectionAgent(HelloWorldAgent):
    def __init__(
            self,
            task: str,
            llm: BaseChatModel,
            api_url: str = "http://localhost:5000",
            browser: Browser | None = None,
            browser_context: BrowserContext | None = None,
            controller: Controller = Controller(),
            use_vision: bool = True,
            max_steps: int = 100
    ):
        super().__init__(
            task=task,
            llm=llm,
            browser=browser,
            browser_context=browser_context,
            controller=controller,
            use_vision=use_vision,
            max_steps=max_steps
        )
        self.api_url = api_url

    async def run(self, max_steps: int = 100) -> AgentHistoryList:
        """Monitor for distractions using the Flask API"""
        try:
            # Set the current task
            response = requests.post(
                f"{self.api_url}/api/task",
                json={"task": self.task}
            )
            if not response.ok:
                logger.error(f"Failed to set task: {response.text}")
                return self.state.history

            while not self.state.stopped and self.state.n_steps < max_steps:
                # Get latest analysis
                response = requests.get(f"{self.api_url}/api/analysis")
                if response.ok:
                    analysis = response.json()
                    
                    # Log the analysis
                    logger.info(f"Analysis: {json.dumps(analysis, indent=2)}")
                    
                    # Update agent state
                    self.state.n_steps += 1
                    
                    # Check for Hello world trigger or distraction
                    current_state = await self.browser_context.get_state()
                    if current_state and current_state.active_element:
                        current_input = current_state.active_element.get("value", "")
                        if await self.check_hello_world(current_input):
                            continue

                    # Check for distractions
                    if not analysis.get("focused", True):
                        logger.warning(f"Distraction detected: {analysis.get('activeDistractions')}")
                        
                        # Add to history
                        self.state.history.add_error(
                            f"Distraction detected: {analysis.get('activeDistractions')}\n"
                            f"Reasoning: {analysis.get('reasoning')}"
                        )

                await asyncio.sleep(2)  # Wait before next check

            return self.state.history

        except Exception as e:
            logger.error(f"Error in distraction detection: {str(e)}")
            self.state.history.add_error(str(e))
            return self.state.history