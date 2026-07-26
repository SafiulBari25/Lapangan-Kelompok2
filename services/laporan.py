"""
services/laporan.py — Pipeline laporan menggunakan functional programming.

ATURAN: Semua fungsi di file ini WAJIB menggunakan map, filter, atau sorted.
        Tidak ada loop for atau while di dalam fungsi manapun.

Fungsi:
    slot_tersedia_diurutkan()      — Filter + urutkan slot yang masih tersedia.
    total_pendapatan_per_jenis()   — Hitung total pendapatan per jenis lapangan.
    pemesanan_diurutkan_waktu()    — Urutkan pemesanan berdasarkan waktu.
    ringkasan_pemesanan()          — Map pemesanan ke string ringkasan.
"""

from functools import reduce
from models.slot import Slot
from models.pemesanan import Pemesanan


def slot_tersedia_diurutkan(daftar_slot: list[Slot]) -> list[Slot]:
    """
    Filter slot yang masih bisa dipesan dan urutkan dari jam paling pagi.

    Args:
        daftar_slot: List semua Slot dari semua lapangan.

    Returns:
        List Slot yang bisa_dipesan() == True, diurutkan berdasarkan jam_mulai.
    """
    tersedia = filter(lambda s: s.status.bisa_dipesan(), daftar_slot)
    return sorted(tersedia, key=lambda s: s.jam_mulai)


def total_pendapatan_per_jenis(daftar_pemesanan: list[Pemesanan]) -> dict[str, float]:
    """
    Hitung total pendapatan per jenis lapangan (Futsal / Badminton).

    Args:
        daftar_pemesanan: List Pemesanan dari GedungOlahraga._riwayat_pemesanan.

    Returns:
        Dict dengan kunci jenis lapangan dan nilai total biaya,
        contoh: {'Futsal': 800000.0, 'Badminton': 350000.0}.
    """
    # Kumpulkan semua jenis lapangan yang muncul
    jenis_set: set[str] = set(map(lambda p: p.lapangan.jenis(), daftar_pemesanan))

    # Hitung total per jenis menggunakan filter + reduce
    def total_untuk_jenis(jenis: str) -> float:
        biaya_jenis = filter(
            lambda p: p.lapangan.jenis() == jenis, daftar_pemesanan
        )
        return reduce(lambda acc, p: acc + p.total_biaya, biaya_jenis, 0.0)

    return {jenis: total_untuk_jenis(jenis) for jenis in sorted(jenis_set)}


def pemesanan_diurutkan_waktu(daftar_pemesanan: list[Pemesanan]) -> list[Pemesanan]:
    """
    Urutkan pemesanan berdasarkan waktu_pesan dari terlama ke terbaru.

    Args:
        daftar_pemesanan: List Pemesanan.

    Returns:
        List Pemesanan terurut dari waktu terlama.
    """
    return sorted(daftar_pemesanan, key=lambda p: p.waktu_pesan)


def ringkasan_pemesanan(daftar_pemesanan: list[Pemesanan]) -> list[str]:
    """
    Map setiap Pemesanan ke string ringkasan yang mudah dibaca.

    Format: "{nama_pemesan} — {jenis} {nomor} — Rp{total_biaya:,}"

    Args:
        daftar_pemesanan: List Pemesanan.

    Returns:
        List string ringkasan.
    """
    return list(map(
        lambda p: (
            f"{p.nama_pemesan} — "
            f"{p.lapangan.jenis()} {p.lapangan.nomor} — "
            f"Rp{p.total_biaya:,.0f}"
        ),
        daftar_pemesanan,
    ))