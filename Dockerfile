# Render için Dockerfile - Chrome ve Selenium desteği ile

FROM python:3.11.9-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını kur (Chrome için)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome kurulumu
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver'ın otomatik indirilmesini sağla (webdriver-manager kullanacak)
ENV WDM_LOG_LEVEL=0
ENV WDM_LOCAL=1

# Python bağımlılıklarını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Port tanımla
ENV PORT=8000
EXPOSE 8000

# Startup script oluştur
RUN echo '#!/bin/bash\n\
echo "Starting application..."\n\
echo "Initializing database..."\n\
python database/init_db.py || echo "Database already initialized or will initialize on first request"\n\
echo "Starting FastAPI server..."\n\
uvicorn main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Startup script ile başlat
CMD ["/app/start.sh"]

