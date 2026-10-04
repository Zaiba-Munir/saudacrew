import json
from crewai import Agent, Task, Crew
from agents.llm_config import get_llm
from tools.db import get_orders_today, get_conn

LOW_STOCK_LIMIT = 10


def collect_stats():
    """Saare numbers Python nikalta hai, LLM nahi."""
    orders = get_orders_today()
    total_sales = sum(o["total"] for o in orders)
    sold = {}
    for o in orders:
        for ln in json.loads(o["items_json"]):
            key = (ln["name"], ln["unit"])
            sold[key] = sold.get(key, 0) + ln["qty"]
    best = max(sold.items(), key=lambda x: x[1]) if sold else None
    conn = get_conn()
    low = conn.execute("SELECT name, stock, unit FROM products WHERE stock <= ? ORDER BY stock",
                       (LOW_STOCK_LIMIT,)).fetchall()
    conn.close()
    return {
        "orders_count": len(orders),
        "total_sales": total_sales,
        "best_seller": {"name": best[0][0], "qty": best[1], "unit": best[0][1]} if best else None,
        "low_stock": [dict(r) for r in low],
    }


def daily_report():
    stats = collect_stats()
    facts = [f"Aaj ke orders: {stats['orders_count']}",
             f"Aaj ki total sale: Rs {stats['total_sales']:g}"]
    b = stats["best_seller"]
    facts.append(f"Sab se zyada bika: {b['name']} ({b['qty']:g} {b['unit']})" if b else "Sab se zyada bika: abhi koi sale nahi")
    if stats["low_stock"]:
        facts.append("Kam stock wali cheezein: " + ", ".join(
            f"{x['name']} ({x['stock']:g} {x['unit']} bacha)" for x in stats["low_stock"]))
    else:
        facts.append("Kam stock wali cheezein: koi nahi")

    rules = """
Tum dukaan ke owner ke liye Report Agent ho. Neeche diye FACTS se Roman Urdu mein chhoti si daily report likho.
Rules:
- Sirf FACTS ke numbers use karo, koi number apni taraf se mat banao.
- Aakhir mein 1-2 lines ka restock mashwara do (kam stock wali cheezein dobara mangwane ka).
- Markdown ya ** mat use karo. 5 se 8 lines. Price ke saath "Rs".
"""
    agent = Agent(role="Report Agent", goal="Owner ke liye saaf daily report banana",
                  backstory="Tum ek hoshiyar munshi ho jo dukaan ka hisaab rakhta hai.",
                  llm=get_llm(), verbose=False)
    task = Task(description=rules + "\n\nFACTS:\n" + "\n".join(facts),
                expected_output="Owner ke liye Roman Urdu daily report", agent=agent)
    text = str(Crew(agents=[agent], tasks=[task], verbose=False).kickoff()).strip()
    return {"stats": stats, "text": text}