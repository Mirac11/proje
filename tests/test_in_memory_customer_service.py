"""
Test: In-Memory Müşteri Servisi (in_memory_customer_service.py)
Tüm servis fonksiyonlarının birim testleri.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.in_memory_customer_service import (
    validate_customer_input_service,
    calculate_risk_service,
    add_customer_service,
    calculate_dashboard_summary_service,
    load_test_customers_service,
    get_all_customers,
    clear_all_customers,
)


@pytest.fixture(autouse=True)
def clean_store():
    """Her test öncesi ve sonrası müşteri listesini temizler."""
    clear_all_customers()
    yield
    clear_all_customers()


# ═══════════════════════════════════════════════════════════════════
# validate_customer_input_service testleri
# ═══════════════════════════════════════════════════════════════════


class TestValidateCustomerInputService:
    """validate_customer_input_service fonksiyonu testleri."""

    def test_valid_data_returns_none(self):
        """Geçerli veri ile doğrulama hatası dönmez."""
        data = {
            "customer_name": "Test Müşteri",
            "company_name": "Test Şirketi",
            "balance": 10000,
            "delay_day": 5,
            "active_project_count": 2,
        }
        assert validate_customer_input_service(data) is None

    def test_missing_field(self):
        """Eksik alan hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": 100,
            # delay_day eksik
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "delay_day" in error

    def test_empty_customer_name(self):
        """Boş müşteri adı hata verir."""
        data = {
            "customer_name": "",
            "company_name": "Şirket",
            "balance": 100,
            "delay_day": 0,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "boş" in error

    def test_empty_company_name(self):
        """Boş şirket adı hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "   ",
            "balance": 100,
            "delay_day": 0,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "boş" in error

    def test_negative_balance(self):
        """Negatif bakiye hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": -500,
            "delay_day": 0,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "negatif" in error

    def test_negative_delay_day(self):
        """Negatif gecikme günü hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": 100,
            "delay_day": -3,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "negatif" in error

    def test_non_numeric_balance_string(self):
        """Sayısal olmayan bakiye string hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": "abc",
            "delay_day": 0,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "sayısal" in error

    def test_valid_string_numeric_values(self):
        """String olarak gelen sayısal değerler kabul edilir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": "5000",
            "delay_day": "10",
            "active_project_count": "3",
        }
        assert validate_customer_input_service(data) is None

    def test_float_delay_day_raises(self):
        """Ondalıklı gecikme günü hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": 100,
            "delay_day": 5.5,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "tam sayı" in error

    def test_none_field_value(self):
        """None alan değeri hata verir."""
        data = {
            "customer_name": "Test",
            "company_name": "Şirket",
            "balance": None,
            "delay_day": 0,
            "active_project_count": 1,
        }
        error = validate_customer_input_service(data)
        assert error is not None
        assert "eksik" in error


# ═══════════════════════════════════════════════════════════════════
# calculate_risk_service testleri
# ═══════════════════════════════════════════════════════════════════


class TestCalculateRiskService:
    """calculate_risk_service fonksiyonu testleri."""

    # ── High Risk ────────────────────────────────────────────

    def test_high_risk_high_balance(self):
        """Bakiye > 50.000 → High Risk."""
        assert calculate_risk_service(60_000, 0) == "High Risk"

    def test_high_risk_high_delay(self):
        """Gecikme > 30 gün → High Risk."""
        assert calculate_risk_service(1_000, 35) == "High Risk"

    def test_high_risk_both(self):
        """Hem bakiye hem gecikme yüksek → High Risk."""
        assert calculate_risk_service(100_000, 45) == "High Risk"

    def test_boundary_balance_50000_not_high(self):
        """Bakiye tam 50.000 → High Risk DEĞİL (strict >)."""
        assert calculate_risk_service(50_000, 0) != "High Risk"

    def test_boundary_delay_30_not_high(self):
        """Gecikme tam 30 gün → High Risk DEĞİL (strict >)."""
        assert calculate_risk_service(0, 30) != "High Risk"

    # ── Medium Risk ──────────────────────────────────────────

    def test_medium_risk_balance(self):
        """Bakiye > 20.000 (≤ 50.000) → Medium Risk."""
        assert calculate_risk_service(30_000, 0) == "Medium Risk"

    def test_medium_risk_delay(self):
        """Gecikme > 15 (≤ 30) → Medium Risk."""
        assert calculate_risk_service(1_000, 20) == "Medium Risk"

    def test_boundary_balance_20000_not_medium(self):
        """Bakiye tam 20.000 → Medium Risk DEĞİL (strict >)."""
        assert calculate_risk_service(20_000, 0) != "Medium Risk"

    def test_boundary_delay_15_not_medium(self):
        """Gecikme tam 15 gün → Medium Risk DEĞİL (strict >)."""
        assert calculate_risk_service(0, 15) != "Medium Risk"

    # ── Low Risk ─────────────────────────────────────────────

    def test_low_risk(self):
        """Düşük bakiye ve gecikme → Low Risk."""
        assert calculate_risk_service(5_000, 5) == "Low Risk"

    def test_low_risk_zero_values(self):
        """Bakiye 0 ve gecikme 0 → Low Risk."""
        assert calculate_risk_service(0, 0) == "Low Risk"


# ═══════════════════════════════════════════════════════════════════
# add_customer_service testleri
# ═══════════════════════════════════════════════════════════════════


class TestAddCustomerService:
    """add_customer_service fonksiyonu testleri."""

    def test_add_success(self):
        """Geçerli veri ile müşteri eklenir ve risk_level atanır."""
        data = {
            "customer_name": "Ahmet",
            "company_name": "ABC Ltd.",
            "balance": 10_000,
            "delay_day": 5,
            "active_project_count": 2,
        }
        result = add_customer_service(data)
        assert result["customer_name"] == "Ahmet"
        assert result["risk_level"] == "Low Risk"
        assert len(get_all_customers()) == 1

    def test_add_high_risk_customer(self):
        """Yüksek riskli müşteri doğru etiketlenir."""
        data = {
            "customer_name": "Riskli",
            "company_name": "Risk A.Ş.",
            "balance": 60_000,
            "delay_day": 0,
            "active_project_count": 1,
        }
        result = add_customer_service(data)
        assert result["risk_level"] == "High Risk"

    def test_add_invalid_data_raises(self):
        """Geçersiz veri ValueError fırlatır."""
        data = {
            "customer_name": "",
            "company_name": "Şirket",
            "balance": -100,
            "delay_day": 0,
            "active_project_count": 1,
        }
        with pytest.raises(ValueError):
            add_customer_service(data)

    def test_add_with_string_values(self):
        """String sayısal değerler doğru dönüştürülür."""
        data = {
            "customer_name": "Test",
            "company_name": "Test Ltd.",
            "balance": "25000",
            "delay_day": "10",
            "active_project_count": "3",
        }
        result = add_customer_service(data)
        assert result["balance"] == 25_000.0
        assert result["delay_day"] == 10
        assert result["active_project_count"] == 3

    def test_workflow_order(self):
        """İş akışı sırası: doğrulama → risk → kayıt."""
        # Geçersiz veri — doğrulama aşamasında durmalı, listeye eklememeli
        data = {
            "customer_name": "",
            "company_name": "",
            "balance": -1,
            "delay_day": 0,
            "active_project_count": 0,
        }
        with pytest.raises(ValueError):
            add_customer_service(data)
        assert len(get_all_customers()) == 0


# ═══════════════════════════════════════════════════════════════════
# calculate_dashboard_summary_service testleri
# ═══════════════════════════════════════════════════════════════════


class TestDashboardSummaryService:
    """calculate_dashboard_summary_service fonksiyonu testleri."""

    def test_empty_dashboard(self):
        """Müşteri yokken dashboard sıfır değerler döner."""
        summary = calculate_dashboard_summary_service()
        assert summary["total_customers"] == 0
        assert summary["average_balance"] == 0
        assert summary["max_balance"] == 0
        assert summary["max_delay_day"] == 0
        assert summary["risk_distribution"]["High Risk"] == 0
        assert summary["risk_distribution"]["Medium Risk"] == 0
        assert summary["risk_distribution"]["Low Risk"] == 0

    def test_dashboard_after_adding_customers(self):
        """Müşteri eklendikten sonra dashboard doğru hesaplanır."""
        add_customer_service({
            "customer_name": "A",
            "company_name": "A Ltd.",
            "balance": 60_000,
            "delay_day": 35,
            "active_project_count": 1,
        })
        add_customer_service({
            "customer_name": "B",
            "company_name": "B Ltd.",
            "balance": 25_000,
            "delay_day": 10,
            "active_project_count": 2,
        })
        add_customer_service({
            "customer_name": "C",
            "company_name": "C Ltd.",
            "balance": 5_000,
            "delay_day": 3,
            "active_project_count": 1,
        })

        summary = calculate_dashboard_summary_service()

        assert summary["total_customers"] == 3
        assert summary["risk_distribution"]["High Risk"] == 1
        assert summary["risk_distribution"]["Medium Risk"] == 1
        assert summary["risk_distribution"]["Low Risk"] == 1
        assert summary["max_balance"] == 60_000
        assert summary["max_delay_day"] == 35
        assert summary["average_balance"] == round((60_000 + 25_000 + 5_000) / 3, 2)

    def test_dashboard_recalculates_after_new_customer(self):
        """Yeni müşteri eklenince dashboard yeniden hesaplanır."""
        add_customer_service({
            "customer_name": "İlk",
            "company_name": "İlk Ltd.",
            "balance": 10_000,
            "delay_day": 0,
            "active_project_count": 1,
        })
        s1 = calculate_dashboard_summary_service()
        assert s1["total_customers"] == 1

        add_customer_service({
            "customer_name": "İkinci",
            "company_name": "İkinci Ltd.",
            "balance": 20_000,
            "delay_day": 5,
            "active_project_count": 2,
        })
        s2 = calculate_dashboard_summary_service()
        assert s2["total_customers"] == 2
        assert s2["average_balance"] == round((10_000 + 20_000) / 2, 2)


# ═══════════════════════════════════════════════════════════════════
# load_test_customers_service testleri
# ═══════════════════════════════════════════════════════════════════


class TestLoadTestCustomersService:
    """load_test_customers_service fonksiyonu testleri."""

    def test_loads_at_least_three(self):
        """En az 3 test müşterisi yüklenir."""
        added = load_test_customers_service()
        assert len(added) >= 3
        assert len(get_all_customers()) >= 3

    def test_different_risk_levels(self):
        """Yüklenen test verileri farklı risk seviyelerine sahip."""
        added = load_test_customers_service()
        risk_levels = {c["risk_level"] for c in added}
        assert "High Risk" in risk_levels
        assert "Medium Risk" in risk_levels
        assert "Low Risk" in risk_levels

    def test_dashboard_after_test_data(self):
        """Test verisi yüklendikten sonra dashboard doğru çalışır."""
        load_test_customers_service()
        summary = calculate_dashboard_summary_service()
        assert summary["total_customers"] >= 3
        assert summary["max_balance"] > 0
        assert summary["average_balance"] > 0

    def test_all_records_have_required_fields(self):
        """Tüm test kayıtları gerekli alanlara sahip."""
        added = load_test_customers_service()
        required = [
            "customer_name", "company_name", "balance",
            "delay_day", "active_project_count", "risk_level",
        ]
        for record in added:
            for field in required:
                assert field in record, f"'{field}' alanı eksik: {record}"
