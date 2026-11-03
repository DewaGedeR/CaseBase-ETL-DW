-- Skema bintang TokoMaju (database tujuan: tokomaju_dw)
-- Dijalankan otomatis oleh etl/load.py di awal proses load.

-- 1. Hapus tabel lama (fakta lebih dulu karena merujuk dimensi)
DROP TABLE IF EXISTS fakta_penjualan;
DROP TABLE IF EXISTS dim_waktu;
DROP TABLE IF EXISTS dim_produk;
DROP TABLE IF EXISTS dim_pelanggan;

-- 2. Tabel dimensi
CREATE TABLE dim_waktu (
    waktu_key   INT         PRIMARY KEY,
    tanggal     DATE        NOT NULL,
    hari        VARCHAR(10) NOT NULL,
    bulan       VARCHAR(10) NOT NULL,
    kuartal     VARCHAR(2)  NOT NULL,
    tahun       INT         NOT NULL
);

CREATE TABLE dim_produk (
    produk_key  INT          PRIMARY KEY,
    id_produk   VARCHAR(10)  NOT NULL,
    nama_produk VARCHAR(100) NOT NULL,
    kategori    VARCHAR(50)  NOT NULL,
    merek       VARCHAR(50)  NOT NULL
);

CREATE TABLE dim_pelanggan (
    pelanggan_key  INT          PRIMARY KEY,
    id_pelanggan   VARCHAR(10)  NOT NULL,
    nama_pelanggan VARCHAR(100) NOT NULL,
    kota           VARCHAR(50)  NOT NULL,
    telepon        VARCHAR(20)
);

-- 3. Tabel fakta
CREATE TABLE fakta_penjualan (
    id_transaksi    VARCHAR(10) PRIMARY KEY,
    waktu_key       INT         NOT NULL REFERENCES dim_waktu (waktu_key),
    pelanggan_key   INT         NOT NULL REFERENCES dim_pelanggan (pelanggan_key),
    produk_key      INT         NOT NULL REFERENCES dim_produk (produk_key),
    qty             INT         NOT NULL CHECK (qty > 0),
    harga_satuan    NUMERIC(12, 0) NOT NULL,
    total_penjualan NUMERIC(14, 0) NOT NULL,
    metode_bayar    VARCHAR(20) NOT NULL
);
