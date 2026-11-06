import logging

from sqlalchemy import create_engine, text

from config import TARGET_URL

log = logging.getLogger(__name__)

engine = create_engine(TARGET_URL)


# 1. LOAD SATU TABEL KE POSTGRESQL
def load_to_postgres(df, table_name, connection):
    if df is None or df.empty:
        log.warning(
            "DataFrame untuk tabel '%s' kosong. Load dilewati.",
            table_name
        )
        return

    log.info(
        "Memulai load tabel '%s': %d baris",
        table_name,
        len(df)
    )

    df.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False
    )

    # Memastikan jumlah baris di database sama dengan DataFrame
    jumlah_db = connection.execute(
        text(f"SELECT COUNT(*) FROM {table_name}")
    ).scalar()

    if jumlah_db != len(df):
        raise ValueError(
            f"Jumlah baris '{table_name}' tidak cocok: "
            f"DataFrame={len(df)}, database={jumlah_db}"
        )

    log.info(
        "Load tabel '%s' berhasil: %d baris",
        table_name,
        jumlah_db
    )


# 2. LOAD SELURUH DATA WAREHOUSE
def load(
    dim_produk,
    dim_pelanggan,
    dim_waktu,
    dim_metode_bayar,
    fakta_penjualan
):

    log.info("=== LOAD DATA WAREHOUSE ===")

    try:
        with engine.begin() as connection:

            # 1. Menghapus tabel fakta lama terlebih dahulu
            # agar tidak bergantung pada tabel dimensi lama.
            connection.execute(
                text("DROP TABLE IF EXISTS fakta_penjualan")
            )

            # 2. Load dimensi pelanggan
            load_to_postgres(
                dim_pelanggan,
                "dim_pelanggan",
                connection
            )

            # 3. Load dimensi produk
            load_to_postgres(
                dim_produk,
                "dim_produk",
                connection
            )

            # 4. Load dimensi waktu
            load_to_postgres(
                dim_waktu,
                "dim_waktu",
                connection
            )

            # load dimensi metode bayar
            load_to_postgres(
                dim_metode_bayar,
                "dim_metode_bayar",
                connection
            )

            # 5. Load fakta penjualan
            load_to_postgres(
                fakta_penjualan,
                "fakta_penjualan",
                connection
            )

        log.info("Load seluruh data warehouse berhasil.")

    except Exception:
        log.exception(
            "Terjadi kesalahan saat proses load data warehouse."
        )
        raise

    finally:
        engine.dispose()