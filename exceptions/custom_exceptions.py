"""
Modul berisi semua custom exception untuk sistem penyewaan lapangan olahraga.
"""


class SlotSudahDipesanError(Exception):
    """Dipicu saat slot yang dipilih sudah dipesan orang lain."""
    pass


class LapanganTidakDitemukanError(Exception):
    """Dipicu saat kode lapangan tidak ditemukan di sistem."""
    pass


class SlotTidakValidError(Exception):
    """Dipicu saat jam selesai tidak lebih besar dari jam mulai."""
    pass


class PemesananTidakDitemukanError(Exception):
    """Dipicu saat ID pemesanan tidak ditemukan di sistem."""
    pass
