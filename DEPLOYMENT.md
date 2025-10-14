# 🚀 Render'da Deployment Talimatları

Bu dokümanda projenizi Render.com platformunda nasıl canlıya alacağınızı adım adım açıklıyoruz.

## 📋 Ön Hazırlık

### 1. Gerekli Hesaplar
- GitHub hesabı (projenizi push etmiş olun)
- Render.com hesabı ([render.com](https://render.com) - ücretsiz hesap yeterli)
- Google Cloud hesabı (Gemini API key için)

### 2. API Keys'i Hazırlayın
Aşağıdaki bilgileri hazır bulundurun:
- **Gemini API Key**: Google AI Studio'dan ([aistudio.google.com](https://aistudio.google.com))
- **Instagram Credentials**: Instagram kullanıcı adı ve şifreniz

---

## 🎯 Yöntem 1: Render Blueprint ile Otomatik Deployment (Önerilen)

Bu yöntem tüm servisleri (Database + Backend + Frontend) tek seferde oluşturur.

### Adım 1: Projeyi GitHub'a Push Edin

```bash
git add .
git commit -m "Production ready"
git push origin main
```

### Adım 2: Render'da Blueprint Oluşturun

1. [Render Dashboard](https://dashboard.render.com)'a gidin
2. **"New"** → **"Blueprint"** seçin
3. GitHub repository'nizi bağlayın
4. `render.yaml` dosyası otomatik algılanacak

### Adım 3: Environment Variables'ları Ayarlayın

Blueprint oluşturduktan sonra manuel olarak şu değerleri girin:

#### Backend Servisi için:
```
GOOGLE_API_KEY=your_gemini_api_key_here
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
ENVIRONMENT=production
FRONTEND_URL=https://cyberbullying-frontend.onrender.com
```

#### Frontend Servisi için:
```
REACT_APP_API_URL=https://cyberbullying-backend.onrender.com
```

> **Not**: Frontend ve Backend URL'lerini kendi Render servis isimlerinize göre güncelleyin.

### Adım 4: Deploy Edin

- **"Create Blueprint"** butonuna tıklayın
- Render otomatik olarak şunları oluşturacak:
  - PostgreSQL Database
  - Backend Web Service (FastAPI)
  - Frontend Static Site (React)

---

## 🔧 Yöntem 2: Manuel Deployment

Her servisi tek tek oluşturmak isterseniz:

### 1️⃣ PostgreSQL Database

1. Dashboard → **"New"** → **"PostgreSQL"**
2. Ayarlar:
   - **Name**: `cyberbullying-db`
   - **Region**: Frankfurt (veya size en yakın)
   - **Plan**: Starter (Ücretsiz)
3. **"Create Database"** tıklayın
4. Database oluştuktan sonra **Internal Database URL**'i kopyalayın

### 2️⃣ Backend (FastAPI)

1. Dashboard → **"New"** → **"Web Service"**
2. GitHub repository'nizi seçin
3. Ayarlar:
   ```
   Name: cyberbullying-backend
   Region: Frankfurt
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables** ekleyin:
   ```
   DATABASE_URL=[PostgreSQL Internal URL - Adım 1'den]
   GOOGLE_API_KEY=your_gemini_api_key_here
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   SECRET_KEY=[otomatik generate edilecek - "Generate" butonuna tıklayın]
   ENVIRONMENT=production
   FRONTEND_URL=https://cyberbullying-frontend.onrender.com
   ```

5. **Health Check Path**: `/api/health`
6. **"Create Web Service"** tıklayın

### 3️⃣ Frontend (React)

1. Dashboard → **"New"** → **"Static Site"**
2. GitHub repository'nizi seçin
3. Ayarlar:
   ```
   Name: cyberbullying-frontend
   Region: Frankfurt
   Branch: main
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/build
   ```

4. **Environment Variables** ekleyin:
   ```
   REACT_APP_API_URL=https://cyberbullying-backend.onrender.com
   ```
   > **Not**: Backend URL'inizi kendi Render servis URL'inize göre güncelleyin.

5. **"Create Static Site"** tıklayın

---

## 🔍 Deployment Sonrası Kontroller

### 1. Backend Kontrolü
Backend URL'inize gidin: `https://cyberbullying-backend.onrender.com/api/health`

Başarılı yanıt:
```json
{
  "status": "healthy",
  "model": "gemini-2.0-flash-exp"
}
```

### 2. Frontend Kontrolü
Frontend URL'inize gidin: `https://cyberbullying-frontend.onrender.com`

- Login sayfası açılmalı
- Register yapıp giriş yapabilmelisiniz

### 3. Database Kontrolü
Backend loglarını kontrol edin:
```
Render Dashboard → Backend Service → Logs
```

Görmek istediğiniz:
```
✅ Loaded X training examples from ...
✅ Gemini 2.0 Flash API configured
```

---

## ⚙️ Önemli Notlar

### Free Tier Limitasyonları
Render'ın ücretsiz planında:
- Web Service 15 dakika hareketsizlik sonrası uyur (ilk istek 30-60 saniye sürebilir)
- PostgreSQL 90 gün sonra silinir (aktif kullanımda problem olmaz)
- Aylık 750 saat ücretsiz kullanım

### Production İyileştirmeleri

1. **Database Backup**: 
   - Render Dashboard → Database → Settings → Backups
   - Otomatik backup'ları etkinleştirin

2. **Custom Domain** (Opsiyonel):
   - Frontend ve Backend için custom domain ekleyebilirsiniz
   - Settings → Custom Domains

3. **CORS Güvenliği**:
   - `main.py`'de `FRONTEND_URL` environment variable'ı doğru ayarlandığından emin olun

4. **Rate Limiting**: 
   - Yüksek trafikte API rate limiting ekleyin

---

## 🐛 Sorun Giderme

### Backend Çalışmıyor
```bash
# Render logs'u kontrol edin:
Dashboard → Backend Service → Logs

# Yaygın hatalar:
- DATABASE_URL eksik → Environment Variables kontrol edin
- GOOGLE_API_KEY geçersiz → API key'i kontrol edin
- Port hatası → Start command'de $PORT kullanıldığından emin olun
```

### Frontend API'ye Bağlanamıyor
```bash
# Browser console'da:
- CORS hatası → Backend FRONTEND_URL doğru mu?
- 404 hatası → REACT_APP_API_URL doğru mu?

# Environment variables'ı kontrol edin:
Dashboard → Frontend → Environment → REACT_APP_API_URL
```

### Database Connection Error
```bash
# Database URL formatını kontrol edin:
postgresql://user:password@host:port/dbname

# Internal Database URL kullanın (External değil)
Dashboard → Database → Internal Database URL
```

### Instagram Scraper Çalışmıyor
```bash
# Render'da Chrome kurulu olmayabilir
# Gerekirse Dockerfile ekleyin veya başka bir hosting kullanın
# Alternatif: Instagram scraping için ayrı bir worker servisi
```

---

## 📊 Monitoring ve Loglar

### Log Takibi
```bash
# Real-time logs:
Dashboard → Service → Logs (en altta "Auto Scroll" aktif edin)

# Hata ayıklama:
print() statements backend'de log olarak görünür
```

### Metrics
```bash
Dashboard → Service → Metrics
- CPU kullanımı
- Memory kullanımı
- Request sayısı
```

---

## 🔄 Güncelleme ve Yeniden Deploy

### Kod Değişikliği Sonrası
```bash
# GitHub'a push edin:
git add .
git commit -m "Update feature"
git push origin main

# Render otomatik deploy eder (Auto-Deploy açıksa)
# Veya manuel: Dashboard → Service → Manual Deploy → Deploy latest commit
```

### Environment Variables Değiştirme
```bash
Dashboard → Service → Environment → Edit
# Değişiklik yaptıktan sonra servis otomatik restart olur
```

---

## 📞 Destek ve Kaynaklar

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React Deployment**: [create-react-app.dev/docs/deployment](https://create-react-app.dev/docs/deployment)

---

## ✅ Checklist

Deployment tamamlandığında kontrol edin:

- [ ] Backend health check çalışıyor
- [ ] Frontend açılıyor ve login sayfası görünüyor
- [ ] Register ve login çalışıyor
- [ ] Manuel analiz çalışıyor (tek yorum tahmini)
- [ ] Sosyal medya analizi çalışıyor
- [ ] Database'e kayıtlar düşüyor (Profile sayfasından kontrol edin)
- [ ] Environment variables hepsi doğru ayarlı
- [ ] CORS hataları yok
- [ ] Loglar temiz, hata yok

---

**Başarılar! 🎉**

Sorularınız için: [Render Community](https://community.render.com)

