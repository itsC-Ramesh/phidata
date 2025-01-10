"""Run `pip install duckduckgo-search` to install dependencies."""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGo

agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), tools=[DuckDuckGo()], show_tool_calls=True, markdown=True)
agent.print_response("Whats happening in France?", stream=True)