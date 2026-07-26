"""
main.py — Antarmuka CLI Sistem Penyewaan Lapangan Olahraga Mas Eko.

Pengembangan UAS:
  - Layer 1: Data persisten menggunakan SQLAlchemy (SQLite).
  - Layer 2: Konversi kurs via REST API + laporan functional programming.

Jalankan : python main.py
Test      : pytest tests/ -v
"""

from datetime import date

# ── UTS (tidak berubah) ─────────────────────────────────────────────────────
from exceptions.custom_exceptions import (
    LapanganTidakDitemukanError,
    SlotSudahDipesanError,
    SlotTidakValidError,
    PemesananTidakDitemukanError,
)
from models.lapangan import LapanganFutsal, LapanganBadminton
from models.slot import Slot
from services.gedung import GedungOlahraga

# ── UAS Layer 1: Database ────────────────────────────────────────────────────
from database.db_handler import (
    init_db,
    simpan_lapangan,
    ambil_semua_lapangan,
    update_harga_lapangan,
    simpan_pemesanan,
    ambil_semua_pemesanan,
)

# ── UAS Layer 2: API & Laporan ───────────────────────────────────────────────
from services.api_client import harga_dalam_mata_uang
from services.laporan import (
    slot_tersedia_diurutkan,
    total_pendapatan_per_jenis,
    pemesanan_diurutkan_waktu,
    ringkasan_pemesanan,
)


# ============================================================================
#  HELPERS
# ============================================================================

def _cari_lapangan_db(nomor: str):
    """Cari LapanganDB berdasarkan nomor. Return None jika tidak ada."""
    for lap in ambil_semua_lapangan():
        if lap.nomor == nomor:
            return lap
    return None


# ============================================================================
#  SUB-MENU
# ============================================================================

def menu_tambah_lapangan(gedung: GedungOlahraga) -> None:
    """Sub-menu tambah lapangan baru (in-memory + database)."""
    print("\n  Jenis: 1) Futsal  2) Badminton")
    try:
        pilihan = input("  Pilih jenis (1/2): ").strip()
        nomor = input("  Nomor lapangan (misal F1, B2): ").strip().upper()
        harga = float(input("  Harga per jam (Rp): "))

        if pilihan == "1":
            ukuran = input("  Ukuran (misal 25x15 meter): ").strip()
            lap = LapanganFutsal(nomor, harga, ukuran)
        elif pilihan == "2":
            jumlah_net = int(input("  Jumlah net: "))
            lap = LapanganBadminton(nomor, harga, jumlah_net)
        else:
            print("  ✘ Pilihan tidak valid.")
            return

        gedung.tambah_lapangan(lap)
        # ── Layer 1: simpan ke database ──────────────────────────────────
        simpan_lapangan(nomor=lap.nomor, jenis=lap.jenis(), harga_per_jam=lap.harga_per_jam)
        print(f"  ✔ Lapangan berhasil ditambahkan: {lap}")

    except ValueError as e:
        print(f"  ✘ Input tidak valid: {e}")


def menu_tampilkan_lapangan(gedung: GedungOlahraga) -> None:
    """Tampilkan semua lapangan + opsi konversi harga ke mata uang asing."""
    gedung.tampilkan_lapangan()
    if not gedung._daftar_lapangan:
        return

    # ── Layer 2: konversi kurs ────────────────────────────────────────────
    mata_uang = input(
        "  Tampilkan harga dalam mata uang asing? "
        "(ketik kode misal USD/SGD, kosongkan untuk skip): "
    ).strip().upper()

    if not mata_uang:
        return

    print()
    for lap in gedung._daftar_lapangan:
        try:
            harga_asing = harga_dalam_mata_uang(lap.harga_per_jam, mata_uang)
            print(f"  {lap} (≈ {harga_asing})")
        except (ConnectionError, ValueError) as e:
            print(f"  {lap}")
            print(f"    ⚠ Konversi gagal: {e}")
    print()


def menu_tambah_slot(gedung: GedungOlahraga) -> None:
    """Sub-menu tambah slot waktu."""
    try:
        nomor = input("  Nomor lapangan: ").strip().upper()
        tanggal = input("  Tanggal (YYYYMMDD, misal 20250601): ").strip()
        jam_mulai = input("  Jam mulai (HH:MM): ").strip()
        jam_selesai = input("  Jam selesai (HH:MM): ").strip()

        id_slot = f"{nomor}-{tanggal}-{jam_mulai.replace(':', '')}"
        slot = Slot(id_slot, jam_mulai, jam_selesai)
        gedung.tambah_slot(nomor, slot)
        print(f"  ✔ Slot ditambahkan: {slot}")

    except LapanganTidakDitemukanError as e:
        print(f"  ✘ {e}")
    except SlotTidakValidError as e:
        print(f"  ✘ {e}")
    except ValueError as e:
        print(f"  ✘ Input tidak valid: {e}")


def menu_pesan(gedung: GedungOlahraga) -> None:
    """Sub-menu pemesanan slot (in-memory + database)."""
    try:
        nomor = input("  Nomor lapangan: ").strip().upper()
        gedung.tampilkan_slot_kosong(nomor)
        id_slot = input("  ID slot yang ingin dipesan: ").strip()
        nama = input("  Nama pemesan: ").strip()
        if not nama:
            print("  ✘ Nama pemesan tidak boleh kosong.")
            return

        pemesanan = gedung.pesan(nomor, id_slot, nama)
        print()
        pemesanan.cetak_bukti()

        # ── Layer 1: simpan pemesanan ke database ─────────────────────────
        lap_db = _cari_lapangan_db(nomor)
        if lap_db:
            simpan_pemesanan(
                lapangan_id=lap_db.id,
                nama_pemesan=pemesanan.nama_pemesan,
                jam_mulai=pemesanan.slot.jam_mulai,
                jam_selesai=pemesanan.slot.jam_selesai,
                total_biaya=pemesanan.total_biaya,
                waktu_pesan=pemesanan.waktu_pesan,
            )

    except LapanganTidakDitemukanError as e:
        print(f"  ✘ {e}")
    except SlotSudahDipesanError as e:
        print(f"  ✘ {e}")
    except PemesananTidakDitemukanError as e:
        print(f"  ✘ {e}")


def menu_update_harga(gedung: GedungOlahraga) -> None:
    """Sub-menu ubah harga sewa lapangan (in-memory + database)."""
    try:
        nomor = input("  Nomor lapangan: ").strip().upper()
        lap = gedung.cari_lapangan(nomor)
        print(f"  Harga saat ini: Rp{lap.harga_per_jam:,.0f}/jam")
        harga_baru = float(input("  Harga baru (Rp): "))
        lap.harga_per_jam = harga_baru  # validasi via @property setter
        # ── Layer 1: update di database ───────────────────────────────────
        update_harga_lapangan(nomor, harga_baru)
        print(f"  ✔ Harga lapangan {nomor} diperbarui: Rp{harga_baru:,.0f}/jam")

    except LapanganTidakDitemukanError as e:
        print(f"  ✘ {e}")
    except ValueError as e:
        print(f"  ✘ {e}")


def menu_tampilkan_dari_db() -> None:
    """Tampilkan data lapangan dan pemesanan langsung dari database (persistensi)."""
    print("\n--- DATA LAPANGAN DARI DATABASE ---")
    lapangan_db = ambil_semua_lapangan()
    if not lapangan_db:
        print("  (kosong)")
    else:
        for lap in lapangan_db:
            print(f"  [{lap.id}] {lap.nomor} | {lap.jenis} | Rp{lap.harga_per_jam:,.0f}/jam")

    print("\n--- RIWAYAT PEMESANAN DARI DATABASE ---")
    pemesanan_db = ambil_semua_pemesanan()
    if not pemesanan_db:
        print("  (kosong)")
    else:
        for p in pemesanan_db:
            print(f"  [{p.id}] lapangan_id={p.lapangan_id} | {p.nama_pemesan} | "
                  f"{p.jam_mulai}–{p.jam_selesai} | Rp{p.total_biaya:,.0f} | {p.waktu_pesan}")
    print()


def menu_laporan(gedung: GedungOlahraga) -> None:
    """Sub-menu laporan menggunakan functional programming pipeline."""
    print("""
  === MENU LAPORAN ===
  [1] Slot tersedia (urut jam paling pagi)
  [2] Pendapatan total per jenis lapangan
  [3] Pemesanan diurutkan berdasarkan waktu
  [4] Ringkasan semua pemesanan
  [0] Kembali
""")
    pilihan = input("  Pilih laporan (0–4): ").strip()

    # Kumpulkan semua slot dari semua lapangan
    semua_slot = [
        s for slots in gedung._daftar_slot.values() for s in slots
    ]

    if pilihan == "1":
        hasil = slot_tersedia_diurutkan(semua_slot)
        print(f"\n  Slot tersedia ({len(hasil)} slot):")
        if hasil:
            for s in hasil:
                print(f"    {s}")
        else:
            print("    (tidak ada slot tersedia)")

    elif pilihan == "2":
        hasil = total_pendapatan_per_jenis(gedung._riwayat_pemesanan)
        print("\n  Total pendapatan per jenis lapangan:")
        if hasil:
            for jenis, total in hasil.items():
                print(f"    {jenis}: Rp{total:,.0f}")
        else:
            print("    (belum ada pemesanan)")

    elif pilihan == "3":
        hasil = pemesanan_diurutkan_waktu(gedung._riwayat_pemesanan)
        print(f"\n  Pemesanan urut waktu ({len(hasil)} pemesanan):")
        if hasil:
            for p in hasil:
                print(f"    {p.waktu_pesan} | {p}")
        else:
            print("    (belum ada pemesanan)")

    elif pilihan == "4":
        hasil = ringkasan_pemesanan(gedung._riwayat_pemesanan)
        print(f"\n  Ringkasan pemesanan ({len(hasil)} entri):")
        if hasil:
            for baris in hasil:
                print(f"    {baris}")
        else:
            print("    (belum ada pemesanan)")

    elif pilihan == "0":
        return
    else:
        print("  ✘ Pilihan tidak valid.")

    print()


# ============================================================================
#  MENU UTAMA
# ============================================================================

def menu_utama(gedung: GedungOlahraga) -> None:
    """
    Fungsi utama CLI yang menangani seluruh pilihan menu.

    Args:
        gedung: Objek GedungOlahraga yang sudah diinisialisasi.
    """
    print("\n" + "=" * 56)
    print("   SISTEM PENYEWAAN LAPANGAN OLAHRAGA — MAS EKO  (UAS)")
    print("=" * 56)

    while True:
        print("""
  ─── MANAJEMEN ──────────────────────────
  [1] Tambah lapangan baru
  [2] Tampilkan semua lapangan + konversi kurs
  [3] Ubah harga sewa lapangan
  [4] Tambah slot waktu
  [5] Lihat slot tersedia
  ─── PEMESANAN ──────────────────────────
  [6] Pesan lapangan
  [7] Rekap pemesanan hari ini
  [8] Rekap slot tersisa per lapangan
  [9] Lihat semua riwayat pemesanan
  ─── DATABASE & LAPORAN ─────────────────
  [10] Tampilkan data dari database (persistensi)
  [11] Menu Laporan (functional programming)
  ─────────────────────────────────────────
  [0]  Keluar
""")
        try:
            pilihan = input("  Pilih menu: ").strip()

            if pilihan == "1":
                menu_tambah_lapangan(gedung)
            elif pilihan == "2":
                menu_tampilkan_lapangan(gedung)
            elif pilihan == "3":
                menu_update_harga(gedung)
            elif pilihan == "4":
                menu_tambah_slot(gedung)
            elif pilihan == "5":
                try:
                    nomor = input("  Nomor lapangan: ").strip().upper()
                    gedung.tampilkan_slot_kosong(nomor)
                except LapanganTidakDitemukanError as e:
                    print(f"  ✘ {e}")
            elif pilihan == "6":
                menu_pesan(gedung)
            elif pilihan == "7":
                hari_ini = date.today().strftime("%Y%m%d")
                gedung.rekap_harian(hari_ini)
            elif pilihan == "8":
                gedung.rekap_slot_tersisa()
            elif pilihan == "9":
                gedung.tampilkan_riwayat()
            elif pilihan == "10":
                menu_tampilkan_dari_db()
            elif pilihan == "11":
                menu_laporan(gedung)
            elif pilihan == "0":
                print("\n  Sampai jumpa! Terima kasih menggunakan sistem ini.\n")
                break
            else:
                print("  ✘ Pilihan tidak valid. Masukkan angka 0–11.")

        except KeyboardInterrupt:
            print("\n\n  Program dihentikan.")
            break


# ============================================================================
#  DATA AWAL (seed)
# ============================================================================

def _isi_data_awal(gedung: GedungOlahraga) -> None:
    """Isi lapangan dan slot demo agar langsung bisa dicoba."""
    lapangan_list = [
        LapanganFutsal("F1", 100_000, "25x15 meter"),
        LapanganFutsal("F2", 100_000, "25x15 meter"),
        LapanganBadminton("B1", 60_000, 1),
        LapanganBadminton("B2", 60_000, 1),
    ]
    hari_ini = date.today().strftime("%Y%m%d")

    for lap in lapangan_list:
        gedung.tambah_lapangan(lap)
        # Cek apakah sudah ada di DB (hindari duplikat saat program dibuka ulang)
        if _cari_lapangan_db(lap.nomor) is None:
            simpan_lapangan(lap.nomor, lap.jenis(), lap.harga_per_jam)

    slot_futsal = [("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"),
                   ("19:00", "20:00"), ("20:00", "21:00"), ("21:00", "22:00")]
    slot_badminton = [("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"),
                      ("16:00", "17:00"), ("17:00", "18:00"), ("18:00", "19:00")]

    for nomor in ["F1", "F2"]:
        for jm, js in slot_futsal:
            gedung.tambah_slot(nomor, Slot(f"{nomor}-{hari_ini}-{jm.replace(':','')}", jm, js))

    for nomor in ["B1", "B2"]:
        for jm, js in slot_badminton:
            gedung.tambah_slot(nomor, Slot(f"{nomor}-{hari_ini}-{jm.replace(':','')}", jm, js))


# ============================================================================
#  ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    init_db()          # ← Layer 1: buat tabel jika belum ada, buat gedung.db
    gedung = GedungOlahraga()
    _isi_data_awal(gedung)
    menu_utama(gedung)