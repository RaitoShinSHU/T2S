import math
from typing import List, Dict, Any

def group_exchange_shells(blocks: List[Dict[str, Any]],
                          j_tol: float = 1e-3,
                          d_tol: float = 1e-3,
                          dist_tol: float = 1e-3):
    blocks_sorted = sorted(blocks, key=lambda b: b["distance"])
    shells = []

    for b in blocks_sorted:
        dist = b["distance"]
        if not shells or abs(dist - shells[-1]["distance"]) > dist_tol:
            shells.append({"distance": dist, "blocks": []})
        shells[-1]["blocks"].append(b)

    for shell in shells:
        types = []
        for b in shell["blocks"]:
            J_tb2j = b["J_iso"] if b["J_iso"] is not None else b["J_inline"]
            J = -J_tb2j
            Dx, Dy, Dz = b["DMI"]
            D = math.sqrt(Dx*Dx + Dy*Dy + Dz*Dz)

            found = None
            for t in types:
                if abs(J - t["J"]) <= j_tol and abs(D - t["D"]) <= d_tol:
                    found = t
                    break
            if found is None:
                found = {"J": J, "D": D, "bonds": []}
                types.append(found)
            found["bonds"].append(b)
        shell["types"] = types

    return shells
