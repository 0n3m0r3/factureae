"""French auto-entrepreneur invoice arithmetic and legal mentions."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable


TWOPLACES = Decimal("0.01")
TVA_NORMAL = Decimal("0.20")
RECOVERY_FEE_EUR = Decimal("40.00")


def money(value: Decimal | int | str | float) -> Decimal:
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Line:
    description: str
    quantity: Decimal
    unit_price_ht: Decimal

    @property
    def total_ht(self) -> Decimal:
        return money(self.quantity * self.unit_price_ht)


@dataclass
class Invoice:
    number: str
    issue_date: str
    service_date: str
    seller_name: str
    seller_address: list[str]
    siret: str
    client_name: str
    client_address: list[str]
    lines: list[Line]
    franchise_tva: bool = True
    tva_rate: Decimal = TVA_NORMAL
    payment_days: int = 30
    extra_mentions: list[str] = field(default_factory=list)

    @property
    def total_ht(self) -> Decimal:
        return money(sum((line.total_ht for line in self.lines), Decimal("0.00")))

    @property
    def tva_amount(self) -> Decimal:
        if self.franchise_tva:
            return money(0)
        return money(self.total_ht * self.tva_rate)

    @property
    def total_ttc(self) -> Decimal:
        return money(self.total_ht + self.tva_amount)

    def legal_mentions(self) -> list[str]:
        mentions = [
            f"SIRET {self.siret}",
            "Entreprise individuelle (EI)",
        ]
        if self.franchise_tva:
            mentions.append("TVA non applicable, art. 293 B du CGI")
        else:
            pct = (self.tva_rate * 100).quantize(Decimal("0.1"))
            mentions.append(f"TVA {pct} %")
        mentions.append(
            "Pas d'escompte pour paiement anticipe. En cas de retard de paiement, "
            "taux egal au taux directeur de la BCE majoré de 10 points, plus "
            f"indemnite forfaitaire de recouvrement de {RECOVERY_FEE_EUR} EUR "
            "(art. L441-10 du code de commerce)."
        )
        mentions.extend(self.extra_mentions)
        return mentions


def from_dicts(
    *,
    number: str,
    issue_date: str,
    service_date: str,
    seller_name: str,
    seller_address: Iterable[str],
    siret: str,
    client_name: str,
    client_address: Iterable[str],
    lines: Iterable[dict],
    franchise_tva: bool = True,
) -> Invoice:
    parsed = [
        Line(
            description=str(item["description"]),
            quantity=Decimal(str(item["quantity"])),
            unit_price_ht=money(item["unit_price_ht"]),
        )
        for item in lines
    ]
    if not parsed:
        raise ValueError("invoice needs at least one line")
    if not number.strip():
        raise ValueError("invoice number required")
    digits = "".join(ch for ch in siret if ch.isdigit())
    if len(digits) != 14:
        raise ValueError("SIRET must contain 14 digits")
    return Invoice(
        number=number.strip(),
        issue_date=issue_date,
        service_date=service_date,
        seller_name=seller_name,
        seller_address=list(seller_address),
        siret=digits,
        client_name=client_name,
        client_address=list(client_address),
        lines=parsed,
        franchise_tva=franchise_tva,
    )
