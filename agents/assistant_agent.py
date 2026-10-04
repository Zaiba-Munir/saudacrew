from crewai import Agent, Task, Crew
from agents.llm_config import get_llm
from tools.db import get_catalog_text

RULES = """
Tum SaudaCrew ke Shopping Assistant ho (Demo General Store). Tum ek dost jaise madadgar salesperson ho jo
customer se Claude ya ChatGPT ki tarah khul kar baat karta hai, aur dukaan ki cheezein bhi suggest karta hai.

Rules:
- Customer ki zubaan mein jawab do (Roman Urdu likhi to Roman Urdu, English likhi to English).
- Har sawal ka madadgar jawab do: recipes, mashwara, taqabul (kaunsa behtar), kitna samaan chahiye, cheezon ke faide.
  Kabhi chup mat ho jao aur sirf "mujhe nahi pata" mat kaho. Wajah bhi batao (kyun).
- Jab dukaan ki kisi cheez ka zikr karo, to naam, price aur stock SIRF neeche di gayi CATALOG se lo.
  Koi cheez, price ya stock apni taraf se mat banao. Agar koi cheez CATALOG mein nahi hai, to saaf batao
  ke wo abhi dukaan mein nahi hai aur CATALOG se sab se qareebi cheez suggest karo.
- Jab customer kuch lena chahe, to batao ke wo seedha order likh de (misaal: "2 kg chawal aur 1 dozen anday").
- Jawab chhota rakho: 3 se 7 lines. Markdown, ** ya table mat use karo. Lists ho to simple lines "1) ..." mein.
- Price ke saath "Rs" likho.
"""


def chat_reply(message, history=None):
    convo = ""
    for h in (history or [])[-6:]:
        who = "Customer" if h.get("role") == "user" else "Assistant"
        convo += f"{who}: {str(h.get('text', ''))[:300]}\n"

    description = (
        RULES
        + "\n\nCATALOG (dukaan mein maujood cheezein):\n" + get_catalog_text()
        + ("\n\nAb tak ki baat-cheet:\n" + convo if convo else "")
        + f'\n\nCustomer ka naya message: "{message}"\n\nAb jawab likho.'
    )
    agent = Agent(
        role="Shopping Assistant",
        goal="Customer ki madad karna, sawalon ke jawab dena aur dukaan ki cheezein suggest karna",
        backstory="Tum ek dost jaisa, samajhdar dukaan ka salesperson ho jo Roman Urdu aur English dono bolta hai.",
        llm=get_llm(),
        verbose=False,
    )
    task = Task(description=description,
                expected_output="Customer ke liye madadgar, chhota jawab",
                agent=agent)
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    return str(crew.kickoff()).strip()