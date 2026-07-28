"""
database/models.py — Definisi tabel SQLAlchemy untuk sistem penyewaan lapangan.

Class:
    Base          — DeclarativeBase wajib sebagai induk semua model.
    LapanganDB    — Tabel 'lapangan', one-to-many ke PemesananDB.
    PemesananDB   — Tabel 'pemesanan', many-to-one ke LapanganDB.
"""

from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class wajib untuk semua model SQLAlchemy."""
    pass


class LapanganDB(Base):
    """
    Model tabel 'lapangan'.

    Kolom:
        id           — Primary key, auto-increment.
        nomor        — Kode unik lapangan (misal 'F1'), tidak boleh null.
        jenis        — 'Futsal' atau 'Badminton'.
        harga_per_jam — Harga sewa per jam dalam rupiah.

    Relasi:
        pemesanan_list — Daftar PemesananDB yang terkait lapangan ini.
    """

    __tablename__ = "lapangan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nomor: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    jenis: Mapped[str] = mapped_column(String(20))
    harga_per_jam: Mapped[float] = mapped_column(Float)

    pemesanan_list: Mapped[list["PemesananDB"]] = relationship(
        "PemesananDB", back_populates="lapangan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (f"LapanganDB(nomor={self.nomor!r}, jenis={self.jenis!r}, "
                f"harga={self.harga_per_jam})")


class PemesananDB(Base):
    """
    Model tabel 'pemesanan'.

    Kolom:
        id           — Primary key, auto-increment.
        lapangan_id  — Foreign key ke lapangan.id.
        nama_pemesan — Nama orang yang memesan.
        jam_mulai    — Jam mulai sewa, misal '08:00'.
        jam_selesai  — Jam selesai sewa, misal '10:00'.
        total_biaya  — Total biaya yang dibayar.
        waktu_pesan  — Waktu saat pemesanan dibuat.

    Relasi:
        lapangan — Objek LapanganDB yang dipesan.
    """

    __tablename__ = "pemesanan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lapangan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lapangan.id"), nullable=False
    )
    nama_pemesan: Mapped[str] = mapped_column(String(100))
    jam_mulai: Mapped[str] = mapped_column(String(10))
    jam_selesai: Mapped[str] = mapped_column(String(10))
    total_biaya: Mapped[float] = mapped_column(Float)
    waktu_pesan: Mapped[str] = mapped_column(String(20))

    lapangan: Mapped["LapanganDB"] = relationship(
        "LapanganDB", back_populates="pemesanan_list"
    )

    def __repr__(self) -> str:
        return (f"PemesananDB(nama={self.nama_pemesan!r}, "
                f"jam={self.jam_mulai}-{self.jam_selesai}, "
                f"biaya={self.total_biaya})")