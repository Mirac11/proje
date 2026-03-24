"""
FRMYS - Veritabanı Yönetim Modülü
SQLite bağlantı yönetimi ve tablo oluşturma işlemleri.
"""

import sqlite3
import os


class DatabaseManager:
    """SQLite veritabanı bağlantı ve şema yöneticisi."""

    def __init__(self, db_path: str = None):
        """
        DatabaseManager oluşturur.

        Args:
            db_path: SQLite veritabanı dosya yolu.
                     None ise proje dizininde 'frmys.db' kullanılır.
                     ':memory:' ise in-memory veritabanı kullanılır (testler için).
        """
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "frmys.db")
        self.db_path = db_path
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Veritabanına bağlantı açar ve döndürür."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self):
        """Açık bağlantıyı kapatır."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def initialize_db(self):
        """Customers tablosunu oluşturur (yoksa)."""
        conn = self.connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                balance         REAL    NOT NULL DEFAULT 0,
                delay_days      INTEGER NOT NULL DEFAULT 0,
                active_projects INTEGER NOT NULL DEFAULT 0,
                risk_level      TEXT,
                alerts          TEXT,
                created_at      TEXT    NOT NULL,
                updated_at      TEXT    NOT NULL
            )
        """)
        conn.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Tek bir SQL sorgusu çalıştırır."""
        conn = self.connect()
        return conn.execute(query, params)

    def commit(self):
        """Bekleyen değişiklikleri veritabanına yazar."""
        if self._connection is not None:
            self._connection.commit()
