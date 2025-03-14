"""Run `pip install duckduckgo-search sqlalchemy pgvector pypdf openai` to install dependencies."""

from phi.agent import Agent
from phi.embedder.azure_openai import AzureOpenAIEmbedder
from phi.model.azure import AzureOpenAIChat
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=PgVector(
        table_name="recipes",
        db_url=db_url,
        embedder=AzureOpenAIEmbedder(),
    ),
)
knowledge_base.load(recreate=False)  # Comment out after first run

agent = Agent(model=AzureOpenAIChat(id="gpt-4o"), knowledge=knowledge_base, show_tool_calls=True, debug_mode=True)
agent.print_response("How to make Thai curry?", markdown=True)
