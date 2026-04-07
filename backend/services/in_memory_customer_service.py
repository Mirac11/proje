"""
FRMYS - In-Memory Müşteri Servisi
Bellek tabanlı (liste) veri yapısı üzerinde çalışan iş kuralları.

Veri Yapısı:
  Her müşteri kaydı dict olarak saklanır:
    - customer_name       : str
    - company_name        : str
    - balance             : float
    - delay_day           : int
    - active_project_count: int
    - risk_level          : str   (otomatik hesaplanır)

Risk Kuralları:
  🔴 High Risk   : balance > 50.000 VEYA delay_day > 30
  🟡 Medium Risk : balance > 20.000 VEYA delay_day > 15
  🟢 Low Risk    : Diğer tüm durumlar
"""

from typing import Optional

# ── Bellekteki Müşteri Listesi (In-Memory Store) ─────────────────
_customers: list[dict] = []


# ── 1) Veri Doğrulama ────────────────────────────────────────────

def validate_customer_input_service(data: dict) -> Optional[str]:
    """
    Müşteri verisini doğrular.

    Kontroller:
      - Tüm zorunlu alanların mevcut ve boş olmaması.
      - balance, delay_day, active_project_count alanlarının
        sayısal olması ve negatif olmaması.

    Args:
        data: Müşteri alanlarını içeren sözlük.
              Beklenen anahtarlar:
                customer_name, company_name, balance,
                delay_day, active_project_count

    Returns:
        Hata mesajı (str) varsa; geçerliyse None.
    """
    required_fields = [
        "customer_name",
        "company_name",
        "balance",
        "delay_day",
        "active_project_count",
    ]

    # ── Boş alan kontrolü ────────────────────────────────────
    for field in required_fields:
        value = data.get(field)
        if value is None:
            return f"'{field}' alanı eksik."
        if isinstance(value, str) and not value.strip():
            return f"'{field}' alanı boş olamaz."

    # ── Sayısal alan kontrolü ────────────────────────────────
    numeric_fields = {
        "balance": "Bakiye",
        "delay_day": "Gecikme günü",
        "active_project_count": "Aktif proje sayısı",
    }

    for field_key, display_name in numeric_fields.items():
        raw_value = data.get(field_key)

        # String'den dönüştürme denemesi
        if isinstance(raw_value, str):
            raw_value = raw_value.strip()
            try:
                raw_value = float(raw_value)
            except ValueError:
                return f"'{display_name}' sayısal bir değer olmalıdır."

        # Tip kontrolü
        if not isinstance(raw_value, (int, float)):
            return f"'{display_name}' sayısal bir değer olmalıdır."

        # Negatif değer kontrolü
        if raw_value < 0:
            return f"'{display_name}' negatif olamaz."

    # ── Tam sayı kontrolü (delay_day, active_project_count) ──
    for field_key in ("delay_day", "active_project_count"):
        raw_value = data.get(field_key)
        if isinstance(raw_value, str):
            raw_value = raw_value.strip()
            try:
                raw_value = float(raw_value)
            except ValueError:
                pass  # Yukarıda zaten yakalanır
        if isinstance(raw_value, float) and raw_value != int(raw_value):
            display = numeric_fields[field_key]
            return f"'{display}' tam sayı olmalıdır."

    return None  # Doğrulama başarılı


# ── 2) Risk Hesaplama ────────────────────────────────────────────

def calculate_risk_service(balance: float, delay_day: int) -> str:
    """
    Bakiye ve gecikme gününe göre risk seviyesi hesaplar.

    Kurallar (öncelik sırasıyla):
      1. balance > 50.000 VEYA delay_day > 30  →  "High Risk"
      2. balance > 20.000 VEYA delay_day > 15  →  "Medium Risk"
      3. Diğer                                 →  "Low Risk"

    Args:
        balance:   Müşteri bakiyesi (≥ 0).
        delay_day: Gecikme süresi, gün (≥ 0).

    Returns:
        "High Risk", "Medium Risk" veya "Low Risk".
    """
    balance = float(balance)
    delay_day = int(delay_day)

    if balance > 50_000 or delay_day > 30:
        return "High Risk"
    if balance > 20_000 or delay_day > 15:
        return "Medium Risk"
    return "Low Risk"


# ── 3) Müşteri Ekleme ───────────────────────────────────────────

def add_customer_service(data: dict) -> dict:
    """
    Doğrulanmış ve risk seviyesi hesaplanmış müşteriyi
    bellekteki listeye ekler.

    İş akışı:
      1. validate_customer_input_service ile doğrulama yapılır.
      2. calculate_risk_service ile risk seviyesi hesaplanır.
      3. Kayıt listeye eklenir.

    Args:
        data: Müşteri alanlarını içeren sözlük.

    Returns:
        Eklenen müşteri kaydı (risk_level dahil).

    Raises:
        ValueError: Doğrulama hatası varsa.
    """
    # Adım 1 — Doğrulama
    error = validate_customer_input_service(data)
    if error is not None:
        raise ValueError(error)

    # Sayısal değerleri normalize et
    balance = float(data["balance"]) if isinstance(data["balance"], str) else float(data["balance"])
    delay_day = int(float(data["delay_day"])) if isinstance(data["delay_day"], str) else int(data["delay_day"])
    active_project_count = (
        int(float(data["active_project_count"]))
        if isinstance(data["active_project_count"], str)
        else int(data["active_project_count"])
    )

    # Adım 2 — Risk hesaplama
    risk_level = calculate_risk_service(balance, delay_day)

    # Adım 3 — Kayıt oluştur ve listeye ekle
    customer_record = {
        "customer_name": data["customer_name"].strip(),
        "company_name": data["company_name"].strip(),
        "balance": balance,
        "delay_day": delay_day,
        "active_project_count": active_project_count,
        "risk_level": risk_level,
    }

    _customers.append(customer_record)
    return customer_record


# ── 4) Dashboard Özet Hesaplama ──────────────────────────────────

def calculate_dashboard_summary_service() -> dict:
    """
    Tüm müşteri verilerinden dashboard özet bilgisini hesaplar.

    Döndürülen değerler:
      - total_customers       : Toplam müşteri sayısı
      - risk_distribution     : {"High Risk": n, "Medium Risk": n, "Low Risk": n}
      - average_balance       : Ortalama bakiye (müşteri yoksa 0)
      - max_balance           : En yüksek bakiye (müşteri yoksa 0)
      - max_delay_day         : En uzun gecikme günü (müşteri yoksa 0)

    Returns:
        Dashboard özet sözlüğü.
    """
    total = len(_customers)

    risk_distribution = {"High Risk": 0, "Medium Risk": 0, "Low Risk": 0}
    total_balance = 0.0
    max_balance = 0.0
    max_delay = 0

    for c in _customers:
        # Risk dağılımı
        level = c.get("risk_level", "Low Risk")
        if level in risk_distribution:
            risk_distribution[level] += 1

        # Bakiye istatistikleri
        bal = c.get("balance", 0.0)
        total_balance += bal
        if bal > max_balance:
            max_balance = bal

        # Gecikme istatistiği
        delay = c.get("delay_day", 0)
        if delay > max_delay:
            max_delay = delay

    average_balance = total_balance / total if total > 0 else 0.0

    return {
        "total_customers": total,
        "risk_distribution": risk_distribution,
        "average_balance": round(average_balance, 2),
        "max_balance": max_balance,
        "max_delay_day": max_delay,
    }


# ── 5) Test Verisi Yükleme ──────────────────────────────────────

def load_test_customers_service() -> list[dict]:
    """
    Farklı risk seviyelerinde en az 3 örnek müşteriyi
    otomatik oluşturup listeye ekler.

    Eklenen test müşterileri:
      1. High Risk   — Büyük bakiye + uzun gecikme
      2. Medium Risk  — Orta bakiye
      3. Low Risk     — Düşük bakiye, gecikme yok

    Returns:
        Eklenen test müşteri kayıtlarının listesi.
    """
    test_data = [
        {
            "customer_name": "Ahmet Yılmaz",
            "company_name": "Yılmaz Holding A.Ş.",
            "balance": 75_000,
            "delay_day": 45,
            "active_project_count": 3,
        },
        {
            "customer_name": "Elif Demir",
            "company_name": "Demir Teknoloji Ltd.",
            "balance": 30_000,
            "delay_day": 10,
            "active_project_count": 2,
        },
        {
            "customer_name": "Mehmet Kaya",
            "company_name": "Kaya Yazılım",
            "balance": 5_000,
            "delay_day": 3,
            "active_project_count": 1,
        },
    ]

    added: list[dict] = []
    for entry in test_data:
        record = add_customer_service(entry)
        added.append(record)

    return added


# ── Yardımcı Fonksiyonlar ────────────────────────────────────────

def get_all_customers() -> list[dict]:
    """Bellekteki tüm müşteri kayıtlarını döndürür."""
    return list(_customers)


def clear_all_customers() -> None:
    """Bellekteki tüm müşteri verilerini temizler (test amaçlı)."""
    _customers.clear()
