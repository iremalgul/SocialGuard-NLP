# 🔐 Environment Variables Referansı

Bu dokümanda projenin ihtiyaç duyduğu tüm environment variables açıklanmaktadır.

## 📋 Backend Environment Variables

Backend servisiniz için (FastAPI) şu environment variables'ları ayarlamanız gerekir:

### Zorunlu Variables

| Variable | Açıklama | Örnek Değer |
|----------|----------|-------------|
| `DATABASE_URL` | PostgreSQL bağlantı URL'i (Render otomatik sağlar) | `postgresql://user:pass@host:5432/db` |
| `GOOGLE_API_KEY` | Google Gemini API anahtarı | `AIzaSy...` |
| `SECRET_KEY` | JWT token için gizli anahtar | `your-super-secret-key-here` |
| `INSTAGRAM_USERNAME` | Instagram giriş kullanıcı adı | `your_username` |
| `INSTAGRAM_PASSWORD` | Instagram giriş şifresi | `your_password` |
| `FRONTEND_URL` | Frontend'in production URL'i (CORS için) | `https://yourapp-frontend.onrender.com` |

### Opsiyonel Variables

| Variable | Açıklama | Default Değer |
|----------|----------|---------------|
| `ENVIRONMENT` | Çalışma ortamı | `development` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token geçerlilik süresi (dakika) | `10080` (7 gün) |

### Local Development için

Local'de çalışırken `.env` dosyası oluşturun:

```bash
# .env dosyası
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=cyberbullying_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_local_password

GOOGLE_API_KEY=your_gemini_api_key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

SECRET_KEY=local-development-secret-key
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

---

## 🎨 Frontend Environment Variables

Frontend için (React) şu environment variables'ı ayarlamanız gerekir:

### Production

| Variable | Açıklama | Örnek Değer |
|----------|----------|-------------|
| `REACT_APP_API_URL` | Backend API'nin base URL'i | `https://yourapp-backend.onrender.com` |

### Local Development

Frontend klasöründe `.env.local` dosyası oluşturun:

```bash
# frontend/.env.local
REACT_APP_API_URL=http://localhost:8000
```

---

## 🚀 Render'da Environment Variables Nasıl Ayarlanır

### Yöntem 1: Web Interface

1. Render Dashboard'a gidin
2. Servisinizi seçin (Backend veya Frontend)
3. Sol menüden **"Environment"** tıklayın
4. **"Add Environment Variable"** ile yeni variable ekleyin
5. **"Save Changes"** tıklayın (servis otomatik restart olur)

### Yöntem 2: render.yaml

`render.yaml` dosyasında tanımlayın:

```yaml
services:
  - type: web
    name: my-backend
    envVars:
      - key: GOOGLE_API_KEY
        sync: false  # Manuel girilecek
      - key: ENVIRONMENT
        value: production  # Sabit değer
      - key: DATABASE_URL
        fromDatabase:
          name: my-database
          property: connectionString  # Otomatik database'den alınır
```

---

## 🔒 Güvenlik İpuçları

### ⚠️ YAPMAYIN
- API keys'i asla GitHub'a push etmeyin
- `.env` dosyasını commit etmeyin (`.gitignore`'da olmalı)
- Secret key'leri kod içinde hardcode etmeyin

### ✅ YAPIN
- Güçlü ve benzersiz `SECRET_KEY` kullanın
- Production'da `ENVIRONMENT=production` ayarlayın
- API keys'i sadece Render Environment Variables'da saklayın
- Instagram credentials'ı güvenli tutun

---

## 🧪 Environment Variables Test

Backend'i çalıştırıp test edin:

```bash
# Local test:
python -c "from config.settings import DATABASE_URL, SECRET_KEY; print('DB:', DATABASE_URL); print('SECRET:', SECRET_KEY[:10] + '...')"

# API health check:
curl https://your-backend.onrender.com/api/health
```

Frontend'i test edin:

```bash
# Build sırasında:
npm run build
# Console'da REACT_APP_API_URL değerini göreceksiniz
```

---

## 🔄 Variables Güncelleme

### Render'da Güncelleme
1. Dashboard → Service → Environment
2. Variable'ı bulun ve **"Edit"** tıklayın
3. Yeni değeri girin ve **"Save Changes"**
4. Servis otomatik restart olur

### Local'de Güncelleme
1. `.env` dosyasını düzenleyin
2. Servisi restart edin:
   ```bash
   # Backend:
   # Ctrl+C ile durdurun, sonra:
   uvicorn main:app --reload
   
   # Frontend:
   # Ctrl+C ile durdurun, sonra:
   npm start
   ```

---

## 📊 Variables Öncelik Sırası

Environment variables şu sırayla okunur:

1. **Sistem environment variables** (en yüksek öncelik)
2. **Render Environment tab'ından** ayarlananlar
3. **render.yaml'da** tanımlananlar
4. **Kod içinde default** değerler (en düşük öncelik)

Örnek:
```python
# config/settings.py
DATABASE_URL = os.getenv("DATABASE_URL")  # Önce sistem env'den bakılır
if not DATABASE_URL:
    # Bulunamazsa parçalardan oluşturulur
    DATABASE_URL = f"postgresql://{DATABASE_USER}:..."
```

---

## 🎯 Variable Naming Conventions

### Backend (Python/FastAPI)
```bash
DATABASE_URL          # Büyük harf, underscore
SECRET_KEY
GOOGLE_API_KEY
```

### Frontend (React)
```bash
REACT_APP_API_URL     # REACT_APP_ prefix zorunlu
REACT_APP_ENV
```

> **Not**: React'te sadece `REACT_APP_` ile başlayan variables build'e dahil edilir!

---

## 🐛 Yaygın Hatalar

### Hata: "SECRET_KEY must be set in production"
```bash
# Çözüm:
Dashboard → Backend → Environment → Add:
SECRET_KEY=your-generated-secret-key-here
```

### Hata: "DATABASE_URL not found"
```bash
# Çözüm 1: Render PostgreSQL kullanıyorsanız
Dashboard → Backend → Environment → Add:
DATABASE_URL=${{postgres.DATABASE_URL}}

# Çözüm 2: External database kullanıyorsanız
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Hata: Frontend API'ye bağlanamıyor
```bash
# Çözüm:
Dashboard → Frontend → Environment → Check:
REACT_APP_API_URL=https://your-backend.onrender.com

# Rebuild edin (environment değişirse rebuild gerekir):
Dashboard → Frontend → Manual Deploy → Clear build cache & deploy
```

### Hata: CORS Error
```bash
# Backend'de FRONTEND_URL doğru mu kontrol edin:
Dashboard → Backend → Environment → Check:
FRONTEND_URL=https://your-frontend.onrender.com

# Emin değilseniz her ikisini de ekleyin:
FRONTEND_URL=https://your-frontend.onrender.com,https://www.your-custom-domain.com
```

---

## 📞 Yardım

Daha fazla bilgi için:
- [Render Environment Variables Docs](https://render.com/docs/environment-variables)
- [React Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)

