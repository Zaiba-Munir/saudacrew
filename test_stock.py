from agents.stock_agent import check_order
from agents.invoice_agent import make_invoice

CASES = {
    "1. Normal order": {"items": [{"name": "chawal", "qty": 2, "unit": "kg"},
                                  {"name": "anday", "qty": 1, "unit": "dozen"}], "budget": None},
    "2. Stock kam (10 dozen anday)": {"items": [{"name": "anday", "qty": 10, "unit": "dozen"}], "budget": None},
    "3. Item shop mein nahi + normal": {"items": [{"name": "aata", "qty": None, "unit": None},
                                                  {"name": "chawal", "qty": 1, "unit": "kg"}], "budget": None},
    "4. Quantity missing": {"items": [{"name": "chai patti", "qty": None, "unit": None}], "budget": None},
    "5. Budget se mehnga (desi ghee)": {"items": [{"name": "desi ghee", "qty": 1, "unit": "kg"}], "budget": 800},
    "6. Do naam, ek item": {"items": [{"name": "chaawal", "qty": 2, "unit": "kg"},
                                      {"name": "rice", "qty": 1, "unit": "kg"}], "budget": None},
}

for title, parsed in CASES.items():
    res = check_order(parsed)
    bill = make_invoice(res["lines"])
    print("\n" + title)
    print("   decision:", res["decision"], "| total:", bill["total"])
    for ln in bill["lines"]:
        print("   bill:", ln["name"], ln["qty"], ln["unit"], "x", ln["price"], "=", ln["line_total"])
    for iss in res["issues"]:
        alts = [a["name"] for a in iss.get("alternatives", [])]
        print("   issue:", iss["type"], "-", iss["message"], "| alternatives:", alts)