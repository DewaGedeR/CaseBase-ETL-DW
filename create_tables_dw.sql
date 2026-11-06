-- Skema bintang TokoMaju (database tujuan: tokomaju_dw)
-- Disesuaikan dengan keluaran etl/load.py:
--   * 4 dimensi: dim_pelanggan, dim_produk, dim_waktu, dim_metode_bayar
--   * fakta_penjualan memakai composite PK (id_transaksi, produk_key)
--   * metode bayar di fakta berupa FK metode_bayar_key ke dim_metode_bayar

-- 1. Hapus tabel lama (fakta lebih dulu karena merujuk dimensi)
DROP TABLE IF EXISTS fakta_penjualan;
DROP TABLE IF EXISTS dim_metode_bayar;
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

-- CATATAN: kolom selain metode_bayar_key mengikuti dugaan (sesuaikan dengan
-- DataFrame dim_metode_bayar di transform.py).
CREATE TABLE dim_metode_bayar (
    metode_bayar_key INT         PRIMARY KEY,
    metode_bayar     VARCHAR(20) NOT NULL
);

-- 3. Tabel fakta
CREATE TABLE fakta_penjualan (
    id_transaksi     VARCHAR(10)    NOT NULL,
    waktu_key        INT            NOT NULL,
    pelanggan_key    INT            NOT NULL,
    produk_key       INT            NOT NULL,
    metode_bayar_key INT            NOT NULL,
    qty              INT            NOT NULL CHECK (qty > 0),
    harga_satuan     NUMERIC(12, 0) NOT NULL,
    total_penjualan  NUMERIC(14, 0) NOT NULL,

    -- composite primary key (satu transaksi bisa memuat banyak produk)
    CONSTRAINT pk_fakta_penjualan PRIMARY KEY (id_transaksi, produk_key),

    CONSTRAINT fk_fakta_waktu        FOREIGN KEY (waktu_key)        REFERENCES dim_waktu (waktu_key),
    CONSTRAINT fk_fakta_pelanggan    FOREIGN KEY (pelanggan_key)    REFERENCES dim_pelanggan (pelanggan_key),
    CONSTRAINT fk_fakta_produk       FOREIGN KEY (produk_key)       REFERENCES dim_produk (produk_key),
    CONSTRAINT fk_fakta_metode_bayar FOREIGN KEY (metode_bayar_key) REFERENCES dim_metode_bayar (metode_bayar_key)
);
