import json
from crewai import Agent, Task, Crew
from agents.llm_config import get_llm

INSTRUCTIONS = """
Tum ek dukaan ke Order Agent ho. Customer Roman Urdu, English ya dono mix mein order likhta hai.
Message se items, quantity aur unit nikalo.

Rules:
- Sirf ek valid JSON object wapas do. Koi aur text, explanation ya ``` mat likho.
- Format:
  {"items": [{"name": "...", "qty": number ya null, "unit": "kg/dozen/litre/pack/piece ya null"}],
   "budget": number ya null}
- "name" mein wohi lafz rakho jo customer ne likha (chawal, chaawal, rice, anday waghera). Tum khud naam mat badlo.
- Agar customer ne quantity nahi batayi, to qty null rakho. Quantity apni taraf se mat banao.
- Agar customer ne budget bataya (jaise "budget 800 hai"), to budget mein number do, warna null.
- Agar message mein koi item nahi hai, to items khali list [] rakho.
- Roman Urdu ginti: ek=1, do=2, teen=3, char=4, panch=5, aadha=0.5, dedh=1.5. Agar item ke saath "ek" likha hai (jaise "ek sabun"), to qty 1 hai.
- Dhyan do: "bhej do", "de do", "la do" mein "do" ka matlab "send/de" hai, number 2 nahi. Sirf tab 2 maano jab "do" kisi item se pehle ginti ke tor par aaye (jaise "do packet biscuit").
- Agar unit nahi batayi aur item ginti wala hai (sabun, biscuit), to unit "piece" rakho.

Misalein:
Message: "2 kilo chawal aur 1 dozen anday bhej do"
{"items": [{"name": "chawal", "qty": 2, "unit": "kg"}, {"name": "anday", "qty": 1, "unit": "dozen"}], "budget": null}

Message: "mujhe cheeni 5 kilo aur chai patti chahiye"
{"items": [{"name": "cheeni", "qty": 5, "unit": "kg"}, {"name": "chai patti", "qty": null, "unit": null}], "budget": null}

Message: "1 kilo desi ghee chahiye, budget 800 hai"
{"items": [{"name": "desi ghee", "qty": 1, "unit": "kg"}], "budget": 800}

Message: "send me 3 kg sugar and 2 litre milk"
{"items": [{"name": "sugar", "qty": 3, "unit": "kg"}, {"name": "milk", "qty": 2, "unit": "litre"}], "budget": null}

Message: "ek sabun aur do packet biscuit bhej do"
{"items": [{"name": "sabun", "qty": 1, "unit": "piece"}, {"name": "biscuit", "qty": 2, "unit": "pack"}], "budget": null}
"""


def extract_json(text):
    """LLM ke jawab se JSON nikalo aur check karo."""
    try:
        start, end = text.index("{"), text.rindex("}") + 1
        data = json.loads(text[start:end])
    except Exception:
        return {"items": [], "budget": None, "error": "JSON samajh nahi aaya", "raw": text}

    clean = []
    for it in data.get("items", []):
        name = str(it.get("name", "")).strip()
        if not name:
            continue
        qty = it.get("qty")
        qty = float(qty) if isinstance(qty, (int, float)) else None
        clean.append({"name": name, "qty": qty, "unit": it.get("unit")})
    budget = data.get("budget")
    budget = float(budget) if isinstance(budget, (int, float)) else None
    return {"items": clean, "budget": budget}


def parse_order(message):
    agent = Agent(
        role="Order Agent",
        goal="Customer ke message se items aur quantity sahi nikalna",
        backstory="Tum Pakistani dukaan ke tajurbakar helper ho jo Roman Urdu aur English dono samajhta hai.",
        llm=get_llm(),
        verbose=False,
    )
    task = Task(
        description=INSTRUCTIONS + f'\n\nAb ye message process karo:\nMessage: "{message}"',
        expected_output="Sirf valid JSON object",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    return extract_json(str(crew.kickoff()))