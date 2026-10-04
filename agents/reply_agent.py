from crewai import Agent, Task, Crew
from agents.llm_config import get_llm

RULES = """
Tum ek dukaan ke Reply Agent ho. Tum customer ko chhota, polite jawab likhte ho.

Rules:
- Customer ki zubaan mein jawab do: agar customer ne Roman Urdu likha to Roman Urdu mein, English likhi to English mein.
- Sirf neeche di hui FACTS ke naam, quantity aur numbers use karo. Koi price, total ya stock apni taraf se mat banao.
- Agar bill hai: items, total batao aur aakhir mein usi zubaan mein confirm karne ko poochho (Roman Urdu mein "Confirm kar dein?", English mein "Shall I confirm your order?").
- Agar koi masla hai (stock kam, item nahi, budget, quantity missing): saaf batao, aur agar alternatives diye hain to unke naam aur price pesh karo.
- Agar koi item bill mein nahi hai (jaise sirf hello): dosti se poochho ke kya chahiye.
- 3 se 6 chhoti lines. Markdown, bullets ya ** ka istemal mat karo. Price ke saath "Rs" likho.
- Sirf customer ko bhejne wala message likho, koi explanation nahi.
"""


def build_facts(message, bill, issues, notes):
    out = [f'Customer ka message: "{message}"']
    if bill["lines"]:
        out.append("Bill:")
        for l in bill["lines"]:
            out.append(f"- {l['name']}: {l['qty']:g} {l['unit']} x Rs {l['price']:g} = Rs {l['line_total']:g}")
        out.append(f"Total: Rs {bill['total']:g}")
    else:
        out.append("Bill: koi item bill mein nahi.")
    for iss in issues:
        s = f"Masla ({iss['type']}): {iss['message']}"
        alts = iss.get("alternatives") or []
        if alts:
            s += " | Alternatives: " + ", ".join(f"{a['name']} Rs {a['price']:g}/{a['unit']}" for a in alts)
        out.append(s)
    for n in notes:
        out.append("Note: " + n)
    return "\n".join(out)


def write_reply(message, bill, issues, notes):
    facts = build_facts(message, bill, issues, notes)
    agent = Agent(
        role="Reply Agent",
        goal="Customer ko saaf, polite aur durust jawab dena",
        backstory="Tum ek dost jaisa dukaan ka salesperson ho jo Roman Urdu aur English dono bolta hai.",
        llm=get_llm(),
        verbose=False,
    )
    task = Task(
        description=RULES + "\n\nFACTS:\n" + facts + "\n\nAb customer ke liye reply likho.",
        expected_output="Customer ke liye ek chhota polite message",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    return str(crew.kickoff()).strip()