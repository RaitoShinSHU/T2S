import re
from typing import List, Dict, Any
from .lattice_reader import read_lattice_vectors

def parse_exchange_blocks(exchange_path: str) -> List[Dict[str, Any]]:
    _, _, _, lines = read_lattice_vectors(exchange_path)
    in_exch = False
    blocks: List[Dict[str, Any]] = []
    cur: Dict[str, Any] = None

    for line in lines:
        if line.strip().startswith("Exchange"):
            in_exch = True
            continue
        if not in_exch:
            continue

        if line.strip().startswith("----"):
            if cur:
                blocks.append(cur)
                cur = None
            continue

        if not line.strip():
            continue

        if line.strip().startswith("i") and "J_iso" in line:
            continue

        if cur is None:
            m = re.match(
                r"\s*(\S+)\s+(\S+)\s+\(\s*([-\d]+),\s*([-\d]+),\s*([-\d]+)\s*\)\s+"
                r"([-\d.]+)\s+\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\s*\)\s+([-\d.]+)",
                line,
            )
            if not m:
                continue
            cur = {
                "i_label": m.group(1),
                "j_label": m.group(2),
                "R": (int(m.group(3)), int(m.group(4)), int(m.group(5))),
                "J_inline": float(m.group(6)),
                "disp": (float(m.group(7)), float(m.group(8)), float(m.group(9))),
                "distance": float(m.group(10)),
                "J_iso": None,
                "DMI": (0.0, 0.0, 0.0),
            }
        else:
            s = line.strip()
            if s.startswith("J_iso:"):
                try:
                    cur["J_iso"] = float(s.split()[1])
                except Exception:
                    pass
            elif "DMI:" in line:
                m = re.search(r"DMI:\s*\(\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\)", line)
                if m:
                    cur["DMI"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))

    if cur:
        blocks.append(cur)

    return blocks
