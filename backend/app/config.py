from pathlib import Path
from types import SimpleNamespace

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# =========================================================
# DATA DIRECTORIES
# =========================================================

DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_PATH = DATA_DIR / "chroma_db"
REGISTRY_PATH = DATA_DIR / "document_registry.json"

# =========================================================
# CREATE DIRECTORIES
# =========================================================

for path in (DATA_DIR, UPLOAD_DIR, CHROMA_PATH):
    path.mkdir(parents=True, exist_ok=True)

# Compatibility object used by code expecting settings.chroma_path
settings = SimpleNamespace(chroma_path=CHROMA_PATH)