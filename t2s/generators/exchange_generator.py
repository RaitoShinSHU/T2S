import math, string
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
                              use_dmi: bool = True) -> str:
    atoms = parse_magnetic_atoms(exchange_path, mag_threshold, is_soc=use_dmi)
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
            out.append(f"J{n} = {t['J']:.6f}")
            if use_dmi:
                out.append(f"D{n} = {t['D']:.6f}")
        else:
            for k, t in enumerate(shell['types']):
                suf = string.ascii_uppercase[k]
                out.append(f"J{n}_{suf} = {t['J']:.6f}")
                if use_dmi:
                    out.append(f"D{n}_{suf} = {t['D']:.6f}")
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
                Dx, Dy, Dz = b['DMI']
                if use_dmi and D > 0:
                    ux, uy, uz = Dx/D, Dy/D, Dz/D
                else:
                    ux, uy, uz = 0.0, 0.0, 0.0
                term = f"J{n} * I"
                if use_dmi and D > min_exchange:
                    term += f" + D{n} * dmvec([{ux:.6f}, {uy:.6f}, {uz:.6f}])"
                out.append(
                    f"set_exchange!(sys, {term}, Bond({i}, {j}, [{b['R'][0]}, {b['R'][1]}, {b['R'][2]}]))"
                )
        out.append("")
    return "\n".join(out)
