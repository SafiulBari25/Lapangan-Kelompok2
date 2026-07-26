"""
tests/test_gedung.py — Unit test lengkap UTS + UAS.

Jalankan: pytest tests/ -v

Test UTS  (14 test): class lapangan, slot, pemesanan, gedung.
Test UAS Layer 1 (3 test): SQLAlchemy in-memory database.
Test UAS Layer 2 (4 test): REST API mock + functional pipeline.
Total minimal: 21 test.
"""

import sys
import os
import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from exceptions.custom_exceptions import (
    SlotSudahDipesanError,
    LapanganTidakDitemukanError,
    SlotTidakValidError,
    PemesananTidakDitemukanError,
)
from models.lapangan import Lapangan, LapanganFutsal, LapanganBadminton
from models.slot import Slot, SlotTersedia, SlotTerpesan
from models.pemesanan import Pemesanan
from services.gedung import GedungOlahraga
from database.models import Base, LapanganDB, PemesananDB
from services.api_client import get_kurs, harga_dalam_mata_uang
from services.laporan import (
    slot_tersedia_diurutkan,
    total_pendapatan_per_jenis,
    pemesanan_diurutkan_waktu,
    ringkasan_pemesanan,
)


# ============================================================================
#  FIXTURES
# ============================================================================

@pytest.fixture
def futsal() -> LapanganFutsal:
    """Objek LapanganFutsal untuk test."""
    return LapanganFutsal("F1", 100_000, "25x15 meter")


@pytest.fixture
def badminton() -> LapanganBadminton:
    """Objek LapanganBadminton untuk test."""
    return LapanganBadminton("B1", 60_000, 1)


@pytest.fixture
def slot_baru() -> Slot:
    """Slot baru yang belum dipesan."""
    return Slot("F1-20250601-0800", "08:00", "10:00")


@pytest.fixture
def gedung(futsal: LapanganFutsal, badminton: LapanganBadminton) -> GedungOlahraga:
    """GedungOlahraga dengan lapangan dan slot siap pakai."""
    g = GedungOlahraga()
    g.tambah_lapangan(futsal)
    g.tambah_lapangan(badminton)
    g.tambah_slot("F1", Slot("F1-20250601-0800", "08:00", "10:00"))
    g.tambah_slot("F1", Slot("F1-20250601-1000", "10:00", "12:00"))
    g.tambah_slot("B1", Slot("B1-20250601-0800", "08:00", "09:00"))
    return g


@pytest.fixture
def db():
    """
    Fixture database SQLite in-memory untuk satu test.

    Database hanya hidup selama satu test lalu hilang otomatis.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# ============================================================================
#  TEST UTS — LAPANGAN
# ============================================================================

def test_harga_negatif_raise_error() -> None:
    """Harga negatif saat membuat lapangan harus raise ValueError."""
    with pytest.raises(ValueError):
        LapanganFutsal("F1", -1000, "25x15 meter")


def test_harga_setter_negatif_raise_error(futsal: LapanganFutsal) -> None:
    """Mengubah harga ke negatif via setter harus raise ValueError."""
    with pytest.raises(ValueError):
        futsal.harga_per_jam = -500


def test_hitung_biaya_benar(futsal: LapanganFutsal) -> None:
    """hitung_biaya(2) harus return harga_per_jam * 2."""
    assert futsal.hitung_biaya(2) == 200_000


def test_hitung_biaya_nol(futsal: LapanganFutsal) -> None:
    """hitung_biaya(0) harus return 0."""
    assert futsal.hitung_biaya(0) == 0.0


def test_futsal_adalah_lapangan(futsal: LapanganFutsal) -> None:
    """LapanganFutsal harus merupakan instance dari Lapangan."""
    assert isinstance(futsal, Lapangan)


def test_badminton_adalah_lapangan(badminton: LapanganBadminton) -> None:
    """LapanganBadminton harus merupakan instance dari Lapangan."""
    assert isinstance(badminton, Lapangan)


def test_jenis_futsal(futsal: LapanganFutsal) -> None:
    """jenis() LapanganFutsal harus return 'Futsal'."""
    assert futsal.jenis() == "Futsal"


def test_jenis_badminton(badminton: LapanganBadminton) -> None:
    """jenis() LapanganBadminton harus return 'Badminton'."""
    assert badminton.jenis() == "Badminton"


def test_lapangan_abstract_tidak_bisa_diinstansiasi() -> None:
    """Lapangan abstract tidak boleh bisa di-instansiasi langsung."""
    with pytest.raises(TypeError):
        Lapangan("X1", 50_000)  # type: ignore


# ============================================================================
#  TEST UTS — SLOT & STATUS
# ============================================================================

def test_slot_tersedia_bisa_dipesan() -> None:
    """SlotTersedia.bisa_dipesan() harus return True."""
    assert SlotTersedia().bisa_dipesan() is True


def test_slot_terpesan_tidak_bisa() -> None:
    """SlotTerpesan.bisa_dipesan() harus return False."""
    assert SlotTerpesan("Budi").bisa_dipesan() is False


def test_slot_baru_default_tersedia(slot_baru: Slot) -> None:
    """Slot baru harus berstatus SlotTersedia secara default."""
    assert isinstance(slot_baru.status, SlotTersedia)


def test_slot_setelah_dipesan_berubah_status(slot_baru: Slot) -> None:
    """Setelah dipesan, status slot harus menjadi SlotTerpesan."""
    slot_baru.pesan("Andi")
    assert isinstance(slot_baru.status, SlotTerpesan)


def test_slot_pesan_duplikat_raise_error(slot_baru: Slot) -> None:
    """Memesan slot yang sudah dipesan harus raise SlotSudahDipesanError."""
    slot_baru.pesan("Andi")
    with pytest.raises(SlotSudahDipesanError):
        slot_baru.pesan("Budi")


def test_slot_tidak_valid_raise_error() -> None:
    """Jam selesai <= jam mulai harus raise SlotTidakValidError."""
    with pytest.raises(SlotTidakValidError):
        Slot("F1-20250601-1000", "10:00", "08:00")


def test_slot_jam_sama_raise_error() -> None:
    """Jam mulai == jam selesai harus raise SlotTidakValidError."""
    with pytest.raises(SlotTidakValidError):
        Slot("F1-20250601-0800", "08:00", "08:00")


# ============================================================================
#  TEST UTS — GEDUNG OLAHRAGA
# ============================================================================

def test_cari_lapangan_ada(gedung: GedungOlahraga) -> None:
    """Mencari lapangan yang ada harus return objek Lapangan."""
    assert gedung.cari_lapangan("F1").nomor == "F1"


def test_cari_lapangan_tidak_ada_raise_error(gedung: GedungOlahraga) -> None:
    """Mencari lapangan tidak ada harus raise LapanganTidakDitemukanError."""
    with pytest.raises(LapanganTidakDitemukanError):
        gedung.cari_lapangan("Z9")


def test_slot_tersedia_semua_kosong(gedung: GedungOlahraga) -> None:
    """Semua slot awal harus tersedia."""
    assert len(gedung.slot_tersedia("F1")) == 2


def test_slot_tersedia_berkurang_setelah_pesan(gedung: GedungOlahraga) -> None:
    """Jumlah slot tersedia harus berkurang 1 setelah pemesanan."""
    gedung.pesan("F1", "F1-20250601-0800", "Andi")
    assert len(gedung.slot_tersedia("F1")) == 1


def test_pesan_berhasil_buat_pemesanan(gedung: GedungOlahraga) -> None:
    """pesan() harus mengembalikan Pemesanan yang valid."""
    p = gedung.pesan("F1", "F1-20250601-0800", "Rina")
    assert isinstance(p, Pemesanan)
    assert p.nama_pemesan == "Rina"
    assert p.total_biaya == 200_000  # 2 jam * 100.000


def test_pesan_slot_tidak_ada_raise_error(gedung: GedungOlahraga) -> None:
    """Memesan slot tidak ada harus raise PemesananTidakDitemukanError."""
    with pytest.raises(PemesananTidakDitemukanError):
        gedung.pesan("F1", "F1-99999999-0000", "Andi")


def test_pesan_double_booking_raise_error(gedung: GedungOlahraga) -> None:
    """Double booking harus raise SlotSudahDipesanError."""
    gedung.pesan("F1", "F1-20250601-0800", "Andi")
    with pytest.raises(SlotSudahDipesanError):
        gedung.pesan("F1", "F1-20250601-0800", "Budi")


def test_tambah_slot_lapangan_tidak_ada_raise_error(gedung: GedungOlahraga) -> None:
    """Tambah slot ke lapangan tidak ada harus raise LapanganTidakDitemukanError."""
    with pytest.raises(LapanganTidakDitemukanError):
        gedung.tambah_slot("Z9", Slot("Z9-20250601-0800", "08:00", "09:00"))


# ============================================================================
#  TEST UAS LAYER 1 — SQLAlchemy In-Memory
# ============================================================================

def test_simpan_lapangan_ke_db(db: Session) -> None:
    """
    Simpan LapanganDB ke session, query kembali.
    Assert: hasil tidak None, harga_per_jam benar, jenis sesuai.
    """
    lap = LapanganDB(nomor="F1", jenis="Futsal", harga_per_jam=100_000.0)
    db.add(lap)
    db.commit()

    hasil = db.query(LapanganDB).filter_by(nomor="F1").first()
    assert hasil is not None
    assert hasil.harga_per_jam == 100_000.0
    assert hasil.jenis == "Futsal"


def test_update_harga_lapangan(db: Session) -> None:
    """
    Simpan lapangan, ubah harga_per_jam, commit.
    Assert: query ulang → harga_per_jam sesuai nilai baru.
    """
    lap = LapanganDB(nomor="B1", jenis="Badminton", harga_per_jam=60_000.0)
    db.add(lap)
    db.commit()

    lap.harga_per_jam = 75_000.0
    db.commit()

    hasil = db.query(LapanganDB).filter_by(nomor="B1").first()
    assert hasil.harga_per_jam == 75_000.0


def test_relasi_lapangan_pemesanan(db: Session) -> None:
    """
    Simpan LapanganDB + PemesananDB dengan lapangan_id yang sesuai.
    Assert: lapangan.pemesanan_list memiliki 1 item dengan nama_pemesan benar.
    """
    lap = LapanganDB(nomor="F2", jenis="Futsal", harga_per_jam=100_000.0)
    db.add(lap)
    db.commit()

    pes = PemesananDB(
        lapangan_id=lap.id,
        nama_pemesan="Andi",
        jam_mulai="08:00",
        jam_selesai="10:00",
        total_biaya=200_000.0,
        waktu_pesan="2025-06-01 08:00",
    )
    db.add(pes)
    db.commit()

    db.refresh(lap)
    assert len(lap.pemesanan_list) == 1
    assert lap.pemesanan_list[0].nama_pemesan == "Andi"


# ============================================================================
#  TEST UAS LAYER 2 — REST API (mock, tanpa koneksi internet)
# ============================================================================

def test_get_kurs_berhasil() -> None:
    """
    Mock requests.get agar return respons palsu dengan rates USD.
    Assert: get_kurs('USD') == 0.000064.
    """
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rates": {"USD": 0.000064}}
    mock_resp.raise_for_status.return_value = None

    with patch("services.api_client.requests.get", return_value=mock_resp):
        hasil = get_kurs("USD")
        assert hasil == 0.000064


def test_get_kurs_timeout() -> None:
    """
    Mock requests.get agar raise Timeout.
    Assert: get_kurs() raise ConnectionError.
    """
    with patch("services.api_client.requests.get",
               side_effect=requests.exceptions.Timeout):
        with pytest.raises(ConnectionError):
            get_kurs("USD")


def test_get_kurs_http_error() -> None:
    """
    Mock requests.get agar raise HTTPError (422 mata uang tidak valid).
    Assert: get_kurs() raise ValueError.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 422
    http_error = requests.exceptions.HTTPError(response=mock_resp)

    with patch("services.api_client.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = http_error
        with pytest.raises(ValueError):
            get_kurs("XYZ")


# ============================================================================
#  TEST UAS LAYER 2 — Functional Programming Pipeline
# ============================================================================

def test_slot_tersedia_hanya_yang_bisa_dipesan() -> None:
    """
    Buat 3 slot, 1 sudah dipesan.
    Assert: slot_tersedia_diurutkan() hanya return 2 slot yang masih tersedia.
    """
    s1 = Slot("F1-20250601-0800", "08:00", "09:00")
    s2 = Slot("F1-20250601-0900", "09:00", "10:00")
    s3 = Slot("F1-20250601-1000", "10:00", "11:00")
    s1.pesan("Andi")  # s1 terpesan

    hasil = slot_tersedia_diurutkan([s1, s2, s3])
    assert len(hasil) == 2
    assert all(s.status.bisa_dipesan() for s in hasil)


def test_slot_tersedia_diurutkan_jam() -> None:
    """
    Buat 2 slot tersedia dengan jam berbeda.
    Assert: urutan slot_tersedia_diurutkan() dari jam paling pagi.
    """
    s1 = Slot("F1-20250601-1000", "10:00", "11:00")  # lebih siang
    s2 = Slot("F1-20250601-0800", "08:00", "09:00")  # lebih pagi

    hasil = slot_tersedia_diurutkan([s1, s2])
    assert hasil[0].jam_mulai == "08:00"
    assert hasil[1].jam_mulai == "10:00"


def test_total_pendapatan_per_jenis(gedung: GedungOlahraga) -> None:
    """
    Setelah 2 pemesanan futsal + 1 badminton, total pendapatan harus benar.
    """
    gedung.pesan("F1", "F1-20250601-0800", "Andi")   # 2 jam × 100.000 = 200.000
    gedung.pesan("F1", "F1-20250601-1000", "Budi")   # 2 jam × 100.000 = 200.000
    gedung.pesan("B1", "B1-20250601-0800", "Cici")   # 1 jam ×  60.000 =  60.000

    hasil = total_pendapatan_per_jenis(gedung._riwayat_pemesanan)
    assert hasil.get("Futsal") == 400_000.0
    assert hasil.get("Badminton") == 60_000.0


def test_ringkasan_pemesanan_format(gedung: GedungOlahraga) -> None:
    """
    ringkasan_pemesanan() harus return list string dengan format yang benar.
    """
    gedung.pesan("F1", "F1-20250601-0800", "Andi")
    hasil = ringkasan_pemesanan(gedung._riwayat_pemesanan)

    assert len(hasil) == 1
    assert "Andi" in hasil[0]
    assert "Futsal" in hasil[0]
    assert "F1" in hasil[0]
    assert "Rp" in hasil[0]