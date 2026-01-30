import math, string
from fractions import Fraction
from typing import List, Optional
from ..core.atom_parser import parse_magnetic_atoms
from ..core.exchange_parser import parse_exchange_blocks
from ..core.symmetry import group_exchange_shells

def make_sunny_exchange_block(exchange_path: str,
                              mag_threshold: float = 0.5,
                              j_tol: float = 1e-3,
                              d_tol: float = 1e-3,
                              dist_tol: float = 1e-3,
                              max_dist: float = 0.0,
                              min_exchange: float = 1e-3,
                              use_dmi: bool = True,
                              spins: Optional[List[str]] = None) -> str:
    atoms = parse_magnetic_atoms(exchange_path, mag_threshold, is_soc=use_dmi)
    if spins is None:
        labels = ", ".join(a["label"] for a in atoms)
        raise ValueError(
            "必须为每个磁性原子指定 S 值。"
            f"磁性原子顺序: {labels}."
        )
    if len(spins) != len(atoms):
        labels = ", ".join(a["label"] for a in atoms)
        raise ValueError(
            "指定的 S 数量与磁性原子数量不一致。"
            f"磁性原子顺序: {labels}."
        )
    spin_values = [float(Fraction(s)) for s in spins]
    label_to_index = {a['label']: i+1 for i,a in enumerate(atoms)}
    blocks = parse_exchange_blocks(exchange_path)
    shells_all = group_exchange_shells(blocks, j_tol=j_tol, d_tol=d_tol, dist_tol=dist_tol)

    shells = []
    for shell in shells_all:
        if max_dist > 0.0 and shell['distance'] > max_dist:
            continue
        types = [t for t in shell['types']
                 if not (abs(t['J']) <= min_exchange and abs(t['D']) <= min_exchange)]
        if types:
            shells.append({'distance': shell['distance'], 'types': types})

    out = []
    out.append("# Exchange shells (J in meV, D = |DMI| in meV)")

    for n, shell in enumerate(shells, 1):
        if len(shell['types']) == 1:
            t = shell['types'][0]
            t["_j_name"] = f"J{n}"
            t["_d_name"] = f"D{n}"
            out.append(f"{t['_j_name']} = {t['J']:.6f}")
            if use_dmi:
                out.append(f"{t['_d_name']} = {t['D']:.6f}")
        else:
            for k, t in enumerate(shell['types']):
                suf = string.ascii_uppercase[k]
                t["_j_name"] = f"J{n}_{suf}"
                t["_d_name"] = f"D{n}_{suf}"
                out.append(f"{t['_j_name']} = {t['J']:.6f}")
                if use_dmi:
                    out.append(f"{t['_d_name']} = {t['D']:.6f}")
        out.append("")

    out.append("# Exchange couplings")
    for n, shell in enumerate(shells, 1):
        out.append(f"# --- Shell {n}: distance ≈ {shell['distance']:.3f} Å ---")
        for t in shell['types']:
            J = t['J']; D = t['D']
            for b in t['bonds']:
                i = label_to_index.get(b['i_label'])
                j = label_to_index.get(b['j_label'])
                if i is None or j is None:
                    continue
                scale = 1.0 / math.sqrt(spin_values[i - 1] * spin_values[j - 1])
                Dx, Dy, Dz = b['DMI']
                if use_dmi and D > 0:
                    ux, uy, uz = Dx/D, Dy/D, Dz/D
                else:
                    ux, uy, uz = 0.0, 0.0, 0.0
                if use_dmi and D > min_exchange:
                    term = f"{scale:.6f} * {t['_j_name']} * I"
                    term += (
                        f" + {scale:.6f} * {t['_d_name']} * dmvec([{ux:.6f}, {uy:.6f}, {uz:.6f}])"
                    )
                else:
                    term = f"{scale:.6f} * {t['_j_name']}"
                out.append(
                    f"set_exchange!(sys, {term}, Bond({i}, {j}, [{b['R'][0]}, {b['R'][1]}, {b['R'][2]}]))"
                )
        out.append("")
    return "\n".join(out)
