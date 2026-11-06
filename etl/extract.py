import logging

import pandas as pd
from sqlalchemy import create_engine

from config import CSV_PATH, XLSX_PATH, SOURCE_URL

log = logging.getLogger(__name__)


# 1. EXTRACT
def extract():
    log.info("=== EXTRACT ===")

    # 1a. Extract CSV (penjualan)
    df_jual = pd.read_csv(
        CSV_PATH,
        sep=";",
        dtype=str,
        encoding="utf-8-sig"
    )
    log.info("penjualan.csv : %d baris, %d kolom", *df_jual.shape)

    # 1b. Extract Excel (produk)
    df_produk = pd.read_excel(
        XLSX_PATH,
        sheet_name="Produk",
        dtype=str
    )
    log.info("produk.xlsx   : %d baris, %d kolom", *df_produk.shape)

    # 1c. Extract database (pelanggan)
    src = create_engine(SOURCE_URL)
    try:
        df_pel = pd.read_sql("SELECT * FROM pelanggan", src)
        df_pel = df_pel.astype(object)
    finally:
        src.dispose()
    log.info("db.pelanggan  : %d baris, %d kolom", *df_pel.shape)

    return df_jual, df_produk, df_pel


# 2. MENJALANKAN DAN MENGECEK HASIL EXTRACT
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    df_jual, df_produk, df_pel = extract()

    print("\n=== DATA PENJUALAN ===")
    print(df_jual.head())

    print("\n=== DATA PRODUK ===")
    print(df_produk.head())

    print("\n=== DATA PELANGGAN ===")
    print(df_pel.head())

    print("\n=== INFORMASI DATA ===")

    print("\nData Penjualan:")
    df_jual.info()

    print("\nData Produk:")
    df_produk.info()

    print("\nData Pelanggan:")
    df_pel.info()