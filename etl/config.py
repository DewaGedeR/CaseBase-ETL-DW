from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

CSV_PATH = DATA_DIR / "penjualan.csv"
XLSX_PATH = DATA_DIR / "produk.xlsx"

DB_USER = "postgres"
DB_PASSWORD = "postgresql"
DB_HOST = "localhost"
DB_PORT = "5432"

# Database sumber
SOURCE_DB = "tokomaju_oltp"

# Database tujuan Data Warehouse
TARGET_DB = "tokomaju_dw"

SOURCE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{SOURCE_DB}"
)

TARGET_URL = (
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{TARGET_DB}"
)