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

# Scraping settings (Free tier için optimize - düşük memory)
DEFAULT_MAX_COMMENTS = 50  # Free tier için daha az yorum (memory limit)
SCROLL_TIMEOUT = 60  # 1 minute (daha kısa timeout)
SCROLL_DELAY = 2  # seconds (hızlandırıldı)
LONG_SCROLL_DELAY = 3  # seconds after 3rd scroll (hızlandırıldı)

# Chrome options (ULTRA MINIMAL - 512MB RAM için)
CHROME_OPTIONS = [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-extensions",
    "--disable-blink-features=AutomationControlled",
    "--window-size=800,600",  # Çok küçük pencere (minimum memory)
    "--single-process",
    "--disable-dev-tools",
    "--no-zygote",
    "--disable-setuid-sandbox",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-breakpad",
    "--disable-component-extensions-with-background-pages",
    "--disable-features=TranslateUI,BlinkGenPropertyTrees,AudioServiceOutOfProcess,IsolateOrigins,site-per-process",
    "--disable-ipc-flooding-protection",
    "--disable-renderer-backgrounding",
    "--enable-features=NetworkService,NetworkServiceInProcess",
    "--force-color-profile=srgb",
    "--hide-scrollbars",
    "--metrics-recording-only",
    "--mute-audio",
    "--disable-logging",
    "--disable-permissions-api",
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--js-flags=--max-old-space-size=256",  # JavaScript heap limit
    "--disable-accelerated-2d-canvas",
    "--disable-accelerated-jpeg-decoding",
    "--disable-accelerated-mjpeg-decode",
    "--disable-accelerated-video-decode",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# XPath selectors
COMMENT_XPATH = "//a[starts-with(@href,'/p/') and contains(@href,'/c/')]/ancestor::div[1]/following-sibling::div//span[@dir='auto'][1]"
USERNAME_XPATH = "//span[@class='_ap3a _aaco _aacw _aacx _aad7 _aade']"
LOGIN_BUTTON_XPATH = "//div[@role='button' and contains(text(), 'Giriş yap')]"
NOT_NOW_BUTTON_XPATH = "//div[@role='button' and contains(text(), 'Şimdi değil')]"