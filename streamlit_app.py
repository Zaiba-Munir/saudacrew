import os
import streamlit as st

st.set_page_config(page_title="SaudaCrew", page_icon="🛒", layout="wide")

# Streamlit Cloud ke secrets se API key uthao (local par .env se aati hai)
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

from tools.db import init_db, get_conn, calculate_total, save_order, get_orders_today
from tools.seed import seed
from tools.receipt import receipt_pdf
from agents.manager import handle_message
from agents.report_agent import daily_report, collect_stats


@st.cache_resource
def setup():
    init_db()
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()
    if n == 0:
        seed()
    return True


setup()

for k, v in {"cart": {}, "chat": [], "last_order": None, "pending": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------- helpers ----------
def categories():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_products(search="", category="All"):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    conn.close()
    out = []
    for r in rows:
        p = dict(r)
        if category != "All" and p["category"] != category:
            continue
        if search:
            hay = (p["name"] + "," + p["aliases"] + "," + p["category"]).lower()
            if search.strip().lower() not in hay:
                continue
        out.append(p)
    return out


def get_product(pid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_to_cart(pid, qty=1.0):
    p = get_product(pid)
    if p is None:
        return
    cur = st.session_state.cart.get(pid, 0)
    new = min(cur + qty, p["stock"])
    if new > 0:
        st.session_state.cart[pid] = new


def change_qty(pid, delta):
    p = get_product(pid)
    cur = st.session_state.cart.get(pid, 0)
    new = cur + delta
    if new <= 0 or p is None:
        st.session_state.cart.pop(pid, None)
    else:
        st.session_state.cart[pid] = min(new, p["stock"])


def add_lines(lines):
    for ln in lines:
        add_to_cart(ln["product_id"], ln["qty"])


def clear_cart():
    st.session_state.cart = {}


def dismiss_order():
    st.session_state.last_order = None


def set_pending(text):
    st.session_state.pending = text


def render_result(i, r):
    bill = r["bill"]
    if bill["lines"]:
        rows = [{"Item": l["name"], "Qty": f"{l['qty']:g} {l['unit']}",
                 "Price": f"Rs {l['price']:,.0f}", "Total": f"Rs {l['line_total']:,.0f}"}
                for l in bill["lines"]]
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.markdown(f"**Total: Rs {bill['total']:,.0f}**")
    for iss in r["issues"]:
        text = iss["message"]
        alts = iss.get("alternatives") or []
        if alts:
            text += ". Alternatives: " + ", ".join(
                f"{a['name']} (Rs {a['price']:,.0f}/{a['unit']})" for a in alts)
        st.warning(text)
    over = any(x["type"] == "over_budget" for x in r["issues"])
    if bill["lines"]:
        if over:
            st.info("This order is over your budget, so it cannot be added. Pick an alternative and ask again.")
        else:
            st.button("➕ Add these items to my cart", key=f"addlines{i}",
                      on_click=add_lines, args=(bill["lines"],))
    with st.expander("🔍 Agent trace"):
        for t in r["trace"]:
            detail = f" ({t['detail']})" if t["detail"] else ""
            st.markdown(f"**{t['agent']}**: {t['action']}{detail} - {t['seconds']}s")


# ---------- sidebar: cart ----------
with st.sidebar:
    st.header("🛒 Your Cart")
    cart = st.session_state.cart
    total = 0.0
    if not cart:
        st.caption("Your cart is empty.")
    for pid, q in list(cart.items()):
        p = get_product(pid)
        if p is None:
            cart.pop(pid, None)
            continue
        line = p["price"] * q
        total += line
        st.markdown(f"**{p['emoji']} {p['name']}**")
        c1, c2, c3, c4 = st.columns([1, 1.6, 1, 2])
        c1.button("−", key=f"m{pid}", on_click=change_qty, args=(pid, -1.0))
        c2.markdown(f"{q:g} {p['unit']}")
        c3.button("+", key=f"p{pid}", on_click=change_qty, args=(pid, 1.0))
        c4.markdown(f"Rs {line:,.0f}")
    if cart:
        st.divider()
        st.markdown(f"### Total: Rs {total:,.0f}")
        cust = st.text_input("Your name (optional)", key="cust_name")
        if st.button("✅ Confirm Order", type="primary", use_container_width=True):
            lines = [{"product_id": pid, "qty": q} for pid, q in cart.items()]
            problem = None
            for ln in lines:
                p = get_product(ln["product_id"])
                if p["stock"] < ln["qty"]:
                    problem = f"{p['name']}: only {p['stock']:g} {p['unit']} left."
            if problem:
                st.error(problem)
            else:
                bill = calculate_total(lines)
                oid = save_order(bill["lines"], bill["total"], cust.strip() or "Demo Customer")
                st.session_state.cart = {}
                st.session_state.last_order = oid
                st.rerun()
        st.button("Clear cart", on_click=clear_cart, use_container_width=True)

# ---------- header ----------
st.title("🛒 SaudaCrew")
st.caption("AI order and business automation for small sellers (Demo General Store). All prices and stock are demo data.")

if st.session_state.last_order:
    oid = st.session_state.last_order
    st.success(f"Order #{oid} confirmed. Thank you!")
    pdf = receipt_pdf(oid)
    if pdf:
        st.download_button("⬇️ Download receipt (PDF)", pdf,
                           file_name=f"receipt_{oid}.pdf", mime="application/pdf")
    st.button("Dismiss", on_click=dismiss_order)

tab_store, tab_chat, tab_owner = st.tabs(["🛍️ Store", "💬 AI Assistant", "📊 Owner Dashboard"])

# ---------- Store ----------
with tab_store:
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search", placeholder="Search products: rice, chawal, ghee...",
                           label_visibility="collapsed")
    category = c2.selectbox("Category", ["All"] + categories(), label_visibility="collapsed")
    products = get_products(search, category)
    st.caption(f"{len(products)} products")
    n_cols = 4
    for i in range(0, len(products), n_cols):
        cols = st.columns(n_cols)
        for col, p in zip(cols, products[i:i + n_cols]):
            with col:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:42px;text-align:center'>{p['emoji']}</div>",
                                unsafe_allow_html=True)
                    st.markdown(f"**{p['name']}**")
                    st.markdown(f"Rs {p['price']:,.0f} / {p['unit']}")
                    if p["stock"] <= 0:
                        st.caption("Out of stock")
                    elif p["stock"] <= 10:
                        st.caption(f"⚠️ Only {p['stock']:g} left")
                    else:
                        st.caption("In stock")
                    st.button("Add to cart", key=f"add{p['id']}", on_click=add_to_cart,
                              args=(p["id"],), disabled=p["stock"] <= 0,
                              use_container_width=True)

# ---------- AI Assistant ----------
with tab_chat:
    st.caption("Ask anything in Roman Urdu or English: recipes, comparisons, or just write your order.")
    with st.expander("Try an example"):
        for j, t in enumerate([
            "5 logon ke liye biryani banani hai, kya kya chahiye?",
            "kaunsa ghee behtar hai, desi ya banaspati?",
            "2 kilo chawal aur 1 dozen anday bhej do",
            "10 dozen anday",
            "1 kilo desi ghee chahiye, budget 800 hai",
            "send me 3 kg sugar and 2 litre milk",
        ]):
            st.button(t, key=f"ex{j}", on_click=set_pending, args=(t,))

    history_box = st.container()
    prompt = st.chat_input("e.g. 2 kilo chawal aur 1 dozen anday bhej do")
    if st.session_state.pending:
        prompt = st.session_state.pending
        st.session_state.pending = None

    if prompt:
        history = [{"role": m["role"], "text": m["text"]} for m in st.session_state.chat]
        st.session_state.chat.append({"role": "user", "text": prompt})
        with st.spinner("Agents are working..."):
            result = handle_message(prompt, history)
        st.session_state.chat.append({"role": "assistant", "text": result["reply"], "result": result})

    with history_box:
        if not st.session_state.chat:
            with st.chat_message("assistant"):
                st.write("Assalam o Alaikum! Write your order in Roman Urdu or English, or ask me anything about the shop.")
        for i, m in enumerate(st.session_state.chat):
            with st.chat_message(m["role"]):
                st.write(m["text"])
                if m.get("result"):
                    render_result(i, m["result"])
        if st.session_state.chat:
            st.button("Clear chat", on_click=lambda: st.session_state.chat.clear())

# ---------- Owner Dashboard ----------
with tab_owner:
    stats = collect_stats()
    m1, m2, m3 = st.columns(3)
    m1.metric("Orders today", stats["orders_count"])
    m2.metric("Sales today", f"Rs {stats['total_sales']:,.0f}")
    b = stats["best_seller"]
    m3.metric("Best seller", f"{b['name']} ({b['qty']:g} {b['unit']})" if b else "No sales yet")

    st.subheader("Low stock")
    if stats["low_stock"]:
        st.dataframe([{"Item": x["name"], "Left": f"{x['stock']:g} {x['unit']}"} for x in stats["low_stock"]],
                     hide_index=True, use_container_width=True)
    else:
        st.caption("Nothing is running low.")

    st.subheader("Orders today")
    orders = get_orders_today()
    if orders:
        st.dataframe([{"Order": o["id"], "Time": o["created_at"].replace("T", " "),
                       "Customer": o["customer"], "Total": f"Rs {o['total']:,.0f}", "Status": o["status"]}
                      for o in orders], hide_index=True, use_container_width=True)
    else:
        st.caption("No orders yet.")

    st.subheader("AI daily report")
    if st.button("Generate report"):
        with st.spinner("Report Agent is writing..."):
            st.write(daily_report()["text"])

    with st.expander("⚙️ Demo tools"):
        st.warning("This deletes all orders and resets stock to the starting demo data.")
        if st.checkbox("I understand"):
            if st.button("Reset demo data"):
                seed()
                st.session_state.cart = {}
                st.session_state.last_order = None
                st.success("Demo data reset.")