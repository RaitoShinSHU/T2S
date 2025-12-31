import math
from typing import Optional
from ..core.atom_parser import parse_magnetic_atoms

def make_sunny_dipole_block(exchange_path: str,
                            mag_threshold: float = 0.5,
                            is_soc: Optional[bool] = None) -> str:
    atoms = parse_magnetic_atoms(exchange_path, mag_threshold, is_soc=is_soc)
    lines = ["# Initialize spins according to TB2J magnetic moments"]
    for i, a in enumerate(atoms, 1):
        mx, my, mz = a['mvec']
        m = math.sqrt(mx*mx + my*my + mz*mz)
        if m > 0:
            ux, uy, uz = mx/m, my/m, mz/m
        else:
            ux, uy, uz = 0.0, 0.0, 1.0
        lines.append(
            f"set_dipole!(sys, [{ux:.6f}, {uy:.6f}, {uz:.6f}], ({i},))"
        )
    return "\n".join(lines)
