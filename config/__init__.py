"""
Configuration package
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Gemini API - Production'da environment variable'dan al
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Label mappings and categories
LABEL_MAP = {
    "No Harassment / Neutral": 0,
    "Direct Insult / Profanity": 1,
    "Sexist / Sexual Implication": 2,
    "Sarcasm / Microaggression": 3,
    "Appearance-based Criticism": 4,
}

REVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

CATEGORY_NAMES = {
    0: "No Harassment / Neutral",
    1: "Direct Insult / Profanity",
    2: "Sexist / Sexual Implication",
    3: "Sarcasm / Microaggression",
    4: "Appearance-based Criticism",
}
