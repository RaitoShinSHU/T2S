from typing import Optional, List
from ..core.atom_parser import parse_magnetic_atoms

def make_sunny_atoms_block(exchange_path: str,
                           mag_threshold: float = 0.5,
                           is_soc: Optional[bool] = None,
                           spins: Optional[List[str]] = None) -> str:
    atoms = parse_magnetic_atoms(exchange_path, mag_threshold, is_soc=is_soc)
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
    for i, spin in enumerate(spins):
        lines.append(f"    {i+1} => Moment(s={spin}, g=2),")
    lines.append("]\n")
    lines.append("sys = System(cryst, moments, :dipole)")
    return "\n".join(lines)
