def make_relax_block() -> str:
    return "\n".join([
        "# Optional: randomize spins and relax to (meta-)stable state",
        "randomize_spins!(sys)",
        "minimize_energy!(sys)",
    ])
