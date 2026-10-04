from tools.db import calculate_total


def make_invoice(lines):
    """Bill banao. Prices sirf database se aati hain, LLM se kabhi nahi."""
    if not lines:
        return {"lines": [], "total": 0}
    return calculate_total(lines)