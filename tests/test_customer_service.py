"""
Test: Müşteri Servisi (customer_service.py)
CRUD işlemleri ve dashboard özeti (in-memory SQLite).
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.db_manager import DatabaseManager
from backend.services.customer_service import CustomerService
from backend.utils.validators import ValidationError


@pytest.fixture
def service():
    """Her test için temiz in-memory veritabanı ve servis oluşturur."""
    db = DatabaseManager(db_path=":memory:")
    db.connect()
    db.initialize_db()
    svc = CustomerService(db)
    yield svc
    db.close()


class TestCreateCustomer:
    """create_customer testleri."""

    def test_create_success(self, service):
        """Geçerli veriyle müşteri oluşturulur ve risk hesaplanır."""
        customer = service.create_customer("Ahmet Yılmaz", 10_000, 5, 2)
        assert customer.id is not None
        assert customer.name == "Ahmet Yılmaz"
        assert customer.balance == 10_000.0
        assert customer.delay_days == 5
        assert customer.active_projects == 2
        assert customer.risk_level == "Normal"
        assert customer.created_at != ""

    def test_create_high_risk(self, service):
        """Yüksek riskli müşteri doğru etiketlenir."""
        customer = service.create_customer("Riskli Müşteri", 60_000, 0, 1)
        assert customer.risk_level == "Yüksek Risk"

    def test_create_invalid_data_raises(self, service):
        """Geçersiz veriyle ValidationError fırlatılır."""
        with pytest.raises(ValidationError):
            service.create_customer("", -100, 0, 1)

    def test_create_with_string_inputs(self, service):
        """GUI'den gelen string değerler doğru dönüştürülür."""
        customer = service.create_customer("Test", "5000", "10", "3")
        assert customer.balance == 5000.0
        assert customer.delay_days == 10
        assert customer.active_projects == 3


class TestGetCustomer:
    """get_customer testleri."""

    def test_get_existing(self, service):
        """Var olan müşteri getirilir."""
        created = service.create_customer("Test Müşteri", 1000, 0, 1)
        fetched = service.get_customer(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Test Müşteri"

    def test_get_nonexistent(self, service):
        """Olmayan müşteri None döner."""
        assert service.get_customer(999) is None


class TestGetAllCustomers:
    """get_all_customers testleri."""

    def test_empty_db(self, service):
        """Boş veritabanı boş liste döner."""
        assert service.get_all_customers() == []

    def test_multiple_customers(self, service):
        """Birden fazla müşteri listeye eklenir."""
        service.create_customer("Müşteri 1", 1000, 0, 1)
        service.create_customer("Müşteri 2", 2000, 5, 2)
        service.create_customer("Müşteri 3", 3000, 10, 0)
        customers = service.get_all_customers()
        assert len(customers) == 3


class TestUpdateCustomer:
    """update_customer testleri."""

    def test_update_success(self, service):
        """Müşteri bilgileri güncellenir ve risk yeniden hesaplanır."""
        created = service.create_customer("Eski İsim", 1000, 0, 1)
        updated = service.update_customer(
            created.id, name="Yeni İsim", balance=60_000
        )
        assert updated is not None
        assert updated.name == "Yeni İsim"
        assert updated.balance == 60_000.0
        assert updated.risk_level == "Yüksek Risk"
        # Değişmeyen alanlar korunur
        assert updated.delay_days == 0
        assert updated.active_projects == 1

    def test_update_nonexistent(self, service):
        """Olmayan müşteri güncellemesi None döner."""
        assert service.update_customer(999, name="Test") is None

    def test_update_partial_fields(self, service):
        """Sadece belirtilen alanlar güncellenir."""
        created = service.create_customer("Test", 5000, 10, 3)
        updated = service.update_customer(created.id, delay_days=25)
        assert updated.name == "Test"
        assert updated.balance == 5000.0
        assert updated.delay_days == 25
        assert updated.active_projects == 3


class TestDeleteCustomer:
    """delete_customer testleri."""

    def test_delete_existing(self, service):
        """Var olan müşteri silindikten sonra getirilemez."""
        created = service.create_customer("Silinecek", 1000, 0, 1)
        assert service.delete_customer(created.id) is True
        assert service.get_customer(created.id) is None

    def test_delete_nonexistent(self, service):
        """Olmayan müşteriyi silmek False döner."""
        assert service.delete_customer(999) is False


class TestDashboardSummary:
    """get_dashboard_summary testleri."""

    def test_empty_dashboard(self, service):
        """Boş veritabanı için dashboard özeti."""
        summary = service.get_dashboard_summary()
        assert summary["total_customers"] == 0
        assert summary["total_balance"] == 0.0
        assert summary["urgent_alerts"] == []
        assert summary["collection_required"] == []
        assert summary["passive_customers"] == []

    def test_dashboard_with_mixed_customers(self, service):
        """Farklı risk profillerinde müşterilerle dashboard testi."""
        # Normal müşteri
        service.create_customer("Normal", 10_000, 0, 2)
        # Yüksek riskli müşteri (bakiye > 50k)
        service.create_customer("Riskli", 80_000, 0, 1)
        # Acil uyarı müşterisi (gecikme > 20)
        service.create_customer("Acil", 5_000, 25, 1)
        # Pasif müşteri (aktif proje = 0)
        service.create_customer("Pasif", 2_000, 0, 0)
        # Tahsilat takibi müşterisi (gecikme > 0)
        service.create_customer("Tahsilat", 3_000, 5, 1)

        summary = service.get_dashboard_summary()

        assert summary["total_customers"] == 5
        assert summary["total_balance"] == 100_000.0

        # Risk dağılımı
        assert summary["risk_distribution"]["Yüksek Risk"] == 1
        assert summary["risk_distribution"]["Normal"] == 4

        # Acil uyarılar (gecikme > 20)
        assert len(summary["urgent_alerts"]) == 1
        assert summary["urgent_alerts"][0].name == "Acil"

        # Tahsilat takibi (gecikme > 0)
        assert len(summary["collection_required"]) == 2  # Acil + Tahsilat

        # Pasif müşteriler
        assert len(summary["passive_customers"]) == 1
        assert summary["passive_customers"][0].name == "Pasif"
