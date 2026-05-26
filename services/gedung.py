""" Modul berisi class controller utama sistem penyewaan lapangan olahraga.

Class:
    GedungOlahraga — Mengelola seluruh lapangan, slot, dan pemesanan.
"""

from datetime import datetime
from models.lapangan import Lapangan
from models.slot import Slot
from models.pemesanan import Pemesanan
from exceptions.custom_exceptions import (
    LapanganTidakDitemukanError,
    SlotTidakValidError,
    PemesananTidakDitemukanError,
)


class GedungOlahraga:
    """
    Controller utama yang mengelola seluruh sistem penyewaan lapangan.

    Mengelola lapangan, slot waktu, dan riwayat pemesanan.
    """

    def __init__(self) -> None:
        """Inisialisasi gedung dengan daftar kosong."""
        self._daftar_lapangan: list[Lapangan] = []
        self._daftar_slot: dict[str, list[Slot]] = {}
        self._riwayat_pemesanan: list[Pemesanan] = []
        self._counter_pemesanan: int = 0

    # ------------------------------------------------------------------ #
    #  MANAJEMEN LAPANGAN
    # ------------------------------------------------------------------ #

    def tambah_lapangan(self, lapangan: Lapangan) -> None:
        """
        Tambah lapangan baru ke sistem.

        Args:
            lapangan: Objek lapangan yang akan ditambahkan.
        """
        self._daftar_lapangan.append(lapangan)
        if lapangan.nomor not in self._daftar_slot:
            self._daftar_slot[lapangan.nomor] = []

    def cari_lapangan(self, nomor: str) -> Lapangan:
        """
        Cari lapangan berdasarkan nomor/kode.

        Args:
            nomor: Kode lapangan yang dicari.

        Returns:
            Objek Lapangan yang ditemukan.

        Raises:
            LapanganTidakDitemukanError: Jika lapangan tidak ditemukan.
        """
        for lap in self._daftar_lapangan:
            if lap.nomor == nomor:
                return lap
        raise LapanganTidakDitemukanError(
            f"Lapangan dengan nomor '{nomor}' tidak ditemukan."
        )

    def tampilkan_lapangan(self) -> None:
        """Tampilkan semua lapangan beserta harga sewa per jam."""
        if not self._daftar_lapangan:
            print("Belum ada lapangan yang terdaftar.")
            return
        print("\n--- DAFTAR LAPANGAN ---")
        for lap in self._daftar_lapangan:
            print(f"  {lap}")
        print()

    # ------------------------------------------------------------------ #
    #  MANAJEMEN SLOT
    # ------------------------------------------------------------------ #

    def tambah_slot(self, nomor_lapangan: str, slot: Slot) -> None:
        """
        Tambah slot waktu untuk lapangan tertentu.

        Args:
            nomor_lapangan: Kode lapangan tujuan.
            slot: Objek Slot yang akan ditambahkan.

        Raises:
            LapanganTidakDitemukanError: Jika lapangan tidak ditemukan.
        """
        self.cari_lapangan(nomor_lapangan)  # validasi lapangan ada
        if nomor_lapangan not in self._daftar_slot:
            self._daftar_slot[nomor_lapangan] = []
        self._daftar_slot[nomor_lapangan].append(slot)

    def slot_tersedia(self, nomor_lapangan: str) -> list[Slot]:
        """
        Return daftar slot yang masih bisa dipesan pada lapangan tertentu.

        Args:
            nomor_lapangan: Kode lapangan.

        Returns:
            List Slot yang bisa_dipesan() == True.

        Raises:
            LapanganTidakDitemukanError: Jika lapangan tidak ditemukan.
        """
        self.cari_lapangan(nomor_lapangan)
        semua = self._daftar_slot.get(nomor_lapangan, [])
        return [s for s in semua if s.status.bisa_dipesan()]

    def tampilkan_slot_kosong(self, nomor_lapangan: str) -> None:
        """
        Tampilkan semua slot kosong untuk lapangan tertentu.

        Args:
            nomor_lapangan: Kode lapangan.
        """
        tersedia = self.slot_tersedia(nomor_lapangan)
        if not tersedia:
            print(f"Tidak ada slot tersedia untuk lapangan {nomor_lapangan}.")
            return
        print(f"\n--- SLOT TERSEDIA — Lapangan {nomor_lapangan} ---")
        for s in tersedia:
            print(f"  {s}")
        print()

    # ------------------------------------------------------------------ #
    #  PEMESANAN
    # ------------------------------------------------------------------ #

    def pesan(self, nomor_lapangan: str, id_slot: str, nama: str) -> Pemesanan:
        """
        Lakukan pemesanan slot pada lapangan tertentu.

        Args:
            nomor_lapangan: Kode lapangan yang akan dipesan.
            id_slot: ID slot yang akan dipesan.
            nama: Nama pemesan.

        Returns:
            Objek Pemesanan yang berhasil dibuat.

        Raises:
            LapanganTidakDitemukanError: Jika lapangan tidak ditemukan.
            PemesananTidakDitemukanError: Jika slot tidak ditemukan.
            SlotSudahDipesanError: Jika slot sudah dipesan.
        """
        lapangan = self.cari_lapangan(nomor_lapangan)

        # Cari slot di lapangan tersebut
        daftar = self._daftar_slot.get(nomor_lapangan, [])
        slot_target: Slot | None = None
        for s in daftar:
            if s.id_slot == id_slot:
                slot_target = s
                break

        if slot_target is None:
            raise PemesananTidakDitemukanError(
                f"Slot '{id_slot}' tidak ditemukan di lapangan {nomor_lapangan}."
            )

        # Ini akan raise SlotSudahDipesanError jika sudah dipesan
        slot_target.pesan(nama)

        # Hitung biaya
        jam_mulai_h = int(slot_target.jam_mulai.split(":")[0])
        jam_selesai_h = int(slot_target.jam_selesai.split(":")[0])
        durasi = jam_selesai_h - jam_mulai_h
        total_biaya = lapangan.hitung_biaya(durasi)

        # Buat rekaman pemesanan
        self._counter_pemesanan += 1
        id_pemesanan = f"PES-{self._counter_pemesanan:03d}"
        waktu_pesan = datetime.now().strftime("%Y-%m-%d %H:%M")

        pemesanan = Pemesanan(
            id_pemesanan=id_pemesanan,
            lapangan=lapangan,
            slot=slot_target,
            nama_pemesan=nama,
            total_biaya=total_biaya,
            waktu_pesan=waktu_pesan,
        )
        self._riwayat_pemesanan.append(pemesanan)
        return pemesanan

    # ------------------------------------------------------------------ #
    #  REKAP
    # ------------------------------------------------------------------ #

    def tampilkan_riwayat(self) -> None:
        """Tampilkan semua riwayat pemesanan."""
        if not self._riwayat_pemesanan:
            print("Belum ada pemesanan.")
            return
        print("\n--- RIWAYAT PEMESANAN ---")
        for p in self._riwayat_pemesanan:
            print(f"  {p}")
        print()

    def rekap_harian(self, tanggal: str) -> None:
        """
        Tampilkan semua pemesanan pada tanggal tertentu.

        Args:
            tanggal: Tanggal dalam format 'YYYY-MM-DD'.
        """
        hasil = [
            p for p in self._riwayat_pemesanan if tanggal in p.slot.id_slot
        ]
        if not hasil:
            print(f"Tidak ada pemesanan pada tanggal {tanggal}.")
            return
        print(f"\n--- REKAP PEMESANAN — {tanggal} ---")
        for p in hasil:
            print(f"  {p}")
        print()

    def rekap_slot_tersisa(self) -> None:
        """Tampilkan semua lapangan beserta jumlah slot yang masih tersedia."""
        print("\n--- REKAP SLOT TERSISA PER LAPANGAN ---")
        for lap in self._daftar_lapangan:
            tersedia = len(self.slot_tersedia(lap.nomor))
            total = len(self._daftar_slot.get(lap.nomor, []))
            print(f"  {lap.nomor} ({lap.jenis()}) — {tersedia}/{total} slot tersedia")
        print()