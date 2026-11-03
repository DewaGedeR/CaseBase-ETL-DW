import logging

from etl.extract import extract
from etl.transform.dim_produk import transform_dim_produk
from etl.transform.dim_pelanggan import build_dim_pelanggan
from etl.transform.dim_waktu import build_dim_waktu
from etl.transform.fakta_penjualan import transform_fakta_penjualan
from etl.load import load


# KONFIGURASI LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


# MAIN ETL
def main():

    log.info("========== MEMULAI ETL TOKOMAJU ==========")

    try:
        # 1. EXTRACT
        df_jual, df_produk, df_pel = extract()

        # 2. TRANSFORM DIMENSI PRODUK
        dim_produk = transform_dim_produk(df_produk)

        # 3. TRANSFORM DIMENSI PELANGGAN
        dim_pelanggan = build_dim_pelanggan(df_pel)

        # 4. TRANSFORM DIMENSI WAKTU
        dim_waktu = build_dim_waktu(df_jual)

        # 5. TRANSFORM FAKTA PENJUALAN
        fakta_penjualan = transform_fakta_penjualan(
            df_jual,
            dim_pelanggan,
            dim_produk,
            dim_waktu
        )

        # 6. PREVIEW HASIL TRANSFORMASI
        print("\n========== PREVIEW HASIL TRANSFORMASI ==========")

        print("\n=== DIMENSI PRODUK ===")
        print(dim_produk.head(5).to_string(index=False))

        print("\n=== DIMENSI PELANGGAN ===")
        print(dim_pelanggan.head(5).to_string(index=False))

        print("\n=== DIMENSI WAKTU ===")
        print(dim_waktu.head(5).to_string(index=False))

        print("\n=== FAKTA PENJUALAN ===")
        print(fakta_penjualan.head(5).to_string(index=False))

        # 7. LOAD
        load(
            dim_produk,
            dim_pelanggan,
            dim_waktu,
            fakta_penjualan
        )

        log.info("========== ETL TOKOMAJU BERHASIL ==========")

    except Exception:
        log.exception("ETL TOKOMAJU GAGAL.")
        raise


if __name__ == "__main__":
    main()