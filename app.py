import uuid
import json
from flask import Flask, render_template, request, jsonify, abort

from tools.db import init_db, get_conn
from tools.seed import seed
from agents.manager import handle_message, confirm_order
from agents.report_agent import daily_report

app = Flask(__name__)

# Server start par database tayyar karo (khali ho to demo products bana do)
init_db()
_c = get_conn()
_n = _c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
_c.close()
if _n == 0:
    seed()

PENDING = {}  # token -> result (confirm hone tak yahan rehta hai)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/message", methods=["POST"])
def api_message():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()
    history = payload.get("history") or []
    if not message:
        return jsonify({"error": "Message khali hai"}), 400
    if not isinstance(history, list):
        history = []

    result = handle_message(message, history)
    token = None
    over_budget = any(i["type"] == "over_budget" for i in result["issues"])
    if result["bill"]["lines"] and not over_budget:
        token = uuid.uuid4().hex
        PENDING[token] = result
        if len(PENDING) > 200:
            PENDING.pop(next(iter(PENDING)))

    return jsonify({
        "reply": result["reply"],
        "bill": result["bill"],
        "issues": result["issues"],
        "decision": result["decision"],
        "trace": result["trace"],
        "token": token,
    })


@app.route("/api/confirm", methods=["POST"])
def api_confirm():
    token = (request.get_json(silent=True) or {}).get("token")
    result = PENDING.pop(token, None)
    if result is None:
        return jsonify({"error": "Ye order pehle hi confirm ho chuka hai ya mila nahi."}), 400
    order_id = confirm_order(result)
    return jsonify({"order_id": order_id, "receipt_url": f"/receipt/{order_id}"})


@app.route("/api/report")
def api_report():
    return jsonify(daily_report())


@app.route("/receipt/<int:order_id>")
def receipt(order_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    if row is None:
        abort(404)
    order = dict(row)
    lines = json.loads(order["items_json"])
    return render_template("receipt.html", order=order, lines=lines)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)