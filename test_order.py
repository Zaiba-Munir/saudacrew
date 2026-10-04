from agents.order_agent import parse_order

MESSAGES = [
    "2 kilo chawal aur 1 dozen anday bhej do",
    "mujhe cheeni 5 kilo aur chai patti chahiye",
    "10 dozen anday",
    "aata aur daal",
    "2 kg chaawal aur 1 kg rice",
    "1 kilo desi ghee chahiye, budget 800 hai",
    "send me 3 kg sugar and 2 litre milk",
    "bhai 1 litre doodh, 2 packet biscuit aur ek sabun bhej dena",
    "namak aur lal mirch 1-1 pack",
    "hello kya haal hai",
]

for i, m in enumerate(MESSAGES, 1):
    print(f"\n{i}. {m}")
    print("   ->", parse_order(m))