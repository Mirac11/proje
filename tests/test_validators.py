"""
Test: Veri Doğrulama Modülü (validators.py)
"""

import pytest
import sys
import os

# Proje kök dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.validators import validate_customer_data, ValidationError


class TestValidateCustomerData:
    """validate_customer_data fonksiyonu testleri."""

    # ── Başarılı senaryolar ──────────────────────────────────

    def test_valid_data_numeric(self):
        """Sayısal değerlerle geçerli veri."""
        result = validate_customer_data("Ahmet Yılmaz", 10000.0, 5, 3)
        assert result["name"] == "Ahmet Yılmaz"
        assert result["balance"] == 10000.0
        assert result["delay_days"] == 5
        assert result["active_projects"] == 3

    def test_valid_data_string_inputs(self):
        """String değerlerle (GUI'den gelir) geçerli veri."""
        result = validate_customer_data("Mehmet Kaya", "25000.50", "10", "2")
        assert result["balance"] == 25000.50
        assert result["delay_days"] == 10
        assert result["active_projects"] == 2

    def test_valid_data_zero_values(self):
        """Sıfır değerler geçerlidir."""
        result = validate_customer_data("Test Müşteri", 0, 0, 0)
        assert result["balance"] == 0.0
        assert result["delay_days"] == 0
        assert result["active_projects"] == 0

    def test_name_trimmed(self):
        """İsim baş ve sondaki boşluklardan temizlenir."""
        result = validate_customer_data("  Ali Veli  ", 100, 0, 1)
        assert result["name"] == "Ali Veli"

    # ── İsim hata senaryoları ────────────────────────────────

    def test_empty_name_raises(self):
        """Boş isim hata verir."""
        with pytest.raises(ValidationError) as exc_info:
            validate_customer_data("", 100, 0, 1)
        assert "Müşteri adı boş olamaz" in str(exc_info.value)

    def test_whitespace_name_raises(self):
        """Sadece boşluk olan isim hata verir."""
        with pytest.raises(ValidationError):
            validate_customer_data("   ", 100, 0, 1)

    def test_long_name_raises(self):
        """100 karakterden uzun isim hata verir."""
        with pytest.raises(ValidationError) as exc_info:
            validate_customer_data("A" * 101, 100, 0, 1)
        assert "100 karakter" in str(exc_info.value)

    # ── Bakiye hata senaryoları ──────────────────────────────

    def test_negative_balance_raises(self):
        """Negatif bakiye hata verir."""
        with pytest.raises(ValidationError) as exc_info:
            validate_customer_data("Test", -1, 0, 1)
        assert "Bakiye" in str(exc_info.value)

    def test_non_numeric_balance_raises(self):
        """Sayısal olmayan bakiye hata verir."""
        with pytest.raises(ValidationError):
            validate_customer_data("Test", "abc", 0, 1)

    # ── Gecikme süresi hata senaryoları ──────────────────────

    def test_negative_delay_raises(self):
        """Negatif gecikme hata verir."""
        with pytest.raises(ValidationError):
            validate_customer_data("Test", 100, -5, 1)

    def test_float_delay_raises(self):
        """Ondalıklı gecikme hata verir (tam sayı olmalı)."""
        with pytest.raises(ValidationError):
            validate_customer_data("Test", 100, 5.5, 1)

    # ── Aktif proje hata senaryoları ─────────────────────────

    def test_negative_projects_raises(self):
        """Negatif proje sayısı hata verir."""
        with pytest.raises(ValidationError):
            validate_customer_data("Test", 100, 0, -1)

    # ── Çoklu hata senaryosu ─────────────────────────────────

    def test_multiple_errors_collected(self):
        """Birden fazla hata tek seferde toplanır."""
        with pytest.raises(ValidationError) as exc_info:
            validate_customer_data("", -100, -5, -1)
        assert len(exc_info.value.errors) >= 3
