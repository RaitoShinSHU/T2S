from typing import Optional
from ..core.atom_parser import parse_magnetic_atoms

def make_sunny_atoms_block(exchange_path: str,
                           mag_threshold: float = 0.5,
                           is_soc: Optional[bool] = None) -> str:
    atoms = parse_magnetic_atoms(exchange_path, mag_threshold, is_soc=is_soc)
    lines = []
    lines.append("# Magnetic atoms (fractional coordinates)")
    lines.append("positions = [")
    for a in atoms:
        fx, fy, fz = a['frac']
        lines.append(f"    [{fx:.8f}, {fy:.8f}, {fz:.8f}],  # {a['label']} ({a['element']})")
    lines.append("]\n")

    lines.append("types = [")
    for a in atoms:
        lines.append(f"    \"{a['element']}\",")
    lines.append("]\n")

    lines.append("cryst = Crystal(latvecs, positions, 1; types=types)\n")
    lines.append("moments = [")
    for i in range(len(atoms)):
        lines.append(f"    {i+1} => Moment(s=1, g=2),")
    lines.append("]\n")
    lines.append("sys = System(cryst, moments, :dipole)")
    return "\n".join(lines)
