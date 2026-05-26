""" Modul berisi hierarki status slot dan class Slot.

Class:
    StatusSlot    — Abstract class, kontrak semua status slot.
    SlotTersedia  — Status slot yang belum dipesan.
    SlotTerpesan  — Status slot yang sudah dipesan.
    Slot          — Entitas satu unit waktu sewa.
"""

from abc import ABC, abstractmethod
from exceptions.custom_exceptions import SlotSudahDipesanError, SlotTidakValidError


class StatusSlot(ABC):
    """Abstract class yang menjadi kontrak semua status slot."""

    @abstractmethod
    def keterangan(self) -> str:
        """Return string keterangan status slot."""
        pass

    @abstractmethod
    def bisa_dipesan(self) -> bool:
        """Return True jika slot masih bisa dipesan."""
        pass


class SlotTersedia(StatusSlot):
    """Status slot yang belum dipesan — masih tersedia."""

    def keterangan(self) -> str:
        """Return keterangan status tersedia."""
        return "Tersedia"

    def bisa_dipesan(self) -> bool:
        """Return True karena slot masih bisa dipesan."""
        return True


class SlotTerpesan(StatusSlot):
    """Status slot yang sudah dipesan oleh seseorang."""

    def __init__(self, nama_pemesan: str) -> None:
        """
        Inisialisasi status terpesan.

        Args:
            nama_pemesan: Nama orang yang memesan slot ini.
        """
        self.nama_pemesan = nama_pemesan

    def keterangan(self) -> str:
        """Return keterangan status beserta nama pemesan."""
        return f"Terpesan oleh {self.nama_pemesan}"

    def bisa_dipesan(self) -> bool:
        """Return False karena slot sudah dipesan."""
        return False


class Slot:
    """Entitas satu unit waktu sewa pada suatu lapangan."""

    def __init__(self, id_slot: str, jam_mulai: str, jam_selesai: str) -> None:
        """
        Inisialisasi slot waktu.

        Args:
            id_slot: ID unik slot, misal 'F1-20250601-0800'.
            jam_mulai: Jam mulai dalam format 'HH:MM', misal '08:00'.
            jam_selesai: Jam selesai dalam format 'HH:MM', misal '10:00'.

        Raises:
            SlotTidakValidError: Jika jam selesai tidak lebih besar dari jam mulai.
        """
        jam_mulai_int = int(jam_mulai.replace(":", ""))
        jam_selesai_int = int(jam_selesai.replace(":", ""))
        if jam_selesai_int <= jam_mulai_int:
            raise SlotTidakValidError(
                f"Jam selesai ({jam_selesai}) harus setelah jam mulai ({jam_mulai})."
            )

        self.id_slot = id_slot
        self.jam_mulai = jam_mulai
        self.jam_selesai = jam_selesai
        self._status: StatusSlot = SlotTersedia()

    @property
    def status(self) -> StatusSlot:
        """Getter status slot saat ini."""
        return self._status

    def pesan(self, nama_pemesan: str) -> None:
        """
        Pesan slot ini atas nama pemesan.

        Args:
            nama_pemesan: Nama orang yang memesan.

        Raises:
            SlotSudahDipesanError: Jika slot sudah dipesan sebelumnya.
        """
        if not self._status.bisa_dipesan():
            raise SlotSudahDipesanError(
                f"Slot {self.id_slot} sudah {self._status.keterangan()}."
            )
        self._status = SlotTerpesan(nama_pemesan)

    def __str__(self) -> str:
        """Representasi string slot beserta status."""
        return (
            f"[{self.id_slot}] {self.jam_mulai}–{self.jam_selesai} | "
            f"{self._status.keterangan()}"
        )