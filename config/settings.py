"""
Instagram Comments Scraper Configuration
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
SCRAPERS_DIR = BASE_DIR / "scrapers"
DATA_DIR = BASE_DIR / "data"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Instagram credentials
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")

# Database Configuration
# Render provides DATABASE_URL as an environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not provided, construct it from individual parts
if not DATABASE_URL:
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "cyberbullying_db")
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "cyberbullying-secret-key-change-in-production-2024")
if ENVIRONMENT == "production" and SECRET_KEY == "cyberbullying-secret-key-change-in-production-2024":
    raise ValueError("SECRET_KEY must be set in production environment!")
    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 7 days default

# Scraping settings (Free tier için optimize - HIZLI)
DEFAULT_MAX_COMMENTS = 20  # Çok az yorum (3-5 dakika altında bitmeli)
SCROLL_TIMEOUT = 30  # 30 saniye max
SCROLL_DELAY = 1  # seconds (çok hızlı)
LONG_SCROLL_DELAY = 1  # seconds (çok hızlı)

# Chrome options (ULTRA MINIMAL - FREE TIER 512MB)
# Başka projelerde çalışan minimal konfigürasyon
CHROME_OPTIONS = [
    "--headless",  # Old headless (daha stabil)
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-extensions",
    "--disable-blink-features=AutomationControlled",
    "--remote-debugging-port=9222",  # Remote debugging
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--disable-dev-tools",
    "--single-process",
    "--window-size=800,600",
    "--user-data-dir=/tmp/chrome-user-data",  # Temporary user data
    "--data-path=/tmp/chrome-data",
    "--disk-cache-dir=/tmp/chrome-cache",
    "--disable-application-cache",
    "--disable-session-crashed-bubble",
    "--disable-infobars",
    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# XPath selectors
COMMENT_XPATH = "//a[starts-with(@href,'/p/') and contains(@href,'/c/')]/ancestor::div[1]/following-sibling::div//span[@dir='auto'][1]"
USERNAME_XPATH = "//span[@class='_ap3a _aaco _aacw _aacx _aad7 _aade']"
LOGIN_BUTTON_XPATH = "//div[@role='button' and contains(text(), 'Giriş yap')]"
NOT_NOW_BUTTON_XPATH = "//div[@role='button' and contains(text(), 'Şimdi değil')]"