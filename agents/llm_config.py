import os

# CrewAI ka "trace share karein?" wala sawal band karne ke liye (har call par 20 sec nahi rukna)
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

import groq_fix  # CrewAI + Groq bug ka fix, ye crewai se pehle import hona zaroori hai
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

MODEL = "groq/openai/gpt-oss-120b"


def get_llm():
    return LLM(model=MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)