
import pandas as pd
import logging

log = logging.getLogger(__name__)


def transform_dim_produk(df_produk):
    log.info("=== TRANSFORM DIMENSI PRODUK ===")

    df = df_produk.copy()

    # 1. Memilih kolom yang dibutuhkan
    kolom = [
        "id_produk",
        "nama_produk",
        "kategori",
        "merek"
    ]

    df = df[kolom]

    # 2. Membersihkan spasi dan nilai kosong
    for col in kolom:
        df[col] = df[col].astype("string").str.strip()

    df = df.replace("", pd.NA)

    # 3. Menghapus data tanpa ID produk
    df = df.dropna(subset=["id_produk"])

    # 4. Membersihkan nama produk dan merek
    df["nama_produk"] = df["nama_produk"].str.strip()
    df["merek"] = df["merek"].str.strip()

    # 5. Menyeragamkan kategori produk
    df["kategori"] = df["kategori"].str.lower().str.strip()

    mapping_kategori = {
        "mamin": "Makanan & Minuman",
        "makanan & minuman": "Makanan & Minuman",
        "rumah tangga": "Rumah Tangga",
        "elektronik": "Elektronik",
        "fashion": "Fashion",
        "olahraga": "Olahraga",
        "kesehatan & kecantikan": "Kesehatan & Kecantikan",
        "kesehatan dan kecantikan": "Kesehatan & Kecantikan"
    }

    df["kategori"] = df["kategori"].map(mapping_kategori).fillna(
        df["kategori"].str.title()
    )

    # 6. Menangani nilai kosong
    df["nama_produk"] = df["nama_produk"].fillna("Tidak Diketahui")
    df["kategori"] = df["kategori"].fillna("Tidak Diketahui")
    df["merek"] = df["merek"].fillna("Tidak Diketahui")

    # 7. Menghapus produk duplikat berdasarkan ID produk
    jumlah_awal = len(df)

    df = df.drop_duplicates(
        subset=["id_produk"],
        keep="first"
    )

    jumlah_duplikat = jumlah_awal - len(df)

    log.info("Jumlah data duplikat dihapus: %d", jumlah_duplikat)

    # 8. Membuat surrogate key
    df = df.reset_index(drop=True)

    df.insert(
        0,
        "produk_key",
        range(1, len(df) + 1)
    )

    # 9. Memastikan urutan kolom dimensi produk
    df = df[
        [
            "produk_key",
            "id_produk",
            "nama_produk",
            "kategori",
            "merek"
        ]
    ]

    # 10. Menambahkan baris "Tidak Diketahui" (key 0) untuk transaksi
    # yang produknya tidak ada pada master produk
    tidak_diketahui = pd.DataFrame([{
        "produk_key": 0,
        "id_produk": "-",
        "nama_produk": "Tidak Diketahui",
        "kategori": "Tidak Diketahui",
        "merek": "Tidak Diketahui"
    }])

    df = pd.concat([tidak_diketahui, df], ignore_index=True)

    log.info("Jumlah data dim_produk: %d", len(df))

    return df
