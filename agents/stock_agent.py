from tools.db import find_product, find_alternatives

UNIT_MAP = {"kilo": "kg", "kg": "kg", "kgs": "kg", "packet": "pack", "pack": "pack",
            "ltr": "litre", "liter": "litre", "litre": "litre", "dozen": "dozen",
            "piece": "piece", "pcs": "piece"}


def _norm(u):
    if not u:
        return None
    u = str(u).strip().lower()
    return UNIT_MAP.get(u, u)


def check_order(parsed):
    """Decide from the Order Agent's JSON: what can be billed and what the problems are."""
    issues, notes = [], []
    merged = {}  # product_id -> {"product": p, "qty": total}

    # Step 1: find each item in the database and merge duplicates
    for it in parsed.get("items", []):
        name, qty = it["name"], it.get("qty")
        p = find_product(name)
        if p is None:
            issues.append({"type": "not_found", "item": name,
                           "message": f"{name} is not available in our shop"})
            continue
        if qty is None or qty <= 0:
            issues.append({"type": "missing_qty", "item": p["name"],
                           "message": f"How much {p['name']} do you need?"})
            continue
        u = _norm(it.get("unit"))
        if u and u != p["unit"]:
            notes.append(f"{p['name']} is sold per {p['unit']} (you wrote '{it.get('unit')}')")
        m = merged.setdefault(p["id"], {"product": p, "qty": 0})
        m["qty"] += qty

    # Step 2: stock check and decision
    lines = []
    for pid, m in merged.items():
        p, qty, stock = m["product"], m["qty"], m["product"]["stock"]
        if stock <= 0:
            alts = find_alternatives(p["category"], p["price"], p["id"])
            issues.append({"type": "out", "item": p["name"], "alternatives": alts,
                           "message": f"{p['name']} is out of stock"})
        elif stock < qty:
            lines.append({"product_id": pid, "qty": stock, "price": p["price"],
                          "category": p["category"], "name": p["name"]})
            alts = find_alternatives(p["category"], p["price"], p["id"])
            issues.append({"type": "short", "item": p["name"], "requested": qty,
                           "available": stock, "unit": p["unit"], "alternatives": alts,
                           "message": f"Only {stock:g} {p['unit']} of {p['name']} available (you asked for {qty:g})"})
        else:
            lines.append({"product_id": pid, "qty": qty, "price": p["price"],
                          "category": p["category"], "name": p["name"]})

    # Step 3: budget check
    budget = parsed.get("budget")
    if budget and lines:
        total = sum(l["price"] * l["qty"] for l in lines)
        if total > budget:
            big = max(lines, key=lambda l: l["price"] * l["qty"])
            others = total - big["price"] * big["qty"]
            remaining = budget - others
            max_unit = remaining / big["qty"] if remaining > 0 else 0
            alts = find_alternatives(big["category"], max_unit, big["product_id"]) if max_unit > 0 else []
            issues.append({"type": "over_budget", "item": big["name"], "budget": budget,
                           "total": total, "alternatives": alts,
                           "message": f"Total is Rs {total:g}, your budget is Rs {budget:g}"})

    clean_lines = [{"product_id": l["product_id"], "qty": l["qty"]} for l in lines]
    return {"lines": clean_lines, "issues": issues, "notes": notes,
            "decision": "ok" if not issues else "needs_confirmation"}