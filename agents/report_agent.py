import json
from crewai import Agent, Task, Crew
from agents.llm_config import get_llm
from tools.db import get_orders_today, get_conn

LOW_STOCK_LIMIT = 10


def collect_stats():
    """All numbers are calculated by Python, not by the LLM."""
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
    facts = [f"Orders today: {stats['orders_count']}",
             f"Total sales today: Rs {stats['total_sales']:g}"]
    b = stats["best_seller"]
    facts.append(f"Best seller: {b['name']} ({b['qty']:g} {b['unit']})" if b else "Best seller: no sales yet")
    if stats["low_stock"]:
        facts.append("Low stock items: " + ", ".join(
            f"{x['name']} ({x['stock']:g} {x['unit']} left)" for x in stats["low_stock"]))
    else:
        facts.append("Low stock items: none")

    rules = """
You are the Report Agent for a shop owner. Write a short daily report in simple English using only the FACTS below.
Rules:
- Use only the numbers in the FACTS. Never invent a number.
- End with 1 or 2 lines of restocking advice for the low stock items.
- No markdown and no ** symbols. 5 to 8 short lines. Write "Rs" before prices.
"""
    agent = Agent(role="Report Agent", goal="Write a clear daily report for the shop owner",
                  backstory="You are a smart shop accountant who keeps the shop's records.",
                  llm=get_llm(), verbose=False)
    task = Task(description=rules + "\n\nFACTS:\n" + "\n".join(facts),
                expected_output="A short daily report in English for the shop owner", agent=agent)
    text = str(Crew(agents=[agent], tasks=[task], verbose=False).kickoff()).strip()
    return {"stats": stats, "text": text}