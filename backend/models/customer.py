"""
FRMYS - Veri Modelleri
Customer ve RiskResult dataclass tanımları.
"""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class RiskResult:
    """Risk analizi sonuç modeli."""

    risk_level: str  # "Yüksek Risk", "Normal", vb.
    alerts: list[str] = field(default_factory=list)
    is_passive: bool = False

    def alerts_to_json(self) -> str:
        """Uyarı listesini JSON string'e çevirir (DB'ye kayıt için)."""
        return json.dumps(self.alerts, ensure_ascii=False)

    @staticmethod
    def alerts_from_json(json_str: str | None) -> list[str]:
        """JSON string'den uyarı listesi çıkarır."""
        if not json_str:
            return []
        return json.loads(json_str)


@dataclass
class Customer:
    """Müşteri veri modeli."""

    id: Optional[int] = None
    name: str = ""
    balance: float = 0.0
    delay_days: int = 0
    active_projects: int = 0
    risk_level: str = ""
    alerts: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        """Customer nesnesini sözlüğe çevirir."""
        return {
            "id": self.id,
            "name": self.name,
            "balance": self.balance,
            "delay_days": self.delay_days,
            "active_projects": self.active_projects,
            "risk_level": self.risk_level,
            "alerts": self.alerts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row) -> "Customer":
        """
        Veritabanı satırından (sqlite3.Row) Customer nesnesi oluşturur.

        Args:
            row: sqlite3.Row nesnesi veya dict-benzeri satır.

        Returns:
            Customer instance.
        """
        return cls(
            id=row["id"],
            name=row["name"],
            balance=row["balance"],
            delay_days=row["delay_days"],
            active_projects=row["active_projects"],
            risk_level=row["risk_level"] or "",
            alerts=RiskResult.alerts_from_json(row["alerts"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
