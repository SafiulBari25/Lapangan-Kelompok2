"""
tests/test_gedung.py — Unit test untuk sistem penyewaan lapangan olahraga.

Jalankan dengan: pytest tests/ -v
"""

import pytest
import sys
import os

# Pastikan root package bisa diimport dari folder tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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


# ------------------------------------------------------------------ #
#  FIXTURES
# ------------------------------------------------------------------ #

@pytest.fixture
def futsal() -> LapanganFutsal:
    """Buat objek LapanganFutsal untuk keperluan test."""
    return LapanganFutsal("F1", 100_000, "25x15 meter")


@pytest.fixture
def badminton() -> LapanganBadminton:
    """Buat objek LapanganBadminton untuk keperluan test."""
    return LapanganBadminton("B1", 60_000, 1)


@pytest.fixture
def slot_baru() -> Slot:
    """Buat objek Slot baru yang belum dipesan."""
    return Slot("F1-20250601-0800", "08:00", "10:00")


@pytest.fixture
def gedung(futsal: LapanganFutsal, badminton: LapanganBadminton) -> GedungOlahraga:
    """Buat GedungOlahraga dengan 2 lapangan dan beberapa slot."""
    g = GedungOlahraga()
    g.tambah_lapangan(futsal)
    g.tambah_lapangan(badminton)
    g.tambah_slot("F1", Slot("F1-20250601-0800", "08:00", "10:00"))
    g.tambah_slot("F1", Slot("F1-20250601-1000", "10:00", "12:00"))
    g.tambah_slot("B1", Slot("B1-20250601-0800", "08:00", "09:00"))
    return g


# ------------------------------------------------------------------ #
#  TEST — LAPANGAN
# ------------------------------------------------------------------ #

def test_harga_negatif_raise_error() -> None:
    """Harga negatif saat membuat lapangan harus raise ValueError."""
    with pytest.raises(ValueError):
        LapanganFutsal("F1", -1000, "25x15 meter")


def test_harga_setter_negatif_raise_error(futsal: LapanganFutsal) -> None:
    """Mengubah harga ke nilai negatif via setter harus raise ValueError."""
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
    """Lapangan (abstract) tidak boleh bisa di-instansiasi langsung."""
    with pytest.raises(TypeError):
        Lapangan("X1", 50_000)  # type: ignore


# ------------------------------------------------------------------ #
#  TEST — SLOT & STATUS
# ------------------------------------------------------------------ #

def test_slot_tersedia_bisa_dipesan() -> None:
    """SlotTersedia.bisa_dipesan() harus return True."""
    assert SlotTersedia().bisa_dipesan() is True


def test_slot_terpesan_tidak_bisa() -> None:
    """SlotTerpesan.bisa_dipesan() harus return False."""
    assert SlotTerpesan("Budi").bisa_dipesan() is False


def test_slot_baru_default_tersedia(slot_baru: Slot) -> None:
    """Slot baru harus berstatus SlotTersedia secara default."""
    assert isinstance(slot_baru.status, SlotTersedia)
    assert slot_baru.status.bisa_dipesan() is True


def test_slot_setelah_dipesan_berubah_status(slot_baru: Slot) -> None:
    """Setelah dipesan, status slot harus berubah menjadi SlotTerpesan."""
    slot_baru.pesan("Andi")
    assert isinstance(slot_baru.status, SlotTerpesan)
    assert slot_baru.status.bisa_dipesan() is False


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


# ------------------------------------------------------------------ #
#  TEST — GEDUNG OLAHRAGA
# ------------------------------------------------------------------ #

def test_cari_lapangan_ada(gedung: GedungOlahraga) -> None:
    """Mencari lapangan yang ada harus return objek Lapangan."""
    lap = gedung.cari_lapangan("F1")
    assert lap.nomor == "F1"


def test_cari_lapangan_tidak_ada_raise_error(gedung: GedungOlahraga) -> None:
    """Mencari lapangan yang tidak ada harus raise LapanganTidakDitemukanError."""
    with pytest.raises(LapanganTidakDitemukanError):
        gedung.cari_lapangan("Z9")


def test_slot_tersedia_semua_kosong(gedung: GedungOlahraga) -> None:
    """Semua slot awal harus tersedia (belum ada yang dipesan)."""
    tersedia = gedung.slot_tersedia("F1")
    assert len(tersedia) == 2


def test_slot_tersedia_berkurang_setelah_pesan(gedung: GedungOlahraga) -> None:
    """Jumlah slot tersedia harus berkurang 1 setelah pemesanan."""
    gedung.pesan("F1", "F1-20250601-0800", "Andi")
    tersedia = gedung.slot_tersedia("F1")
    assert len(tersedia) == 1


def test_pesan_berhasil_buat_pemesanan(gedung: GedungOlahraga) -> None:
    """pesan() harus mengembalikan objek Pemesanan yang valid."""
    p = gedung.pesan("F1", "F1-20250601-0800", "Rina")
    assert isinstance(p, Pemesanan)
    assert p.nama_pemesan == "Rina"
    assert p.total_biaya == 200_000  # 2 jam * 100.000


def test_pesan_slot_tidak_ada_raise_error(gedung: GedungOlahraga) -> None:
    """Memesan slot dengan ID yang tidak ada harus raise PemesananTidakDitemukanError."""
    with pytest.raises(PemesananTidakDitemukanError):
        gedung.pesan("F1", "F1-99999999-0000", "Andi")


def test_pesan_double_booking_raise_error(gedung: GedungOlahraga) -> None:
    """Double booking pada slot yang sama harus raise SlotSudahDipesanError."""
    gedung.pesan("F1", "F1-20250601-0800", "Andi")
    with pytest.raises(SlotSudahDipesanError):
        gedung.pesan("F1", "F1-20250601-0800", "Budi")


def test_tambah_slot_lapangan_tidak_ada_raise_error(gedung: GedungOlahraga) -> None:
    """Menambah slot ke lapangan yang tidak ada harus raise LapanganTidakDitemukanError."""
    with pytest.raises(LapanganTidakDitemukanError):
        gedung.tambah_slot("Z9", Slot("Z9-20250601-0800", "08:00", "09:00"))