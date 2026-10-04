import time
from agents.order_agent import parse_order
from agents.stock_agent import check_order
from agents.invoice_agent import make_invoice
from agents.reply_agent import write_reply
from tools.db import save_order


def handle_message(message):
    """Manager: agents ko order mein chalata hai aur trace banata hai. Order abhi save NAHI hota."""
    trace = []

    def step(agent, action, fn, detail=lambda out: ""):
        t0 = time.time()
        out = fn()
        trace.append({"agent": agent, "action": action, "detail": detail(out),
                      "seconds": round(time.time() - t0, 1)})
        return out

    try:
        parsed = step("Order Agent", "Message se items nikale",
                      lambda: parse_order(message),
                      lambda o: f"{len(o['items'])} item(s) mile")
        stock = step("Stock Agent", "Stock check kiya aur faisla liya",
                     lambda: check_order(parsed),
                     lambda o: f"decision: {o['decision']}, masle: {len(o['issues'])}")
        bill = step("Invoice Agent", "Database ki prices se bill banaya",
                    lambda: make_invoice(stock["lines"]),
                    lambda o: f"total: Rs {o['total']:g}")
        reply = step("Reply Agent", "Customer ke liye jawab likha",
                     lambda: write_reply(message, bill, stock["issues"], stock["notes"]))
    except Exception as e:
        trace.append({"agent": "Manager", "action": "Error sambhala", "detail": str(e)[:150], "seconds": 0})
        return {"parsed": None, "bill": {"lines": [], "total": 0}, "issues": [], "decision": "error",
                "reply": "Maaf kijiye, abhi kuch masla aa gaya. Dobara koshish karein.", "trace": trace}

    return {"parsed": parsed, "bill": bill, "issues": stock["issues"],
            "decision": stock["decision"], "reply": reply, "trace": trace}


def confirm_order(result, customer="Demo Customer"):
    """Customer ke Confirm karne ke baad hi order save aur stock kam hota hai."""
    if not result["bill"]["lines"]:
        return None
    return save_order(result["bill"]["lines"], result["bill"]["total"], customer)