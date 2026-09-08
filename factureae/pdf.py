"""Minimal PDF 1.4 writer (WinAnsi / Latin-1) — no third-party deps."""

from __future__ import annotations

from .compute import Invoice


def _esc(text: str) -> str:
    encoded = text.encode("latin-1", "replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _ascii_fold(text: str) -> str:
    table = str.maketrans(
        {
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "à": "a",
            "â": "a",
            "ä": "a",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ô": "o",
            "ö": "o",
            "î": "i",
            "ï": "i",
            "ç": "c",
            "É": "E",
            "È": "E",
            "Ê": "E",
            "À": "A",
            "Ù": "U",
            "Ô": "O",
            "Î": "I",
            "Ç": "C",
            "€": "EUR",
            "’": "'",
            "‘": "'",
            "–": "-",
            "—": "-",
        }
    )
    return text.translate(table)


def build_pdf(invoice: Invoice, *, demo: bool = False) -> bytes:
    lines: list[str] = []
    y = 800

    def text(x: int, yy: int, s: str, size: int = 11) -> None:
        lines.append(f"BT /F1 {size} Tf {x} {yy} Td ({_esc(_ascii_fold(s))}) Tj ET")

    text(50, y, "FACTURE", 18)
    y -= 28
    text(50, y, f"Numero: {invoice.number}")
    y -= 16
    text(50, y, f"Date: {invoice.issue_date}")
    y -= 16
    text(50, y, f"Prestation: {invoice.service_date}")
    y -= 28
    text(50, y, "Vendeur", 13)
    y -= 16
    text(50, y, invoice.seller_name)
    for row in invoice.seller_address:
        y -= 14
        text(50, y, row)
    y -= 14
    text(50, y, f"SIRET {invoice.siret}")
    y -= 24
    text(50, y, "Client", 13)
    y -= 16
    text(50, y, invoice.client_name)
    for row in invoice.client_address:
        y -= 14
        text(50, y, row)
    y -= 28
    text(50, y, "Description")
    text(320, y, "Qte")
    text(370, y, "PU HT")
    text(450, y, "Total HT")
    y -= 8
    lines.append(f"0.4 w 50 {y} m 540 {y} l S")
    y -= 18
    for item in invoice.lines:
        text(50, y, item.description[:48])
        text(320, y, str(item.quantity))
        text(370, y, f"{item.unit_price_ht} EUR")
        text(450, y, f"{item.total_ht} EUR")
        y -= 16
    y -= 10
    text(370, y, "Total HT")
    text(450, y, f"{invoice.total_ht} EUR")
    y -= 16
    if invoice.franchise_tva:
        text(370, y, "TVA")
        text(450, y, "0.00 EUR")
    else:
        text(370, y, "TVA")
        text(450, y, f"{invoice.tva_amount} EUR")
    y -= 16
    text(370, y, "Total TTC")
    text(450, y, f"{invoice.total_ttc} EUR")
    y -= 28
    text(50, y, f"Payable sous {invoice.payment_days} jours.")
    y -= 20
    text(50, y, "Mentions legales", 13)
    for mention in invoice.legal_mentions():
        y -= 14
        text(50, y, mention[:95], 9)
    if demo:
        text(120, 400, "DEMO - unpaid copy", 20)

    stream = "\n".join(lines).encode("latin-1")
    objects = []

    def obj(payload: bytes) -> int:
        objects.append(payload)
        return len(objects)

    obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    obj(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
    )
    obj(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, payload in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("ascii")
        out += payload
        out += b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects)+1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode("ascii")
    return bytes(out)
