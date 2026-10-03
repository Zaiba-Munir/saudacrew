
import groq_fix
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()

llm = LLM(
    model="groq/openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
)

agent = Agent(
    role="Dukaan Helper",
    goal="Customer ko Roman Urdu mein polite jawab dena",
    backstory="Tum ek dost jaisa dukaan ka helper ho.",
    llm=llm,
)

task = Task(
    description="Customer ko Roman Urdu mein salam karo aur poocho ke wo kya order karna chahta hai.",
    expected_output="Ek chhota polite Roman Urdu message",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task])
print(crew.kickoff())