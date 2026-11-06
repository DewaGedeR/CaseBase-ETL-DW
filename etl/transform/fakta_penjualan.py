import logging

import pandas as pd

from transform.dim_waktu import parse_tanggal, tanggal_ke_key

log = logging.getLogger(__name__)


# TRANSFORM FAKTA PENJUALAN
def transform_fakta_penjualan(
    df_penjualan,
    df_dim_pelanggan,
    df_dim_produk,
    df_dim_waktu,
    df_dim_metode_bayar
):

    log.info("=== TRANSFORM FAKTA PENJUALAN ===")

    kolom_fakta = [
        "id_transaksi",
        "waktu_key",
        "pelanggan_key",
        "produk_key",
        "metode_bayar_key",
        "qty",
        "harga_satuan",
        "total_penjualan"
    ]

    # 1. Memeriksa data penjualan
    if df_penjualan is None or df_penjualan.empty:
        log.warning("Data penjualan kosong.")
        return pd.DataFrame(columns=kolom_fakta)

    # 2. Menyalin data sumber
    df = df_penjualan.copy()
    n_mentah = len(df)

    # 3. Menghapus duplikasi baris penuh
    df = df.drop_duplicates()
    n_duplikat = n_mentah - len(df)

    # 4. Membersihkan ID transaksi dan ID dimensi
    kolom_id = [
        "id_transaksi",
        "id_produk",
        "id_pelanggan"
    ]

    for col in kolom_id:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

        df[col] = df[col].replace(
            ["", "NULL", "NONE", "NAN", "-"],
            pd.NA
        )

    # Menyeragamkan format ID pelanggan
    df["id_pelanggan"] = df["id_pelanggan"].str.upper()

    # 5. Mengubah tanggal transaksi menjadi datetime
    df["tanggal"] = pd.to_datetime(
        df["tanggal"].apply(parse_tanggal)
    )

    n_tanggal_invalid = int(df["tanggal"].isna().sum())

    # 6. Membuat waktu_key dari tanggal transaksi
    df["waktu_key"] = tanggal_ke_key(
        df["tanggal"]
    )

    # 7. Memastikan waktu_key tersedia pada dimensi waktu
    ada_di_dim_waktu = df["waktu_key"].isin(
        df_dim_waktu["waktu_key"]
    )

    n_waktu_tidak_ditemukan = int(
        (~ada_di_dim_waktu).sum()
    )

    # Mengeluarkan transaksi yang tidak memiliki pasangan waktu
    df = df[ada_di_dim_waktu].copy()

    # 8. Mengubah qty menjadi numerik
    df["qty"] = pd.to_numeric(
        df["qty"],
        errors="coerce"
    )

    # 9. Membersihkan harga satuan
    # Contoh: Rp85.000 menjadi 85000
    df["harga_satuan"] = pd.to_numeric(
        df["harga_satuan"]
        .astype("string")
        .str.replace("Rp", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce"
    )

    n_numerik_invalid = int(
        (
            df["qty"].isna()
            | df["harga_satuan"].isna()
        ).sum()
    )

    # 10. Mengeluarkan qty kosong, nol, atau negatif
    n_sebelum_qty = len(df)

    df = df[df["qty"] > 0].copy()

    n_qty_tidak_valid = n_sebelum_qty - len(df)

    # 11. Menghubungkan dengan dimensi pelanggan
    peta_pelanggan = df_dim_pelanggan[
        [
            "id_pelanggan",
            "pelanggan_key"
        ]
    ].copy()

    peta_pelanggan["id_pelanggan"] = (
        peta_pelanggan["id_pelanggan"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df = df.merge(
        peta_pelanggan,
        on="id_pelanggan",
        how="left",
        validate="many_to_one"
    )

    # 12. Menghubungkan dengan dimensi produk
    peta_produk = df_dim_produk[
        [
            "id_produk",
            "produk_key"
        ]
    ].copy()

    peta_produk["id_produk"] = (
        peta_produk["id_produk"]
        .astype("string")
        .str.strip()
    )

    df = df.merge(
        peta_produk,
        on="id_produk",
        how="left",
        validate="many_to_one"
    )

    # 13. Menghitung pelanggan dan produk yang tidak ditemukan
    n_pelanggan_tidak_ditemukan = int(
        df["pelanggan_key"].isna().sum()
    )

    n_produk_tidak_ditemukan = int(
        df["produk_key"].isna().sum()
    )

    # 14. Mengarahkan data tanpa pasangan ke key 0
    # Key 0 merupakan baris "Tidak Diketahui" pada dimensi
    df["pelanggan_key"] = df["pelanggan_key"].fillna(0)
    df["produk_key"] = df["produk_key"].fillna(0)

    # 15. Menghitung total penjualan
    df["total_penjualan"] = (
        df["qty"] * df["harga_satuan"]
    )

    # 16. Menangani metode pembayaran kosong
    df["metode_bayar"] = (
        df["metode_bayar"]
        .astype("string")
        .str.strip()
        .fillna("Tidak Diketahui")
    )

    df["metode_bayar"] = df["metode_bayar"].replace(
        "",
        "Tidak Diketahui"
    )

    # 17. Menghubungkan dengan dimensi metode pembayaran
    peta_metode_bayar = df_dim_metode_bayar[
        [
            "metode_bayar",
            "metode_bayar_key"
        ]
    ].copy()

    df = df.merge(
        peta_metode_bayar,
        on="metode_bayar",
        how="left",
        validate="many_to_one"
    )

    # Jika metode pembayaran tidak ditemukan, gunakan key 0
    df["metode_bayar_key"] = (
        df["metode_bayar_key"]
        .fillna(0)
    )

    # 18. Menghapus data yang tidak memiliki ID transaksi
    # atau nilai transaksi yang valid
    jumlah_awal = len(df)

    df = df.dropna(
        subset=[
            "id_transaksi",
            "waktu_key",
            "qty",
            "harga_satuan"
        ]
    ).copy()

    jumlah_dihapus = jumlah_awal - len(df)

    # 19. Memastikan tipe data akhir
    df["waktu_key"] = df["waktu_key"].astype(int)
    df["pelanggan_key"] = df["pelanggan_key"].astype(int)
    df["produk_key"] = df["produk_key"].astype(int)
    df["metode_bayar_key"] = df["metode_bayar_key"].astype(int)

    df["qty"] = df["qty"].astype(int)
    df["harga_satuan"] = df["harga_satuan"].astype(int)
    df["total_penjualan"] = df["total_penjualan"].astype(int)

    # 20. Memilih kolom tabel fakta
    fakta_final = df[kolom_fakta].copy()

    # 21. Logging hasil transformasi
    log.info("Baris mentah: %d", n_mentah)
    log.info("Duplikat dihapus: %d", n_duplikat)
    log.info("Tanggal tidak valid: %d", n_tanggal_invalid)
    log.info("Waktu tidak ditemukan di dimensi: %d", n_waktu_tidak_ditemukan)
    log.info("Nilai qty/harga tidak valid: %d", n_numerik_invalid)
    log.info("Qty kosong/nol/negatif dihapus: %d", n_qty_tidak_valid)

    log.info(
        "Pelanggan tidak ditemukan (key 0): %d",
        n_pelanggan_tidak_ditemukan
    )

    log.info(
        "Produk tidak ditemukan (key 0): %d",
        n_produk_tidak_ditemukan
    )

    log.info("Data tidak valid yang dihapus pada tahap akhir: %d", jumlah_dihapus)

    log.info(
        "fakta_penjualan: %d baris, %d kolom",
        *fakta_final.shape
    )

    log.info(
        "Total penjualan fakta: %d",
        fakta_final["total_penjualan"].sum()
    )

    return fakta_final