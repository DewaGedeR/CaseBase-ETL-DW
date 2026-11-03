
import logging
import re

import pandas as pd

log = logging.getLogger(__name__)


# NAMA HARI DAN BULAN
HARI = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu"
}

BULAN = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}

# Singkatan bulan Indonesia dan Inggris
BULAN_SINGKAT = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mei": 5,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "agu": 8,
    "aug": 8,
    "sep": 9,
    "okt": 10,
    "oct": 10,
    "nov": 11,
    "des": 12,
    "dec": 12
}


# 1. PARSING TANGGAL
def parse_tanggal(nilai):
    """
    Mengubah berbagai format tanggal menjadi pd.Timestamp.

    Format yang dikenali:
    yyyy-mm-dd
    dd/mm/yyyy
    dd-mm-yyyy
    dd Mon yyyy

    Jika kosong atau tidak valid, hasilnya pd.NaT.
    """

    if pd.isna(nilai):
        return pd.NaT

    teks = str(nilai).strip()

    try:
        # Format yyyy-mm-dd
        m = re.fullmatch(
            r"(\d{4})-(\d{1,2})-(\d{1,2})",
            teks
        )

        if m:
            return pd.Timestamp(
                int(m[1]),
                int(m[2]),
                int(m[3])
            )

        # Format dd/mm/yyyy atau dd-mm-yyyy
        m = re.fullmatch(
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
            teks
        )

        if m:
            return pd.Timestamp(
                int(m[3]),
                int(m[2]),
                int(m[1])
            )

        # Format dd Mon yyyy
        m = re.fullmatch(
            r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
            teks
        )

        if m:
            bulan = BULAN_SINGKAT.get(
                m[2][:3].lower()
            )

            if bulan is None:
                return pd.NaT

            return pd.Timestamp(
                int(m[3]),
                bulan,
                int(m[1])
            )

    except (ValueError, KeyError):
        return pd.NaT

    return pd.NaT


# 2. MEMBUAT SURROGATE KEY WAKTU
def tanggal_ke_key(tanggal):
    """
    Mengubah Series tanggal menjadi waktu_key
    dengan format yyyymmdd.

    Contoh:
    2025-09-23 menjadi 20250923.
    """

    return (
        tanggal.dt.year * 10000
        + tanggal.dt.month * 100
        + tanggal.dt.day
    ).astype("Int64")


# 3. TRANSFORM DIMENSI WAKTU
def build_dim_waktu(penjualan):
    """
    Membentuk tabel dim_waktu dari kolom tanggal
    pada data penjualan hasil extract.
    """

    log.info("=== TRANSFORM DIMENSI WAKTU ===")

    df = penjualan.copy()

    # 1. Mengubah tanggal ke format datetime
    tanggal = pd.to_datetime(
        df["tanggal"].apply(parse_tanggal)
    )

    # 2. Menghitung tanggal tidak valid
    n_invalid = int(tanggal.isna().sum())

    log.info(
        "Tanggal tidak valid/kosong: %d dari %d",
        n_invalid,
        len(tanggal)
    )

    # 3. Mengambil tanggal unik dan mengurutkannya
    unik = (
        tanggal.dropna()
        .dt.normalize()
        .drop_duplicates()
        .sort_values()
    )

    dim = unik.to_frame(
        "tanggal"
    ).reset_index(drop=True)

    # 4. Membuat surrogate key
    dim["waktu_key"] = tanggal_ke_key(
        dim["tanggal"]
    ).astype(int)

    # 5. Membentuk atribut waktu
    dim["hari"] = (
        dim["tanggal"]
        .dt.weekday
        .map(HARI)
    )

    dim["bulan"] = (
        dim["tanggal"]
        .dt.month
        .map(BULAN)
    )

    dim["kuartal"] = (
        "Q" + dim["tanggal"].dt.quarter.astype(str)
    )

    dim["tahun"] = (
        dim["tanggal"].dt.year.astype(int)
    )

    # 6. Mengubah tanggal menjadi tipe DATE
    dim["tanggal"] = dim["tanggal"].dt.date

    # 7. Memastikan urutan kolom
    dim = dim[
        [
            "waktu_key",
            "tanggal",
            "hari",
            "bulan",
            "kuartal",
            "tahun"
        ]
    ]

    # 8. Logging hasil transformasi
    log.info(
        "dim_waktu: %d baris, %d kolom",
        *dim.shape
    )

    if not dim.empty:
        log.info(
            "Rentang tanggal: %s sampai %s",
            dim["tanggal"].min(),
            dim["tanggal"].max()
        )

    return dim
