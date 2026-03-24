"""
Test: Risk Analiz Motoru (risk_engine.py)
Her iş kuralı için pozitif ve negatif senaryolar.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.risk_engine import calculate_risk


class TestCalculateRisk:
    """calculate_risk fonksiyonu testleri."""

    # ── 🔴 Yüksek Risk testleri ─────────────────────────────

    def test_high_risk_high_balance(self):
        """Bakiye > 50.000 → Yüksek Risk."""
        result = calculate_risk(balance=60_000, delay_days=0, active_projects=1)
        assert result.risk_level == "Yüksek Risk"
        assert any("Yüksek Risk" in a and "Bakiye" in a for a in result.alerts)

    def test_high_risk_high_delay(self):
        """Gecikme > 30 gün → Yüksek Risk."""
        result = calculate_risk(balance=1_000, delay_days=35, active_projects=1)
        assert result.risk_level == "Yüksek Risk"
        assert any("Yüksek Risk" in a and "Gecikme" in a for a in result.alerts)

    def test_high_risk_both_conditions(self):
        """Hem bakiye hem gecikme eşik üstünde → Yüksek Risk + çift uyarı."""
        result = calculate_risk(balance=100_000, delay_days=45, active_projects=2)
        assert result.risk_level == "Yüksek Risk"
        high_risk_alerts = [a for a in result.alerts if "Yüksek Risk" in a]
        assert len(high_risk_alerts) == 2

    def test_boundary_balance_50000_not_high_risk(self):
        """Bakiye tam 50.000 → Yüksek Risk DEĞİL (eşik strict greater-than)."""
        result = calculate_risk(balance=50_000, delay_days=0, active_projects=1)
        assert result.risk_level == "Normal"

    def test_boundary_delay_30_not_high_risk(self):
        """Gecikme tam 30 gün → Yüksek Risk DEĞİL."""
        result = calculate_risk(balance=0, delay_days=30, active_projects=1)
        assert result.risk_level == "Normal"

    # ── ⚠️ Acil Uyarı testleri ──────────────────────────────

    def test_urgent_alert_delay_21(self):
        """Gecikme 21 gün → Acil Uyarı mevcut."""
        result = calculate_risk(balance=1_000, delay_days=21, active_projects=1)
        assert any("Acil Uyarı" in a for a in result.alerts)

    def test_no_urgent_alert_delay_20(self):
        """Gecikme tam 20 gün → Acil Uyarı YOK."""
        result = calculate_risk(balance=1_000, delay_days=20, active_projects=1)
        assert not any("Acil Uyarı" in a for a in result.alerts)

    # ── 🔔 Tahsilat Takibi testleri ─────────────────────────

    def test_collection_tracking_delay_1(self):
        """Gecikme 1 gün → Tahsilat Takibi mevcut."""
        result = calculate_risk(balance=1_000, delay_days=1, active_projects=1)
        assert any("Tahsilat Takibi" in a for a in result.alerts)

    def test_no_collection_tracking_delay_0(self):
        """Gecikme 0 gün → Tahsilat Takibi YOK."""
        result = calculate_risk(balance=1_000, delay_days=0, active_projects=1)
        assert not any("Tahsilat Takibi" in a for a in result.alerts)

    # ── 💤 Pasif Müşteri testleri ────────────────────────────

    def test_passive_customer_zero_projects(self):
        """Aktif proje = 0 → Pasif Müşteri."""
        result = calculate_risk(balance=1_000, delay_days=0, active_projects=0)
        assert result.is_passive is True
        assert any("Pasif Müşteri" in a for a in result.alerts)

    def test_active_customer_with_projects(self):
        """Aktif proje > 0 → Pasif değil."""
        result = calculate_risk(balance=1_000, delay_days=0, active_projects=3)
        assert result.is_passive is False
        assert not any("Pasif Müşteri" in a for a in result.alerts)

    # ── Normal senaryo ───────────────────────────────────────

    def test_normal_no_alerts(self):
        """Tüm değerler güvenli aralıkta → Normal, uyarı yok."""
        result = calculate_risk(balance=10_000, delay_days=0, active_projects=2)
        assert result.risk_level == "Normal"
        assert result.alerts == []
        assert result.is_passive is False

    # ── Kombine senaryo ──────────────────────────────────────

    def test_combined_all_alerts(self):
        """Tüm kurallar tetiklenir: Yüksek Risk + Acil + Tahsilat + Pasif."""
        result = calculate_risk(balance=100_000, delay_days=40, active_projects=0)
        assert result.risk_level == "Yüksek Risk"
        assert result.is_passive is True
        assert any("Yüksek Risk" in a and "Bakiye" in a for a in result.alerts)
        assert any("Yüksek Risk" in a and "Gecikme" in a for a in result.alerts)
        assert any("Acil Uyarı" in a for a in result.alerts)
        assert any("Tahsilat Takibi" in a for a in result.alerts)
        assert any("Pasif Müşteri" in a for a in result.alerts)
