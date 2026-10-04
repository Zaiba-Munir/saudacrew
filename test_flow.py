from agents.manager import handle_message, confirm_order
from agents.report_agent import daily_report

TESTS = [
    "2 kilo chawal aur 1 dozen anday bhej do",
    "10 dozen anday",
    "1 kilo desi ghee chahiye, budget 800 hai",
    "aata aur daal",
    "send me 3 kg sugar and 2 litre milk",
]

for m in TESTS:
    print("\n" + "=" * 60)
    print("CUSTOMER:", m)
    r = handle_message(m)
    for t in r["trace"]:
        print(f"  [{t['agent']}] {t['action']} | {t['detail']} ({t['seconds']}s)")
    print("BILL TOTAL: Rs", r["bill"]["total"])
    print("REPLY:\n" + r["reply"])
    if r["decision"] == "ok":
        print("-> Customer ne confirm kiya, order saved:", confirm_order(r))

print("\n" + "=" * 60)
print("OWNER REPORT:")
print(daily_report()["text"])