# 🛡️ SocialGuard Pro - Sosyal Medya Analiz Platformu

AI destekli sosyal medya analiz platformu. Instagram yorumlarını analiz eder, zararlı içerikleri tespit eder ve kullanıcı davranışlarını değerlendirir.

**Teknolojiler:** React + FastAPI + PostgreSQL + Google Gemini 2.0 Flash + Selenium

---

## ✨ Özellikler

- 🤖 **AI Analiz**: Google Gemini 2.0 Flash ile hızlı metin analizi
- 📱 **Instagram Scraping**: Selenium ile yorum çekme ve analiz
- 🔐 **Güvenli Sistem**: JWT authentication, bcrypt şifreleme
- 📊 **Görselleştirme**: Grafikler, istatistikler, detaylı raporlar
- 💾 **Veritabanı**: PostgreSQL ile güvenli veri saklama
- 🎯 **5 Kategori**: Zararsız, Hakaret, Cinsiyetçi, Alaycı, Görünüm Eleştirisi

---

## 📁 Proje Yapısı

```
IBM/
├── backend/                   # Backend API
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic models
│   ├── utils.py              # Utility functions
│   ├── few_shot/             # Few-shot learning model
│   ├── requirements.txt      # Python dependencies
│   └── runtime.txt           # Python version
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── pages/            # Ana sayfalar
│   │   ├── components/       # Bileşenler
│   │   └── context/          # AuthContext
│   └── package.json          # npm dependencies
│
├── config/                    # Shared configuration
│   ├── __init__.py           # API keys, label maps
│   └── settings.py           # Database, Instagram config
│
├── database/                  # Database models & utils
│   ├── database.py           # SQLAlchemy setup
│   ├── db_models.py          # User, Analysis, Prediction models
│   ├── auth_utils.py         # JWT, password hashing
│   └── init_db.py            # Database initialization
│
├── scrapers/                  # Instagram scraper
│   └── instagram_comments_scraper.py
│
├── data/                      # Training data
│   └── dataset.csv           # 2,147 labeled Turkish comments
│
├── Dockerfile                 # Docker configuration
└── render.yaml               # Render deployment config
```

---

## 🚀 Hızlı Kurulum (Local)

### Gereksinimler
- Python 3.11+
- Node.js 16+
- PostgreSQL 12+
- Google Gemini API Key

### 1️⃣ Veritabanı Kurulumu

```bash
# PostgreSQL'de database oluşturun
psql -U postgres
CREATE DATABASE cyberbullying_db;
\q
```

**config/settings.py** dosyasında database ayarlarını güncelleyin (veya .env kullanın).

### 2️⃣ Backend Kurulumu

```bash
# Python paketlerini yükleyin
pip install -r backend/requirements.txt

# Database tablolarını oluşturun
python database/init_db.py
```

**Gemini API Key**: `config/__init__.py` dosyasında API key'inizi güncelleyin veya environment variable kullanın:
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```
- API Key alma: https://aistudio.google.com/app/apikey

### 3️⃣ Frontend Kurulumu

```bash
cd frontend
npm install
cd ..
```

---

## 🎯 Kullanım

### Backend Başlatma
```bash
uvicorn backend.main:app --reload --port 8000
```
Backend: `http://localhost:8000` | API Docs: `http://localhost:8000/docs`

### Frontend Başlatma (Yeni terminal)
```bash
cd frontend
npm start
```
Frontend: `http://localhost:3000`

### İlk Kullanıcı
Register sayfasından yeni hesap oluşturun ve giriş yapın.

---

## 📱 Temel Kullanım

### Sosyal Medya Analizi (Ana Sayfa)
1. Instagram post URL'si girin
2. Yorum sayısı ve tespit eşiğini ayarlayın (%0-100)
3. "Analiz Et" butonuna tıklayın
4. Sonuçları inceleyin: Grafikler, kullanıcı analizi, yorum detayları

### Manuel Analiz
- **Tekli Yorum**: Tek bir yorumu kategorize edin
- **Toplu Analiz**: Birden fazla yorumu aynı anda analiz edin
- **Veri Seti**: CSV yükleyin, AI etiketlesin, JSON indirin

### Profil Sayfası
- Analiz geçmişinizi görüntüleyin
- İstatistiklerinizi inceleyin
- Eski analizleri silin veya detaylandırın

---

## 🎯 Kategori Sistemi

| ID | Kategori | Açıklama |
|----|----------|----------|
| 0 | Zararsız / Nötr | Normal, olumlu yorumlar |
| 1 | Doğrudan Hakaret | Açık hakaret ve küfür |
| 2 | Cinsiyetçi / Cinsel | Cinsiyet ayrımcılığı |
| 3 | Alaycılık | İma yoluyla rahatsız edici |
| 4 | Görünüm Eleştirisi | Fiziksel görünüm eleştirisi |

**Risk Kategorileri:**
- 🔴 Yüksek Risk: %30+ zararlı
- 🟠 Orta Risk: %10-30 zararlı
- 🟡 Düşük Risk: %5-10 zararlı
- 🟢 Güvenli: %5'ten az zararlı

---

## 🔌 API Endpoints (Özet)

### Authentication
- `POST /api/auth/register` - Kayıt ol
- `POST /api/auth/login` - Giriş yap
- `GET /api/auth/me` - Kullanıcı bilgisi

### Analiz
- `POST /api/social-media-analysis` - Instagram analizi
- `POST /api/predict` - Tekli yorum tahmini
- `POST /api/batch-predict` - Toplu tahmin
- `POST /api/upload-dataset` - CSV yükle ve etiketle

### Geçmiş
- `GET /api/analyses/history` - Analiz geçmişi
- `GET /api/manual-predictions/history` - Manuel tahmin geçmişi
- `GET /api/analyses/stats/summary` - İstatistikler

**Tam API dokümantasyonu:** `http://localhost:8000/docs`

---

## 🌐 Production Deployment (Render)

Render.com platformunda canlıya almak için:

1. Tüm deployment talimatları → **[DEPLOYMENT_NOTES.md](./DEPLOYMENT_NOTES.md)**
2. Blueprint ile tek seferde deploy
3. Environment variables ayarlayın
4. Frontend ve Backend otomatik çalışacak!

**Not:** Instagram scraping Docker container'da çalışır (Chrome + Selenium dahil).

---

## 🔧 Teknoloji Stack

**Backend:**
- FastAPI - Web framework
- PostgreSQL + SQLAlchemy - Database
- Google Gemini 2.0 Flash - AI model
- Selenium - Web scraping
- Scikit-learn - TF-IDF similarity
- Docker - Containerization

**Frontend:**
- React 18 - UI library
- React Router - Navigation
- Bootstrap 5 - CSS framework
- Chart.js - Grafikler
- Axios - HTTP client

**Security:**
- JWT - Authentication
- Bcrypt - Password hashing
- Protected Routes - Authorization

---

## 📊 Veri Seti

- **2,147 etiketlenmiş Türkçe yorum**
- **5 kategori** dengeli dağılım
- **Few-shot learning** için optimize edilmiş

---

## 🐛 Sorun Giderme

### PostgreSQL Bağlantı Hatası
```bash
# Servis çalışıyor mu?
Get-Service -Name postgresql*

# Şifre ve ayarları kontrol edin
config/settings.py
```

### Python Modül Hatası
```bash
pip install -r backend/requirements.txt --upgrade
```

### Gemini API Hatası
- API key'i kontrol edin: Environment variable `GOOGLE_API_KEY`
- Yeni key alın: https://aistudio.google.com/app/apikey

### Frontend Port Hatası
```bash
# Farklı port kullanın
PORT=3001 npm start
```

### Scraping Çalışmıyor
- Chrome browser güncel olmalı
- Internet bağlantısı aktif olmalı
- Instagram login credentials gerekebilir (config/settings.py)

---

## 📝 Örnek Kullanım

### Terminal 1: Backend
```bash
uvicorn backend.main:app --reload --port 8000
# ✅ Backend: http://localhost:8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm start
# ✅ Frontend: http://localhost:3000
```

### Tarayıcı
1. `http://localhost:3000` açın
2. Register sayfasından yeni hesap oluşturun
3. Instagram URL girin: `https://www.instagram.com/p/DPErH0FDHom/`
4. Analiz Et!

---

## 🎉 Notlar

- ⚠️ Backend ve Frontend her ikisi de açık olmalı
- ⚠️ PostgreSQL servisi çalışır durumda olmalı
- ⚠️ Gemini API key geçerli olmalı
- ⚠️ Internet bağlantısı aktif olmalı (scraping için)

**İyi kullanımlar!** 🚀

---

**Versiyon:** 2.0.0  
**Son Güncelleme:** 2025-10-14  
**Geliştirici:** SocialGuard Pro Team
