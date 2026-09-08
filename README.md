# FactureAE

CLI that writes a French **auto-entrepreneur / EI** invoice as a one-page PDF.

- HT / TVA / TTC with `decimal` rounding
- Franchise en base de TVA: *TVA non applicable, art. 293 B du CGI*
- SIRET check (14 digits)
- Legal delay/penalty mention (art. L441-10)
- Zero third-party PDF libraries

## Price

**9 USDC** on Base (one-time, personal-use zip: CLI + tests + examples).

1. Send **9 USDC** (Base) to `0x89324980acaf83Bc065f1cE7A613BF43f9E5692d`
2. Email the **transaction hash** to `louka.altdorfreynes@gmail.com`
3. You get the zip. No subscription.

Demo PDF in this repo is watermarked. Paid zip is not.

Operator: Louka Altdorf Reynes (`0n3m0r3`). Autonomous agent can fulfill.

## Demo (watermarked)

```bash
python3 -m factureae --input examples/demo.json --out facture.pdf --demo
```

Paid copy omits `--demo`.
