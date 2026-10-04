from tools.db import get_conn, init_db

# DEMO DATA: Demo General Store ki qeematein sirf demo ke liye hain
# name, aliases, category, unit, price, stock, emoji
PRODUCTS = [
    ("Basmati Rice", "chawal,chaawal,rice,basmati,basmati rice", "Grains & Flour", "kg", 320, 50, "🍚"),
    ("Maida (Fine Flour)", "maida,flour,fine flour", "Grains & Flour", "kg", 130, 60, "🌾"),
    ("Suji (Semolina)", "suji,sooji,semolina", "Grains & Flour", "kg", 140, 30, "🌾"),
    ("Besan (Gram Flour)", "besan,gram flour", "Grains & Flour", "kg", 260, 25, "🌾"),
    ("Oats", "oats", "Grains & Flour", "pack", 380, 20, "🥣"),
    ("Cornflakes", "cornflakes,corn flakes", "Grains & Flour", "pack", 450, 18, "🥣"),

    ("Daal Chana", "chana daal,daal chana,chane ki daal", "Pulses", "kg", 280, 40, "🫘"),
    ("Daal Masoor", "masoor daal,daal masoor,masoor ki daal", "Pulses", "kg", 300, 35, "🫘"),
    ("Daal Mash", "mash daal,daal mash,mash ki daal", "Pulses", "kg", 420, 25, "🫘"),
    ("Daal Moong", "moong daal,daal moong,moong ki daal", "Pulses", "kg", 330, 30, "🫘"),
    ("Kabuli Chana", "kabuli chana,chana,chickpeas", "Pulses", "kg", 340, 30, "🫘"),

    ("Milk", "doodh,milk", "Dairy", "litre", 220, 30, "🥛"),
    ("Yogurt (Dahi)", "dahi,yogurt,yoghurt", "Dairy", "kg", 260, 20, "🥛"),
    ("Butter", "butter,makhan", "Dairy", "pack", 320, 15, "🧈"),
    ("Cheese Slices", "cheese,cheese slices", "Dairy", "pack", 450, 6, "🧀"),

    ("Eggs", "anday,ande,egg,eggs", "Eggs", "dozen", 360, 8, "🥚"),
    ("Desi Eggs", "desi anday,desi ande,desi eggs", "Eggs", "dozen", 420, 15, "🥚"),

    ("Cooking Oil", "cooking oil,tel,oil", "Oil & Ghee", "litre", 520, 20, "🛢️"),
    ("Banaspati Ghee", "banaspati,banaspati ghee,vegetable ghee", "Oil & Ghee", "kg", 650, 15, "🧈"),
    ("Desi Ghee", "desi ghee,asli ghee,ghee", "Oil & Ghee", "kg", 1400, 5, "🧈"),
    ("Olive Oil", "olive oil,zaitoon ka tel", "Oil & Ghee", "bottle", 1300, 10, "🫒"),

    ("Salt", "namak,salt", "Spices", "kg", 60, 40, "🧂"),
    ("Red Chilli Powder", "lal mirch,chilli powder,red chilli,red chilli powder", "Spices", "pack", 120, 30, "🌶️"),
    ("Turmeric Powder", "haldi,turmeric", "Spices", "pack", 90, 30, "🟡"),
    ("Coriander Powder", "dhania,coriander,dhania powder", "Spices", "pack", 100, 25, "🌿"),
    ("Cumin Seeds", "zeera,cumin", "Spices", "pack", 110, 25, "🌿"),
    ("Black Pepper", "kali mirch,black pepper", "Spices", "pack", 150, 20, "⚫"),
    ("Garam Masala", "garam masala", "Spices", "pack", 130, 25, "🌶️"),
    ("Biryani Masala", "biryani masala", "Spices", "pack", 90, 30, "🍛"),

    ("Tea", "chai patti,chai,tea", "Beverages", "pack", 480, 25, "🍵"),
    ("Green Tea", "green tea,green chai", "Beverages", "pack", 350, 15, "🍵"),
    ("Coffee", "coffee,coffee jar", "Beverages", "jar", 650, 12, "☕"),
    ("Mango Juice", "juice,mango juice,aam ka juice", "Beverages", "litre", 250, 20, "🧃"),
    ("Cold Drink", "cold drink,soft drink,soda,cola", "Beverages", "bottle", 160, 40, "🥤"),
    ("Mineral Water", "mineral water,water,pani", "Beverages", "bottle", 80, 60, "💧"),

    ("Sugar", "cheeni,chini,sugar", "Pantry", "kg", 150, 40, "🍬"),
    ("Gur (Jaggery)", "gur,jaggery", "Pantry", "kg", 220, 15, "🟤"),
    ("Honey", "shahad,honey", "Pantry", "jar", 750, 10, "🍯"),

    ("Biscuits", "biscuit,biscuits", "Snacks & Biscuits", "pack", 50, 60, "🍪"),
    ("Chips", "chips,crisps", "Snacks & Biscuits", "pack", 60, 50, "🥔"),
    ("Chocolate Bar", "chocolate,chocolate bar", "Snacks & Biscuits", "piece", 100, 40, "🍫"),
    ("Instant Noodles", "noodles,instant noodles", "Snacks & Biscuits", "pack", 70, 45, "🍜"),
    ("Nimko", "nimko,namkeen", "Snacks & Biscuits", "pack", 120, 25, "🥜"),

    ("Bread", "double roti,bread,roti", "Bakery", "pack", 140, 12, "🍞"),
    ("Rusk", "rusk,toast rusk", "Bakery", "pack", 180, 18, "🍞"),

    ("Potato", "aloo,potato", "Fruits & Vegetables", "kg", 90, 50, "🥔"),
    ("Onion", "pyaz,onion", "Fruits & Vegetables", "kg", 120, 50, "🧅"),
    ("Tomato", "tamatar,tomato", "Fruits & Vegetables", "kg", 140, 40, "🍅"),
    ("Banana", "kela,kele,banana", "Fruits & Vegetables", "dozen", 200, 20, "🍌"),
    ("Apple", "saib,apple", "Fruits & Vegetables", "kg", 320, 25, "🍎"),
    ("Lemon", "nimbu,lemon", "Fruits & Vegetables", "kg", 300, 10, "🍋"),

    ("Soap", "sabun,soap", "Household", "piece", 110, 35, "🧼"),
    ("Washing Powder", "surf,washing powder", "Household", "kg", 450, 18, "🧺"),
    ("Dishwash Liquid", "dishwash,dish wash,dishwash liquid", "Household", "bottle", 280, 20, "🍽️"),
    ("Tissue Box", "tissue,tissues,tissue box", "Household", "box", 150, 30, "🧻"),

    ("Shampoo", "shampoo", "Personal Care", "bottle", 450, 15, "🧴"),
    ("Toothpaste", "toothpaste,paste,manjan", "Personal Care", "tube", 220, 30, "🪥"),
    ("Toothbrush", "toothbrush,brush", "Personal Care", "piece", 90, 40, "🪥"),
]


def seed():
    # Purane tables hata kar naye banao (taake naya emoji column aa jaye)
    conn = get_conn()
    conn.execute("DROP TABLE IF EXISTS products")
    conn.execute("DROP TABLE IF EXISTS orders")
    conn.commit()
    conn.close()
    init_db()
    conn = get_conn()
    conn.executemany(
        "INSERT INTO products (name, aliases, category, unit, price, stock, emoji) VALUES (?,?,?,?,?,?,?)",
        PRODUCTS)
    conn.commit()
    conn.close()
    print(f"{len(PRODUCTS)} demo products ban gaye, purane orders saaf.")


if __name__ == "__main__":
    seed()