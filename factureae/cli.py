"""CLI: python3 -m factureae --input invoice.json --out facture.pdf"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compute import from_dicts
from .pdf import build_pdf


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="factureae")
    p.add_argument("--input", required=True, help="JSON invoice spec")
    p.add_argument("--out", required=True, help="PDF path")
    p.add_argument("--demo", action="store_true", help="stamp DEMO watermark")
    args = p.parse_args(argv)
    spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
    invoice = from_dicts(**spec)
    pdf = build_pdf(invoice, demo=args.demo)
    Path(args.out).write_bytes(pdf)
    if not pdf.startswith(b"%PDF"):
        print("error: invalid PDF", file=sys.stderr)
        return 1
    print(f"wrote {args.out} ht={invoice.total_ht} ttc={invoice.total_ttc}")
    return 0
