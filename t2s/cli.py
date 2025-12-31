import argparse
from pathlib import Path
from .builder import build_sunny_julia

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("exchange", nargs="?", default="exchange.out")
    parser.add_argument("-o", "--output")
    parser.add_argument("--mag-threshold", type=float, default=0.5)
    parser.add_argument("--j-tol", type=float, default=1e-3)
    parser.add_argument("--d-tol", type=float, default=1e-3)
    parser.add_argument("--dist-tol", type=float, default=1e-3)
    parser.add_argument("--max-dist", type=float, default=0.0)
    parser.add_argument("--min-exchange", type=float, default=1e-3)

    soc = parser.add_mutually_exclusive_group()
    soc.add_argument("--soc", action="store_true")
    soc.add_argument("--no-soc", action="store_true")

    parser.add_argument("--with-dipole", action="store_true")
    parser.add_argument("--with-relax", action="store_true")

    args = parser.parse_args()

    import sys
    from pathlib import Path
    if not Path(args.exchange).exists():
        print(f"[ERROR] exchange.out not found: {args.exchange}", file=sys.stderr)
        sys.exit(1)


    if args.soc:
        soc_mode = "soc"
    elif args.no_soc:
        soc_mode = "no-soc"
    else:
        soc_mode = "auto"

    code = build_sunny_julia(
        exchange_path=args.exchange,
        soc_mode=soc_mode,
        mag_threshold=args.mag_threshold,
        j_tol=args.j_tol,
        d_tol=args.d_tol,
        dist_tol=args.dist_tol,
        max_dist=args.max_dist,
        min_exchange=args.min_exchange,
        with_dipole=args.with_dipole,
        with_relax=args.with_relax,
    )

    if args.output:
        Path(args.output).write_text(code, encoding="utf-8")
    else:
        print(code)


def entrypoint():
    main()
