from pathlib import Path

def detect_soc(exchange_path: str = "exchange.out") -> bool:
    txt = Path(exchange_path).read_text(encoding="utf-8", errors="ignore")
    lower = txt.lower()

    if "non-collinear" in lower or "noncollinear" in lower:
        return True
    if "dmi:" in txt:
        return True
    if "m(x)" in txt or "m(y)" in txt or "m(z)" in txt:
        return True

    if "collinear" in lower:
        return False
    if "w_magmom" in txt:
        return False

    return False
