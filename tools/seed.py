from tools.db import get_conn, init_db

# DEMO DATA: Demo General Store ki qeematein sirf demo ke liye hain
PRODUCTS = [
    # name, aliases, category, unit, price, stock
    ("Rice", "chawal,chaawal,rice,basmati", "grains", "kg", 320, 50),
    ("Eggs", "anday,ande,egg,eggs", "eggs_dairy", "dozen", 360, 8),
    ("Sugar", "cheeni,chini,sugar", "pantry", "kg", 150, 40),
    ("Tea", "chai patti,chai,tea", "beverages", "pack", 480, 25),
    ("Maida (Fine Flour)", "maida,flour", "grains", "kg", 130, 60),
    ("Milk", "doodh,milk", "eggs_dairy", "litre", 220, 30),
    ("Cooking Oil", "cooking oil,tel,oil", "oil_ghee", "litre", 520, 20),
    ("Banaspati Ghee", "banaspati,banaspati ghee,vegetable ghee", "oil_ghee", "kg", 650, 15),
    ("Desi Ghee", "desi ghee,asli ghee,ghee", "oil_ghee", "kg", 1400, 5),
    ("Salt", "namak,salt", "pantry", "kg", 60, 40),
    ("Red Chilli Powder", "lal mirch,mirch,chilli powder", "spices", "pack", 120, 30),
    ("Biscuits", "biscuit,biscuits", "snacks", "pack", 50, 60),
    ("Bread", "double roti,bread,roti", "bakery", "pack", 140, 12),
    ("Soap", "sabun,soap", "household", "piece", 110, 35),
    ("Washing Powder", "surf,washing powder", "household", "kg", 450, 18),
]


def seed():
    init_db()
    conn = get_conn()
    conn.execute("DELETE FROM products")
    conn.execute("DELETE FROM orders")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='orders'")
    conn.executemany(
        "INSERT INTO products (name, aliases, category, unit, price, stock) VALUES (?,?,?,?,?,?)",
        PRODUCTS)
    conn.commit()
    conn.close()
    print(f"{len(PRODUCTS)} demo products ban gaye, purane orders saaf.")


if __name__ == "__main__":
    seed()