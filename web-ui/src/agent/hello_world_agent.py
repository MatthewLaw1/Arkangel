import logging
import asyncio
from typing import Optional
from .custom_agent import CustomAgent
from langchain_core.language_models.chat_models import BaseChatModel
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller

logger = logging.getLogger(__name__)

class HelloWorldAgent(CustomAgent):
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
        self.last_input = ""

    async def check_hello_world(self, text: str) -> bool:
        """Check if input matches 'Hello world'"""
        if text.lower() == "hello world":
            logger.info("Hello world trigger detected")
            return True
        return False

    async def run(self, max_steps: int = 100) -> AgentHistoryList:
        """Monitor for 'Hello world' input"""
        try:
            while not self.state.stopped and self.state.n_steps < max_steps:
                # Get latest input from the browser context
                current_state = await self.browser_context.get_state()
                if current_state and current_state.active_element:
                    current_input = current_state.active_element.get("value", "")
                    
                    # Check if input has changed and matches trigger
                    if current_input != self.last_input:
                        self.last_input = current_input
                        if await self.check_hello_world(current_input):
                            # Launch web UI in native browser
                            await self.browser_context.execute_script("""
                                window.open('http://localhost:5000', '_blank');
                            """)
                            
                            # Add to history
                            self.state.history.add_error(
                                "Hello world trigger detected - launched web UI"
                            )

                await asyncio.sleep(1)  # Check every second

            return self.state.history

        except Exception as e:
            logger.error(f"Error in hello world detection: {str(e)}")
            self.state.history.add_error(str(e))
            return self.state.history