"""
FRMYS - Risk Analiz Motoru
İş kurallarına göre müşteri risk seviyesi ve uyarılarını hesaplar.

İş Kuralları:
  🔴 Yüksek Risk   : bakiye > 50.000 VEYA gecikme > 30 gün
  ⚠️  Acil Uyarı    : gecikme > 20 gün
  🔔 Tahsilat Takibi: gecikme > 0 gün
  💤 Pasif Müşteri  : aktif proje = 0
"""

from backend.models.customer import RiskResult


# ── Eşik Değerleri (Thresholds) ─────────────────────────────────
HIGH_RISK_BALANCE_THRESHOLD = 50_000
HIGH_RISK_DELAY_THRESHOLD = 30
URGENT_ALERT_DELAY_THRESHOLD = 20
COLLECTION_DELAY_THRESHOLD = 0


def calculate_risk(
    balance: float,
    delay_days: int,
    active_projects: int,
) -> RiskResult:
    """
    Müşterinin finansal verilerine göre risk analizi yapar.

    Args:
        balance: Toplam bakiye (≥ 0).
        delay_days: Gecikme süresi, gün cinsinden (≥ 0).
        active_projects: Aktif proje sayısı (≥ 0).

    Returns:
        RiskResult: risk_level, alerts listesi ve is_passive bayrağı.
    """
    alerts: list[str] = []
    risk_level = "Normal"
    is_passive = False

    # 🔴 Yüksek Risk kontrolü
    if balance > HIGH_RISK_BALANCE_THRESHOLD:
        risk_level = "Yüksek Risk"
        alerts.append(
            f"Yüksek Risk: Bakiye ({balance:,.2f}) "
            f"{HIGH_RISK_BALANCE_THRESHOLD:,} birim eşiğini aşıyor."
        )

    if delay_days > HIGH_RISK_DELAY_THRESHOLD:
        risk_level = "Yüksek Risk"
        alerts.append(
            f"Yüksek Risk: Gecikme süresi ({delay_days} gün) "
            f"{HIGH_RISK_DELAY_THRESHOLD} gün eşiğini aşıyor."
        )

    # ⚠️ Acil Uyarı kontrolü
    if delay_days > URGENT_ALERT_DELAY_THRESHOLD:
        alerts.append(
            f"Acil Uyarı: Gecikme süresi ({delay_days} gün) "
            f"{URGENT_ALERT_DELAY_THRESHOLD} gün eşiğini aşıyor."
        )

    # 🔔 Tahsilat Takibi kontrolü
    if delay_days > COLLECTION_DELAY_THRESHOLD:
        alerts.append(
            f"Tahsilat Takibi: Gecikme süresi ({delay_days} gün) mevcut."
        )

    # 💤 Pasif Müşteri kontrolü
    if active_projects == 0:
        is_passive = True
        alerts.append("Pasif Müşteri: Aktif proje bulunmuyor.")

    return RiskResult(
        risk_level=risk_level,
        alerts=alerts,
        is_passive=is_passive,
    )
