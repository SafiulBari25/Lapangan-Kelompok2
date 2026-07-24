"""
database/db_handler.py — Fungsi CRUD untuk sistem penyewaan lapangan.

Fungsi:
    init_db()                — Buat semua tabel jika belum ada.
    simpan_lapangan()        — Tambah lapangan baru ke database.
    ambil_semua_lapangan()   — Ambil seluruh data lapangan dari database.
    update_harga_lapangan()  — Perbarui harga sewa lapangan tertentu.
    simpan_pemesanan()       — Simpan rekaman pemesanan ke database.
    ambil_semua_pemesanan()  — Ambil seluruh riwayat pemesanan.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import Base, LapanganDB, PemesananDB

# Koneksi ke file database di root folder proyek
engine = create_engine("sqlite:///gedung.db", echo=False)


def init_db() -> None:
    """
    Buat semua tabel jika belum ada.

    Dipanggil SEKALI saat program mulai, sebelum menu ditampilkan.
    """
    Base.metadata.create_all(engine)


def simpan_lapangan(nomor: str, jenis: str, harga_per_jam: float) -> LapanganDB:
    """
    Tambah baris baru ke tabel lapangan.

    Args:
        nomor: Kode unik lapangan.
        jenis: 'Futsal' atau 'Badminton'.
        harga_per_jam: Harga sewa per jam.

    Returns:
        Objek LapanganDB yang sudah tersimpan.
    """
    with Session(engine) as session:
        lap_db = LapanganDB(nomor=nomor, jenis=jenis, harga_per_jam=harga_per_jam)
        session.add(lap_db)
        session.commit()
        session.refresh(lap_db)
        # Detach supaya bisa dipakai di luar session
        session.expunge(lap_db)
        return lap_db


def ambil_semua_lapangan() -> list[LapanganDB]:
    """
    Ambil seluruh data lapangan dari database.

    Returns:
        List LapanganDB semua lapangan yang tersimpan.
    """
    with Session(engine) as session:
        hasil = session.query(LapanganDB).all()
        for lap in hasil:
            session.expunge(lap)
        return hasil


def update_harga_lapangan(nomor: str, harga_baru: float) -> None:
    """
    Perbarui harga sewa lapangan berdasarkan nomor.

    Args:
        nomor: Kode lapangan yang akan diupdate.
        harga_baru: Harga sewa per jam yang baru.
    """
    with Session(engine) as session:
        lap = session.query(LapanganDB).filter_by(nomor=nomor).first()
        if lap:
            lap.harga_per_jam = harga_baru
            session.commit()


def simpan_pemesanan(
    lapangan_id: int,
    nama_pemesan: str,
    jam_mulai: str,
    jam_selesai: str,
    total_biaya: float,
    waktu_pesan: str,
) -> PemesananDB:
    """
    Tambah baris baru ke tabel pemesanan.

    Args:
        lapangan_id: ID (PK) lapangan yang dipesan.
        nama_pemesan: Nama orang yang memesan.
        jam_mulai: Jam mulai sewa, misal '08:00'.
        jam_selesai: Jam selesai sewa, misal '10:00'.
        total_biaya: Total biaya yang dibayar.
        waktu_pesan: Waktu saat pemesanan dibuat.

    Returns:
        Objek PemesananDB yang sudah tersimpan.
    """
    with Session(engine) as session:
        pes_db = PemesananDB(
            lapangan_id=lapangan_id,
            nama_pemesan=nama_pemesan,
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai,
            total_biaya=total_biaya,
            waktu_pesan=waktu_pesan,
        )
        session.add(pes_db)
        session.commit()
        session.refresh(pes_db)
        session.expunge(pes_db)
        return pes_db


def ambil_semua_pemesanan() -> list[PemesananDB]:
    """
    Ambil seluruh riwayat pemesanan dari database.

    Returns:
        List PemesananDB seluruh pemesanan yang pernah terjadi.
    """
    with Session(engine) as session:
        hasil = session.query(PemesananDB).all()
        for p in hasil:
            session.expunge(p)
        return hasil