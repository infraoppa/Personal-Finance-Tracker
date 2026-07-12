import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

loaded = load_dotenv(ENV_PATH)

APP_TITLE = os.getenv("APP_TITLE")

print(APP_TITLE)