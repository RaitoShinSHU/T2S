import math, re
from typing import List, Dict, Any, Optional
from .lattice_reader import read_lattice_vectors, invert_3x3, matvec

def parse_magnetic_atoms(exchange_path: str,
                         mag_threshold: float = 0.5,
                         is_soc: Optional[bool] = None) -> List[Dict[str, Any]]:
    a_vec, b_vec, c_vec, lines = read_lattice_vectors(exchange_path)
    invA = invert_3x3(a_vec, b_vec, c_vec)

    atoms: List[Dict[str, Any]] = []
    in_atoms = False
    header_line = None
    vector_mode = None

    for line in lines:
        if line.strip().startswith("Atoms"):
            in_atoms = True
            continue
        if not in_atoms:
            continue
        if not line.strip():
            break
        if line.strip().startswith("(Note"):
            continue
        if line.strip().startswith("Atom"):
            header_line = line
            if is_soc is not None:
                vector_mode = is_soc
            else:
                if "w_magmom" in header_line:
                    vector_mode = False
                elif "M(x)" in header_line or "M(y)" in header_line or "M(z)" in header_line:
                    vector_mode = True
                else:
                    vector_mode = False
            continue
        if line.strip().startswith("Total") or header_line is None:
            break

        parts = line.split()
        if vector_mode:
            if len(parts) < 8:
                continue
            name = parts[0]
            x, y, z = map(float, parts[1:4])
            mx, my, mz = map(float, parts[5:8])
            m = math.sqrt(mx*mx + my*my + mz*mz)
        else:
            if len(parts) < 6:
                continue
            name = parts[0]
            x, y, z = map(float, parts[1:4])
            m_scalar = float(parts[5])
            m = abs(m_scalar)
            mx, my, mz = 0.0, 0.0, m_scalar

        if m < mag_threshold:
            continue

        r_cart = [x, y, z]
        r_frac = matvec(invA, r_cart)
        m_elem = re.match(r"[A-Za-z]+", name)
        elem = m_elem.group(0) if m_elem else name

        atoms.append(dict(
            label=name,
            element=elem,
            cart=r_cart,
            frac=r_frac,
            moment=m,
            mvec=[mx, my, mz],
        ))

    return atoms
