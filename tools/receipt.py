import io
import json
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from tools.db import get_conn


def get_order(order_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    order = dict(row)
    order["lines"] = json.loads(order["items_json"])
    return order


def receipt_pdf(order_id):
    order = get_order(order_id)
    if order is None:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A5)
    w, h = A5
    y = h - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w / 2, y, "Demo General Store")
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawCentredString(w / 2, y, "Powered by SaudaCrew")
    y -= 22
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(w / 2, y, f"Order #{order['id']}")
    y -= 14
    c.setFont("Helvetica", 9)
    c.drawCentredString(w / 2, y, order["created_at"].replace("T", " "))
    y -= 12
    c.drawCentredString(w / 2, y, f"Customer: {order['customer']}")
    y -= 24

    c.setFont("Helvetica-Bold", 9)
    c.drawString(30, y, "Item")
    c.drawRightString(w - 150, y, "Qty")
    c.drawRightString(w - 95, y, "Price")
    c.drawRightString(w - 30, y, "Total")
    y -= 4
    c.line(30, y, w - 30, y)
    y -= 14

    c.setFont("Helvetica", 9)
    for ln in order["lines"]:
        c.drawString(30, y, str(ln["name"])[:28])
        c.drawRightString(w - 150, y, f"{ln['qty']:g} {ln['unit']}")
        c.drawRightString(w - 95, y, f"{ln['price']:g}")
        c.drawRightString(w - 30, y, f"{ln['line_total']:g}")
        y -= 14
        if y < 90:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = h - 40

    c.line(30, y, w - 30, y)
    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30, y, "TOTAL (Rs)")
    c.drawRightString(w - 30, y, f"{order['total']:g}")
    y -= 30
    c.setFont("Helvetica", 9)
    c.drawCentredString(w / 2, y, "Thank you! Please visit again.")
    y -= 12
    c.drawCentredString(w / 2, y, "DEMO DATA: not a real bill")
    c.save()
    return buf.getvalue()