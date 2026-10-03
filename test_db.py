from tools.db import check_stock, calculate_total, save_order, find_alternatives, get_orders_today

print("1.", check_stock("chaawal", 2)["status"])
print("2.", check_stock("anday", 10)["status"])
print("3.", check_stock("daal", 1)["status"])

bill = calculate_total([{"product_id": 1, "qty": 2}, {"product_id": 2, "qty": 1}])
print("4.", bill["total"])

print("5.", [p["name"] for p in find_alternatives("oil_ghee", 800, exclude_id=9)])

oid = save_order(bill["lines"], bill["total"])
print("6. Order saved:", oid, "| aaj ke orders:", len(get_orders_today()))