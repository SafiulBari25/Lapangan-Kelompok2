"""
services/api_client.py — Konsumsi REST API frankfurter.app untuk kurs mata uang.

Fungsi:
    get_kurs()               — Ambil kurs IDR ke mata uang tujuan secara real-time.
    harga_dalam_mata_uang()  — Konversi harga IDR ke string mata uang asing.
"""

import requests

BASE_URL = "https://api.frankfurter.app"


def get_kurs(mata_uang_tujuan: str) -> float:
    """
    Ambil kurs konversi IDR ke mata uang tujuan dari API frankfurter.app.

    Args:
        mata_uang_tujuan: Kode mata uang tujuan, misal 'USD', 'SGD', 'EUR'.

    Returns:
        Nilai kurs sebagai float, misal 0.000064 untuk USD.

    Raises:
        ConnectionError: Jika terjadi timeout atau masalah koneksi jaringan.
        ValueError: Jika API mengembalikan respons error (4xx/5xx) atau
                    mata uang tidak dikenali.
    """
    url = f"{BASE_URL}/latest"
    params = {"from": "IDR", "to": mata_uang_tujuan.upper()}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # raise HTTPError untuk 4xx/5xx
    except requests.exceptions.Timeout:
        raise ConnectionError(
            "Koneksi ke server kurs timeout. Periksa koneksi internet Anda."
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Tidak dapat terhubung ke server kurs. Periksa koneksi internet Anda."
        )
    except requests.exceptions.HTTPError as e:
        raise ValueError(
            f"API kurs mengembalikan error {e.response.status_code}. "
            f"Pastikan kode mata uang '{mata_uang_tujuan}' valid."
        )

    data = response.json()
    rates = data.get("rates", {})
    kurs = rates.get(mata_uang_tujuan.upper())

    if kurs is None:
        raise ValueError(
            f"Mata uang '{mata_uang_tujuan}' tidak ditemukan dalam respons API."
        )

    return float(kurs)


def harga_dalam_mata_uang(harga_idr: float, mata_uang_tujuan: str) -> str:
    """
    Konversi harga IDR ke mata uang asing dan kembalikan sebagai string.

    Args:
        harga_idr: Harga dalam rupiah.
        mata_uang_tujuan: Kode mata uang tujuan, misal 'USD'.

    Returns:
        String siap tampil, contoh: 'USD 6.40'.

    Raises:
        ConnectionError: Jika tidak bisa terhubung ke API.
        ValueError: Jika mata uang tidak valid atau API error.
    """
    kurs = get_kurs(mata_uang_tujuan)
    harga_konversi = harga_idr * kurs
    kode = mata_uang_tujuan.upper()
    return f"{kode} {harga_konversi:.2f}"