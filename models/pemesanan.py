""" Modul berisi class rekaman pemesanan yang berhasil.

Class:
    Pemesanan — Menyimpan data lengkap satu pemesanan yang berhasil dilakukan.
"""

from models.lapangan import Lapangan
from models.slot import Slot


class Pemesanan:
    """Rekaman lengkap satu pemesanan lapangan yang berhasil."""

    def __init__(
        self,
        id_pemesanan: str,
        lapangan: Lapangan,
        slot: Slot,
        nama_pemesan: str,
        total_biaya: float,
        waktu_pesan: str,
    ) -> None:
        """
        Inisialisasi data pemesanan.

        Args:
            id_pemesanan: ID unik pemesanan, misal 'PES-001'.
            lapangan: Objek lapangan yang dipesan.
            slot: Objek slot waktu yang dipesan.
            nama_pemesan: Nama pemesan.
            total_biaya: Total biaya yang harus dibayar (rupiah).
            waktu_pesan: Waktu saat pemesanan dibuat, misal '2025-06-01 08:30'.
        """
        self.id_pemesanan = id_pemesanan
        self.lapangan = lapangan
        self.slot = slot
        self.nama_pemesan = nama_pemesan
        self.total_biaya = total_biaya
        self.waktu_pesan = waktu_pesan

    def cetak_bukti(self) -> None:
        """Tampilkan detail pemesanan sebagai bukti reservasi."""
        print("=" * 50)
        print("        BUKTI PEMESANAN LAPANGAN")
        print("=" * 50)
        print(f"ID Pemesanan  : {self.id_pemesanan}")
        print(f"Lapangan      : {self.lapangan}")
        print(f"Slot Waktu    : {self.slot.jam_mulai} – {self.slot.jam_selesai}")
        print(f"Nama Pemesan  : {self.nama_pemesan}")
        print(f"Total Biaya   : Rp{self.total_biaya:,.0f}")
        print(f"Waktu Pesan   : {self.waktu_pesan}")
        print("=" * 50)

    def __str__(self) -> str:
        """Representasi ringkas pemesanan."""
        return (
            f"{self.id_pemesanan} | {self.lapangan.nomor} | "
            f"{self.slot.jam_mulai}–{self.slot.jam_selesai} | "
            f"{self.nama_pemesan} | Rp{self.total_biaya:,.0f}"
        )