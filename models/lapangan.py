""" Modul berisi hierarki class lapangan olahraga.

Class:
    Lapangan        — Abstract base class untuk semua jenis lapangan.
    LapanganFutsal  — Subclass lapangan futsal dengan atribut ukuran.
    LapanganBadminton — Subclass lapangan badminton dengan atribut jumlah_net.
"""

from abc import ABC, abstractmethod


class Lapangan(ABC):
    """Abstract base class untuk semua jenis lapangan olahraga."""

    def __init__(self, nomor: str, harga_per_jam: float) -> None:
        """
        Inisialisasi lapangan.

        Args:
            nomor: Kode unik lapangan, misal 'F1', 'B2'.
            harga_per_jam: Harga sewa per jam dalam rupiah.
        """
        self.nomor = nomor
        self._harga_per_jam: float = 0.0
        self.harga_per_jam = harga_per_jam  # lewat setter agar tervalidasi

    @property
    def harga_per_jam(self) -> float:
        """Getter harga sewa per jam."""
        return self._harga_per_jam

    @harga_per_jam.setter
    def harga_per_jam(self, nilai: float) -> None:
        """
        Setter harga per jam dengan validasi.

        Args:
            nilai: Harga baru per jam.

        Raises:
            ValueError: Jika harga bernilai negatif.
        """
        if nilai < 0:
            raise ValueError("Harga per jam tidak boleh negatif.")
        self._harga_per_jam = nilai

    def hitung_biaya(self, durasi_jam: float) -> float:
        """
        Hitung total biaya sewa berdasarkan durasi.

        Args:
            durasi_jam: Lama sewa dalam jam.

        Returns:
            Total biaya sewa (rupiah).
        """
        return self._harga_per_jam * durasi_jam

    @abstractmethod
    def jenis(self) -> str:
        """Return string jenis lapangan, misal 'Futsal' atau 'Badminton'."""
        pass

    def __str__(self) -> str:
        """Representasi string lapangan."""
        return (
            f"Lapangan {self.jenis()} {self.nomor} | "
            f"Rp{self.harga_per_jam:,.0f}/jam"
        )


class LapanganFutsal(Lapangan):
    """Subclass lapangan futsal dengan informasi ukuran lapangan."""

    def __init__(self, nomor: str, harga_per_jam: float, ukuran: str) -> None:
        """
        Inisialisasi lapangan futsal.

        Args:
            nomor: Kode lapangan, misal 'F1'.
            harga_per_jam: Harga sewa per jam.
            ukuran: Ukuran lapangan, misal '25x15 meter'.
        """
        super().__init__(nomor, harga_per_jam)
        self.ukuran = ukuran

    def jenis(self) -> str:
        """Return jenis lapangan."""
        return "Futsal"

    def __str__(self) -> str:
        """Representasi string lapangan futsal beserta ukuran."""
        return (
            f"Lapangan Futsal {self.nomor} | "
            f"Rp{self.harga_per_jam:,.0f}/jam | {self.ukuran}"
        )


class LapanganBadminton(Lapangan):
    """Subclass lapangan badminton dengan informasi jumlah net."""

    def __init__(self, nomor: str, harga_per_jam: float, jumlah_net: int) -> None:
        """
        Inisialisasi lapangan badminton.

        Args:
            nomor: Kode lapangan, misal 'B1'.
            harga_per_jam: Harga sewa per jam.
            jumlah_net: Jumlah net yang tersedia.
        """
        super().__init__(nomor, harga_per_jam)
        self.jumlah_net = jumlah_net

    def jenis(self) -> str:
        """Return jenis lapangan."""
        return "Badminton"

    def __str__(self) -> str:
        """Representasi string lapangan badminton beserta jumlah net."""
        return (
            f"Lapangan Badminton {self.nomor} | "
            f"Rp{self.harga_per_jam:,.0f}/jam | {self.jumlah_net} net"
        )