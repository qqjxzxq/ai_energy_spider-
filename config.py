# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OPENALEX_BASE = "https://api.openalex.org/works"

OUTPUT_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

RAW_ENERGY_CSV = os.path.join(OUTPUT_DIR, "energy_papers_raw.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

PER_PAGE = 200
MAX_RESULTS = 100
SLEEP_BETWEEN_REQ = 0.4

ENERGY_TERMS = [
    "energy",
    "electricity",
    "power",
    "load",
    "demand",
    "smart grid",
    "renewable",
    "solar",
    "photovoltaic",
    "wind",
    "hydropower",
    "energy efficiency",
    "energy management",
    "battery",
    "energy storage",
    "electric vehicle",
]
