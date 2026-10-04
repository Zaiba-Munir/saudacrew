import sqlite3, json, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "shop.db")


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        aliases TEXT NOT NULL,
        category TEXT NOT NULL,
        unit TEXT NOT NULL,
        price REAL NOT NULL,
        stock REAL NOT NULL,
        emoji TEXT NOT NULL DEFAULT '')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        customer TEXT,
        items_json TEXT NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL)""")
    conn.commit()
    conn.close()


def find_product(name):
    """Customer ke lafz se product dhoondo (chawal, chaawal, rice sab same)."""
    name = name.strip().lower()
    conn = get_conn()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    for r in rows:  # pehle exact match
        names = [a.strip() for a in r["aliases"].split(",")] + [r["name"].lower()]
        if name in names:
            return dict(r)
    for r in rows:  # phir partial match
        names = [a.strip() for a in r["aliases"].split(",")] + [r["name"].lower()]
        if any(len(a) >= 3 and a in name for a in names):
            return dict(r)
    return None


def check_stock(name, qty):
    p = find_product(name)
    if p is None:
        return {"status": "not_found", "requested_name": name, "requested": qty}
    if p["stock"] <= 0:
        status = "out"
    elif p["stock"] < qty:
        status = "short"
    else:
        status = "ok"
    return {"status": status, "product": p, "requested": qty, "available": p["stock"]}


def calculate_total(items):
    """items = [{'product_id': 1, 'qty': 2}, ...]. Price sirf database se."""
    conn = get_conn()
    lines, total = [], 0
    for it in items:
        p = conn.execute("SELECT * FROM products WHERE id=?", (it["product_id"],)).fetchone()
        line_total = p["price"] * it["qty"]
        total += line_total
        lines.append({"product_id": p["id"], "name": p["name"], "unit": p["unit"],
                      "qty": it["qty"], "price": p["price"], "line_total": line_total})
    conn.close()
    return {"lines": lines, "total": total}


def save_order(lines, total, customer="Demo Customer", status="Received"):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO orders (created_at, customer, items_json, total, status) VALUES (?,?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), customer, json.dumps(lines), total, status))
    for ln in lines:  # stock kam karo
        conn.execute("UPDATE products SET stock = stock - ? WHERE id=?", (ln["qty"], ln["product_id"]))
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    return order_id


def get_orders_today():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    rows = conn.execute("SELECT * FROM orders WHERE created_at LIKE ?", (today + "%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_alternatives(category, max_price, exclude_id, limit=3):
    """Same category, budget ke andar, stock available."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM products WHERE category=? AND price<=? AND id!=? AND stock>0 ORDER BY price DESC LIMIT ?",
        (category, max_price, exclude_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_catalog_text():
    """Assistant ko dukaan ki poori list dikhane ke liye (naam, price, stock)."""
    conn = get_conn()
    rows = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    conn.close()
    out = []
    for r in rows:
        stock = "in stock" if r["stock"] > 0 else "OUT OF STOCK"
        out.append(f"- {r['name']} ({r['category']}): Rs {r['price']:g} per {r['unit']}, {stock}")
    return "\n".join(out)