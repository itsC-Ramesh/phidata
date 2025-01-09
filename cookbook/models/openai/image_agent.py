from agno.agent import Agent
from agno.agent.media import ImageInput
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGo

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo()],
    markdown=True,
)

agent.print_response(
    "Tell me about this image and give me the latest news about it.",
    images=[
        ImageInput(url="https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg")
    ],
    stream=True,
)
