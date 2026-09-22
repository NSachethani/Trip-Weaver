import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0,
)
