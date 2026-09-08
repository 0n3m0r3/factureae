import unittest
from decimal import Decimal
from pathlib import Path
import json
import subprocess
import sys
import tempfile

from factureae.compute import from_dicts, money
from factureae.pdf import build_pdf
from factureae.cli import main


SPEC = {
    "number": "FA-2026-001",
    "issue_date": "2026-09-08",
    "service_date": "2026-09-07",
    "seller_name": "Louka Altdorf Reynes",
    "seller_address": ["Lille", "France"],
    "siret": "12345678901234",
    "client_name": "Client Test SARL",
    "client_address": ["Paris"],
    "lines": [
        {"description": "Script Python", "quantity": "2", "unit_price_ht": "60.00"},
        {"description": "Relecture", "quantity": "1", "unit_price_ht": "40.50"},
    ],
    "franchise_tva": True,
}


class ComputeTests(unittest.TestCase):
    def test_franchise_totals_and_mention(self):
        inv = from_dicts(**SPEC)
        self.assertEqual(inv.total_ht, money("160.50"))
        self.assertEqual(inv.tva_amount, money("0"))
        self.assertEqual(inv.total_ttc, money("160.50"))
        mentions = " ".join(inv.legal_mentions())
        self.assertIn("293 B", mentions)
        self.assertIn("12345678901234", mentions)

    def test_tva_20(self):
        spec = dict(SPEC)
        spec["franchise_tva"] = False
        inv = from_dicts(**spec)
        self.assertEqual(inv.total_ht, money("160.50"))
        self.assertEqual(inv.tva_amount, money("32.10"))
        self.assertEqual(inv.total_ttc, money("192.60"))

    def test_bad_siret(self):
        spec = dict(SPEC)
        spec["siret"] = "123"
        with self.assertRaises(ValueError):
            from_dicts(**spec)

    def test_pdf_header_and_demo(self):
        inv = from_dicts(**SPEC)
        pdf = build_pdf(inv, demo=True)
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"%%EOF", pdf)
        self.assertIn(b"DEMO", pdf)
        paid = build_pdf(inv, demo=False)
        self.assertNotIn(b"DEMO", paid)

    def test_cli_writes_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.json"
            out = Path(tmp) / "out.pdf"
            src.write_text(json.dumps(SPEC), encoding="utf-8")
            rc = main(["--input", str(src), "--out", str(out), "--demo"])
            self.assertEqual(rc, 0)
            data = out.read_bytes()
            self.assertTrue(data.startswith(b"%PDF-1.4"))


if __name__ == "__main__":
    unittest.main()
