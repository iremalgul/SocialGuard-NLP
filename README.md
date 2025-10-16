# 🛡️ SocialGuard Pro - Sosyal Medya Analiz Platformu

AI destekli sosyal medya analiz platformu. Instagram yorumlarını analiz eder, zararlı içerikleri tespit eder ve kullanıcı davranışlarını değerlendirir.

**Stack:** React • FastAPI • PostgreSQL • Google Gemini 2.0 Flash • Selenium

## ✨ Özellikler

- 🤖 **AI Analiz** - Google Gemini 2.0 Flash ile anlık metin analizi
- 📱 **Instagram Scraping** - Selenium ile otomatik yorum çekme
- 🔐 **Güvenli Sistem** - JWT authentication + bcrypt şifreleme
- 📊 **Görselleştirme** - Grafikler, istatistikler, detaylı raporlar
- 💾 **Veritabanı** - PostgreSQL ile güvenli veri saklama
- 🎯 **5 Kategori** - Zararsız, Hakaret, Cinsiyetçi, Alaycı, Görünüm Eleştirisi

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
│   └── package.json
│
├── config/                    # Shared configuration
├── database/                  # Database models & utils
├── scrapers/                  # Instagram scraper
├── data/                      # Training data (2,147 labeled comments)
│
├── Dockerfile                 # Docker configuration
└── render.yaml               # Render deployment config
```

---

## 🚀 Hızlı Kurulum

### Gereksinimler
- Python 3.11+ • Node.js 16+ • PostgreSQL 12+ • Google Gemini API Key

### 1. Veritabanı Oluştur
```bash
psql -U postgres -c "CREATE DATABASE cyberbullying_db;"
```

### 2. Environment Variables
Proje root'unda `.env` dosyası oluşturun:
```env
DATABASE_PASSWORD=your_postgres_password
GOOGLE_API_KEY=your_gemini_api_key
INSTAGRAM_USERNAME=your_instagram_username  # opsiyonel
INSTAGRAM_PASSWORD=your_instagram_password  # opsiyonel
```

**Gemini API Key:** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 3. Kurulum
```bash
# Backend
pip install -r backend/requirements.txt
python database/init_db.py

# Frontend
cd frontend && npm install && cd ..
```

### 4. Çalıştır

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm start
```

- 🌐 **Frontend:** http://localhost:3000
- 🔗 **Backend:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

---

## 📱 Kullanım

### Sosyal Medya Analizi
1. Instagram post URL'sini girin
2. Yorum sayısı ve tespit eşiğini ayarlayın
3. "Analiz Et" butonuna tıklayın
4. Sonuçları inceleyin (grafikler, kullanıcı analizi, yorum detayları)

### Manuel Analiz
- **Tekli Yorum** - Tek bir yorumu kategorize edin
- **Toplu Analiz** - Birden fazla yorumu aynı anda analiz edin
- **Veri Seti** - CSV yükleyin, AI etiketlesin, JSON indirin

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

## 🔌 API Endpoints

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

**Tam dokümantasyon:** http://localhost:8000/docs

---

## 🌐 Production Deployment (Render)

### Otomatik Deployment
```bash
# 1. Git push
git add .
git commit -m "Update"
git push origin main

# 2. Render Dashboard
New → Blueprint → Repository seçin
render.yaml otomatik algılanır
```

### Environment Variables (Render Dashboard)

**Backend Servisi:**
```
GOOGLE_API_KEY=your_gemini_api_key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
FRONTEND_URL=https://your-frontend-url.onrender.com
```

**Frontend Servisi:**
```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

### Deployment Notları
- ✅ `backend/requirements.txt` ve `backend/runtime.txt` mevcut olmalı
- ✅ Backend `env: docker` kullanır (Selenium + Chrome dahil)
- ✅ Frontend `env: node` kullanır (Python kurulumu YOK)
- ✅ Blueprint ile tüm servisler otomatik oluşturulur
- ✅ Database otomatik oluşturulur (PostgreSQL 15)
- ✅ Her deploy sonrası otomatik yeniden başlar

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

## 🐛 Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| **PostgreSQL Hatası** | `.env` dosyasında `DATABASE_PASSWORD` kontrol edin |
| **Gemini API Hatası** | API key kontrol edin: https://aistudio.google.com/app/apikey |
| **ModuleNotFoundError** | `pip install -r backend/requirements.txt --upgrade` |
| **Port Hatası** | `PORT=3001 npm start` ile farklı port kullanın |
| **Scraping Çalışmıyor** | Instagram credentials kontrol edin (.env) |
| **Import Hatası** | Backend `backend.main:app` şeklinde import edilmeli |

---

## 📝 Hızlı Başlangıç

```bash
# 1. Klonlayın
git clone https://github.com/your-repo/SocialGuard-NLP.git
cd SocialGuard-NLP

# 2. .env dosyası oluşturun

# 3. Database
psql -U postgres -c "CREATE DATABASE cyberbullying_db;"

# 4. Kurulum
pip install -r backend/requirements.txt
python database/init_db.py
cd frontend && npm install && cd ..

# 5. Başlatın (2 terminal)
# Terminal 1: uvicorn backend.main:app --reload --port 8000
# Terminal 2: cd frontend && npm start
```

**http://localhost:3000** → Register → Instagram URL analiz edin! 🚀

---

## ⚠️ Notlar

- Backend + Frontend + PostgreSQL birlikte çalışmalı
- Gemini API key zorunlu
- Instagram scraping için login credentials önerilir
- Production'da Docker kullanılır (Selenium + Chrome dahil)

**İyi kullanımlar!** 🛡️

---

**Versiyon:** 2.1.0 | **Güncelleme:** 2024-10-16 | **Geliştirici:** SocialGuard Pro Team
