"""
FRMYS - Müşteri Servisi
CRUD operasyonları ve dashboard özet verisi.
"""

from datetime import datetime, timezone
from typing import Optional

from backend.database.db_manager import DatabaseManager
from backend.models.customer import Customer, RiskResult
from backend.services.risk_engine import calculate_risk
from backend.utils.validators import validate_customer_data


class CustomerService:
    """Müşteri CRUD işlemleri ve dashboard özeti sağlayan servis."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # ── CREATE ──────────────────────────────────────────────────

    def create_customer(
        self,
        name: str,
        balance,
        delay_days,
        active_projects,
    ) -> Customer:
        """
        Yeni müşteri oluşturur. Veri doğrulanır, risk hesaplanır ve DB'ye kaydedilir.

        Args:
            name: Müşteri adı.
            balance: Toplam bakiye.
            delay_days: Gecikme süresi (gün).
            active_projects: Aktif proje sayısı.

        Returns:
            Oluşturulan Customer nesnesi (id dahil).

        Raises:
            ValidationError: Geçersiz veri durumunda.
        """
        validated = validate_customer_data(name, balance, delay_days, active_projects)
        risk = calculate_risk(
            validated["balance"],
            validated["delay_days"],
            validated["active_projects"],
        )

        now = _now_iso()

        cursor = self.db.execute(
            """
            INSERT INTO customers
                (name, balance, delay_days, active_projects,
                 risk_level, alerts, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                validated["name"],
                validated["balance"],
                validated["delay_days"],
                validated["active_projects"],
                risk.risk_level,
                risk.alerts_to_json(),
                now,
                now,
            ),
        )
        self.db.commit()

        return Customer(
            id=cursor.lastrowid,
            name=validated["name"],
            balance=validated["balance"],
            delay_days=validated["delay_days"],
            active_projects=validated["active_projects"],
            risk_level=risk.risk_level,
            alerts=risk.alerts,
            created_at=now,
            updated_at=now,
        )

    # ── READ ────────────────────────────────────────────────────

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """ID ile müşteri getirir. Bulunamazsa None döner."""
        row = self.db.execute(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        if row is None:
            return None
        return Customer.from_row(row)

    def get_all_customers(self) -> list[Customer]:
        """Tüm müşterileri döner (oluşturulma tarihine göre sıralı)."""
        rows = self.db.execute(
            "SELECT * FROM customers ORDER BY created_at DESC"
        ).fetchall()
        return [Customer.from_row(r) for r in rows]

    # ── UPDATE ──────────────────────────────────────────────────

    def update_customer(self, customer_id: int, **fields) -> Optional[Customer]:
        """
        Müşteri bilgilerini günceller ve riski yeniden hesaplar.

        Args:
            customer_id: Güncellenecek müşteri ID'si.
            **fields: Güncellenecek alanlar (name, balance, delay_days, active_projects).

        Returns:
            Güncellenmiş Customer nesnesi. Müşteri bulunamazsa None.

        Raises:
            ValidationError: Geçersiz veri durumunda.
        """
        existing = self.get_customer(customer_id)
        if existing is None:
            return None

        # Mevcut değerlerle birleştir
        name = fields.get("name", existing.name)
        balance = fields.get("balance", existing.balance)
        delay_days = fields.get("delay_days", existing.delay_days)
        active_projects = fields.get("active_projects", existing.active_projects)

        validated = validate_customer_data(name, balance, delay_days, active_projects)
        risk = calculate_risk(
            validated["balance"],
            validated["delay_days"],
            validated["active_projects"],
        )

        now = _now_iso()

        self.db.execute(
            """
            UPDATE customers
            SET name = ?, balance = ?, delay_days = ?, active_projects = ?,
                risk_level = ?, alerts = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                validated["name"],
                validated["balance"],
                validated["delay_days"],
                validated["active_projects"],
                risk.risk_level,
                risk.alerts_to_json(),
                now,
                customer_id,
            ),
        )
        self.db.commit()

        return Customer(
            id=customer_id,
            name=validated["name"],
            balance=validated["balance"],
            delay_days=validated["delay_days"],
            active_projects=validated["active_projects"],
            risk_level=risk.risk_level,
            alerts=risk.alerts,
            created_at=existing.created_at,
            updated_at=now,
        )

    # ── DELETE ──────────────────────────────────────────────────

    def delete_customer(self, customer_id: int) -> bool:
        """
        Müşteriyi siler.

        Returns:
            True silindiyse, False müşteri bulunamadıysa.
        """
        cursor = self.db.execute(
            "DELETE FROM customers WHERE id = ?", (customer_id,)
        )
        self.db.commit()
        return cursor.rowcount > 0

    # ── DASHBOARD ───────────────────────────────────────────────

    def get_dashboard_summary(self) -> dict:
        """
        Dashboard için portföy özet verisi döner.

        Returns:
            dict: {
                "total_customers": int,
                "risk_distribution": {"Yüksek Risk": int, "Normal": int},
                "urgent_alerts": [Customer, ...],
                "collection_required": [Customer, ...],
                "passive_customers": [Customer, ...],
                "total_balance": float,
            }
        """
        customers = self.get_all_customers()

        risk_distribution: dict[str, int] = {}
        urgent_alerts: list[Customer] = []
        collection_required: list[Customer] = []
        passive_customers: list[Customer] = []
        total_balance = 0.0

        for c in customers:
            # Risk dağılımı
            risk_distribution[c.risk_level] = risk_distribution.get(c.risk_level, 0) + 1

            # Toplam bakiye
            total_balance += c.balance

            # Acil uyarı (gecikme > 20 gün)
            if c.delay_days > 20:
                urgent_alerts.append(c)

            # Tahsilat takibi (gecikme > 0 gün)
            if c.delay_days > 0:
                collection_required.append(c)

            # Pasif müşteri (aktif proje = 0)
            if c.active_projects == 0:
                passive_customers.append(c)

        return {
            "total_customers": len(customers),
            "risk_distribution": risk_distribution,
            "urgent_alerts": urgent_alerts,
            "collection_required": collection_required,
            "passive_customers": passive_customers,
            "total_balance": total_balance,
        }


def _now_iso() -> str:
    """Şu anki zamanı ISO 8601 formatında döndürür."""
    return datetime.now(timezone.utc).isoformat()
