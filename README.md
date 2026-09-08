# FactureAE

CLI that writes a French **auto-entrepreneur / EI** invoice as a one-page PDF.

- HT / TVA / TTC with `decimal` rounding
- Franchise en base de TVA: *TVA non applicable, art. 293 B du CGI*
- SIRET check (14 digits)
- Legal delay/penalty mention (art. L441-10)
- Zero third-party PDF libraries

## Run

```bash
PYTHONPATH=. python3 -m factureae --input examples/demo.json --out facture.pdf --demo
```

`--demo` stamps a watermark. Omit it for a clean PDF.

Tests: `PYTHONPATH=. python3 -m unittest tests.test_compute -v`

## Paid service (optional)

The CLI is in this repo. If you want **me to produce 12 filled PDFs** from your SIRET, address, and line items:

**9 USDC** on Base to `0x89324980acaf83Bc065f1cE7A613BF43f9E5692d`

Email the tx hash plus JSON specs to `louka.altdorfreynes@gmail.com`. No subscription. Operator: Louka Altdorf Reynes (`0n3m0r3`).
