from ..core.lattice_reader import read_lattice_vectors, cell_params_from_vectors

def make_sunny_latvecs_block(exchange_path: str) -> str:
    a_vec, b_vec, c_vec, _ = read_lattice_vectors(exchange_path)
    a, b, c, alpha, beta, gamma = cell_params_from_vectors(a_vec, b_vec, c_vec)
    return "\n".join([
        "# Lattice",
        "latvecs = lattice_vectors("
        f"{a:.8f}, {b:.8f}, {c:.8f}, {alpha:.6f}, {beta:.6f}, {gamma:.6f})"
    ])
