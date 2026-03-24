"""
FRMYS - Veri Doğrulama Modülü
Arayüzden gelen müşteri verilerinin tip ve değer kontrolleri.
"""


class ValidationError(Exception):
    """Doğrulama hatası. errors özelliği hata listesini içerir."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_customer_data(
    name: str,
    balance,
    delay_days,
    active_projects,
) -> dict:
    """
    Müşteri verilerini doğrular ve temizlenmiş değerleri döndürür.

    Args:
        name: Müşteri adı.
        balance: Toplam bakiye (str veya sayısal).
        delay_days: Gecikme süresi gün (str veya sayısal).
        active_projects: Aktif proje sayısı (str veya sayısal).

    Returns:
        Temizlenmiş değerler içeren dict:
        {"name", "balance", "delay_days", "active_projects"}

    Raises:
        ValidationError: Doğrulama hataları varsa.
    """
    errors: list[str] = []

    # --- İsim doğrulama ---
    if not isinstance(name, str) or not name.strip():
        errors.append("Müşteri adı boş olamaz.")
    elif len(name.strip()) > 100:
        errors.append("Müşteri adı en fazla 100 karakter olabilir.")

    # --- Bakiye doğrulama ---
    validated_balance = _validate_numeric(
        value=balance,
        field_name="Bakiye",
        allow_float=True,
        min_value=0,
        errors=errors,
    )

    # --- Gecikme süresi doğrulama ---
    validated_delay = _validate_numeric(
        value=delay_days,
        field_name="Gecikme süresi",
        allow_float=False,
        min_value=0,
        errors=errors,
    )

    # --- Aktif proje sayısı doğrulama ---
    validated_projects = _validate_numeric(
        value=active_projects,
        field_name="Aktif proje sayısı",
        allow_float=False,
        min_value=0,
        errors=errors,
    )

    if errors:
        raise ValidationError(errors)

    return {
        "name": name.strip(),
        "balance": validated_balance,
        "delay_days": validated_delay,
        "active_projects": validated_projects,
    }


def _validate_numeric(
    value,
    field_name: str,
    allow_float: bool,
    min_value: float | int,
    errors: list[str],
) -> float | int | None:
    """
    Sayısal alan doğrulaması yapar.

    Returns:
        Dönüştürülmüş değer veya hata durumunda None.
    """
    # String'den dönüştürme (GUI'den gelen veriler string olabilir)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            errors.append(f"{field_name} boş olamaz.")
            return None
        try:
            value = float(value) if allow_float else int(value)
        except ValueError:
            expected = "sayısal bir değer" if allow_float else "tam sayı"
            errors.append(f"{field_name} geçerli bir {expected} olmalıdır.")
            return None

    # Tip kontrolü
    if allow_float:
        if not isinstance(value, (int, float)):
            errors.append(f"{field_name} sayısal bir değer olmalıdır.")
            return None
        value = float(value)
    else:
        if isinstance(value, float):
            if value != int(value):
                errors.append(f"{field_name} tam sayı olmalıdır.")
                return None
            value = int(value)
        if not isinstance(value, int):
            errors.append(f"{field_name} tam sayı olmalıdır.")
            return None

    # Minimum değer kontrolü
    if value < min_value:
        errors.append(f"{field_name} {min_value} değerinden küçük olamaz.")
        return None

    return value
