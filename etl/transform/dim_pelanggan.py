import logging
import re

import pandas as pd

log = logging.getLogger(__name__)


# 1. NORMALISASI KOTA
def normalisasi_kota(nilai):
    if pd.isna(nilai):
        return "Tidak Diketahui"

    teks = re.sub(r"\s+", " ", str(nilai)).strip()

    if teks.lower() in {"", "null", "none", "nan", "-"}:
        return "Tidak Diketahui"

    return teks.title()


# 2. NORMALISASI NOMOR TELEPON
def normalisasi_telepon(nilai):
    if pd.isna(nilai):
        return pd.NA

    digit = re.sub(r"\D", "", str(nilai))

    if digit.startswith("62"):
        sisa = digit[2:]
    elif digit.startswith("0"):
        sisa = digit[1:]
    else:
        sisa = digit

    sisa = sisa.lstrip("0")

    if not 8 <= len(sisa) <= 13:
        return pd.NA

    return "+62" + sisa


# 3. TRANSFORM DIMENSI PELANGGAN
def build_dim_pelanggan(pelanggan):

    log.info("=== TRANSFORM DIMENSI PELANGGAN ===")

    df = pelanggan.copy()

    n_awal = len(df)

    # 1. Memilih kolom yang dibutuhkan
    kolom = [
        "id_pelanggan",
        "nama",
        "kota",
        "telepon"
    ]

    df = df[kolom].copy()

    # 2. Membersihkan ID pelanggan
    df["id_pelanggan"] = (
        df["id_pelanggan"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df["id_pelanggan"] = df["id_pelanggan"].replace(
        ["", "NULL", "NONE", "NAN", "-"],
        pd.NA
    )

    # 3. Menghapus data tanpa ID pelanggan
    n_tanpa_id = int(df["id_pelanggan"].isna().sum())

    df = df.dropna(subset=["id_pelanggan"])

    # 4. Menghapus duplikasi ID pelanggan
    n_sebelum = len(df)

    df = df.drop_duplicates(
        subset=["id_pelanggan"],
        keep="first"
    )

    n_duplikat = n_sebelum - len(df)

    # 5. Membersihkan nama pelanggan
    df["nama"] = (
        df["nama"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    df["nama"] = df["nama"].replace(
        ["", "Null", "None", "Nan", "-"],
        pd.NA
    )

    df["nama_pelanggan"] = df["nama"].fillna("Tanpa Nama")

    # 6. Normalisasi kota
    df["kota"] = df["kota"].apply(normalisasi_kota)

    n_kota_kosong = int(
        df["kota"].eq("Tidak Diketahui").sum()
    )

    # 7. Normalisasi nomor telepon
    df["telepon"] = df["telepon"].apply(normalisasi_telepon)

    n_telepon_invalid = int(df["telepon"].isna().sum())

    # 8. Mengurutkan data berdasarkan ID pelanggan
    df = df.sort_values(
        "id_pelanggan"
    ).reset_index(drop=True)

    # 9. Membuat surrogate key
    df.insert(
        0,
        "pelanggan_key",
        range(1, len(df) + 1)
    )

    # 10. Memilih kolom akhir dimensi pelanggan
    dim = df[
        [
            "pelanggan_key",
            "id_pelanggan",
            "nama_pelanggan",
            "kota",
            "telepon"
        ]
    ].copy()

    # 11. Menambahkan baris "Tidak Diketahui" (key 0) untuk transaksi
    # tanpa pelanggan
    tidak_diketahui = pd.DataFrame([{
        "pelanggan_key": 0,
        "id_pelanggan": "-",
        "nama_pelanggan": "Tidak Diketahui",
        "kota": "Tidak Diketahui",
        "telepon": pd.NA
    }])

    dim = pd.concat([tidak_diketahui, dim], ignore_index=True)

    # 12. Logging hasil transformasi
    log.info(
        "dim_pelanggan: %d baris awal -> %d baris akhir",
        n_awal,
        len(dim)
    )

    log.info("Data tanpa ID dihapus: %d", n_tanpa_id)
    log.info("Data duplikat dihapus: %d", n_duplikat)
    log.info("Kota kosong/tidak diketahui: %d", n_kota_kosong)
    log.info("Nomor telepon tidak valid: %d", n_telepon_invalid)

    log.info(
        "dim_pelanggan: %d baris, %d kolom",
        *dim.shape
    )

    return dim


# 4. MEMBUAT PETA ID PELANGGAN DAN SURROGATE KEY
def buat_peta_pelanggan(dim):

    return dict(
        zip(
            dim["id_pelanggan"],
            dim["pelanggan_key"]
        )
    )