import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

CSV_PATH = DATA_DIR / "penjualan.csv"
XLSX_PATH = DATA_DIR / "produk.xlsx"

DB_USER = os.getenv("DB_USER")

DB_PASSWORD_SOURCE = os.getenv("DB_PASSWORD_SOURCE")
DB_PASSWORD_TARGET = os.getenv("DB_PASSWORD_TARGET")

DB_HOST = os.getenv("DB_HOST")

SOURCE_PORT = os.getenv("SOURCE_PORT")
TARGET_PORT = os.getenv("TARGET_PORT")

# Database sumber
SOURCE_DB = os.getenv("SOURCE_DB")

# Database tujuan Data Warehouse
TARGET_DB = os.getenv("TARGET_DB")

SOURCE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD_SOURCE)}"
    f"@{DB_HOST}:{SOURCE_PORT}/{SOURCE_DB}"
)

TARGET_URL = (
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD_TARGET)}"
    f"@{DB_HOST}:{TARGET_PORT}/{TARGET_DB}"
)