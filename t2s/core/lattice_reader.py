import math
from pathlib import Path
from typing import List, Tuple

def read_lines(exchange_path: str) -> List[str]:
    return Path(exchange_path).read_text(encoding="utf-8", errors="ignore").splitlines(True)

def read_lattice_vectors(exchange_path: str) -> Tuple[list, list, list, List[str]]:
    lines = read_lines(exchange_path)
    a_vec = b_vec = c_vec = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Cell (Angstrom):"):
            a_vec = [float(x) for x in lines[i + 1].split()]
            b_vec = [float(x) for x in lines[i + 2].split()]
            c_vec = [float(x) for x in lines[i + 3].split()]
            break
    if a_vec is None:
        raise RuntimeError("在 exchange.out 中没有找到 'Cell (Angstrom):' 段。")
    return a_vec, b_vec, c_vec, lines

def invert_3x3(a_vec, b_vec, c_vec):
    ax, ay, az = a_vec; bx, by, bz = b_vec; cx, cy, cz = c_vec
    det = ax*(by*cz - bz*cy) - bx*(ay*cz - az*cy) + cx*(ay*bz - az*by)
    if abs(det) < 1e-8:
        raise RuntimeError("晶格矩阵接近奇异，无法求逆。")
    inv_det = 1.0 / det
    return [
        [(by*cz - bz*cy)*inv_det, -(ay*cz - az*cy)*inv_det,  (ay*bz - az*by)*inv_det],
        [-(bx*cz - bz*cx)*inv_det, (ax*cz - az*cx)*inv_det, -(ax*bz - az*bx)*inv_det],
        [(bx*cy - by*cx)*inv_det, -(ax*cy - ay*cx)*inv_det,  (ax*by - ay*bx)*inv_det],
    ]

def matvec(mat, v):
    return [sum(mat[i][j] * v[j] for j in range(3)) for i in range(3)]

def cell_params_from_vectors(a_vec, b_vec, c_vec):
    def length(v): return math.sqrt(sum(x*x for x in v))
    def dot(u,v): return sum(ui*vi for ui,vi in zip(u,v))
    def safe_acos(x): return math.acos(max(-1.0, min(1.0, x)))

    a = length(a_vec); b = length(b_vec); c = length(c_vec)
    alpha = math.degrees(safe_acos(dot(b_vec,c_vec)/(b*c)))
    beta  = math.degrees(safe_acos(dot(a_vec,c_vec)/(a*c)))
    gamma = math.degrees(safe_acos(dot(a_vec,b_vec)/(a*b)))
    return a, b, c, alpha, beta, gamma
