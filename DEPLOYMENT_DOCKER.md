# 🐳 Docker ile Render Deployment (Instagram Scraping Desteği)

Bu projeyi Instagram scraping özelliği ile birlikte deploy etmek için Docker kullanıyoruz.

## 📋 Neden Docker?

Instagram scraping için Selenium ve Chrome gerekiyor. Render'ın normal Python environment'ında Chrome kurulu değil. Docker sayesinde:

✅ Chrome tarayıcısı kurulu
✅ ChromeDriver otomatik yönetiliyor
✅ Selenium tam çalışıyor
✅ Instagram URL analizi çalışıyor

## 🚀 Deployment Adımları

### 1. Kodu GitHub'a Push Edin

```bash
git add .
git commit -m "Docker deployment - Instagram scraping enabled"
git push origin main
```

### 2. Render'da Blueprint Oluşturun

1. [Render Dashboard](https://dashboard.render.com)
2. **New** → **Blueprint**
3. GitHub repository'nizi seçin
4. `render.yaml` otomatik algılanacak
5. **Create Blueprint**

### 3. Environment Variables Ekleyin

Blueprint oluştuktan sonra **Backend** servisine gidin:

```
Dashboard → cyberbullying-backend → Environment
```

Eklenecek değerler:

```
GOOGLE_API_KEY=your_gemini_api_key_here
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
ENVIRONMENT=production
FRONTEND_URL=https://cyberbullying-frontend.onrender.com
```

### 4. Frontend URL'i Güncelleyin

**Frontend** servisine gidin:

```
Dashboard → cyberbullying-frontend → Environment
```

```
REACT_APP_API_URL=https://cyberbullying-backend.onrender.com
```

> **Not**: URL'leri kendi Render servis isimlerinize göre değiştirin.

## 📦 Docker Build Süreci

Render otomatik olarak:

1. `Dockerfile`'ı kullanarak image oluşturur
2. Python 3.11.9 kurulur
3. Chrome ve sistem bağımlılıkları kurulur
4. Python paketleri yüklenir
5. Uygulama başlatılır

**Build süresi**: İlk build ~5-10 dakika sürebilir (Chrome indirmesi nedeniyle)

## ⚙️ Dockerfile Özellikleri

- **Base Image**: `python:3.11.9-slim`
- **Chrome**: Stable versiyonu
- **ChromeDriver**: webdriver-manager ile otomatik
- **Port**: 8000
- **Health Check**: `/api/health`

## 🔍 Deployment Kontrolü

### Backend Logları

```
Dashboard → cyberbullying-backend → Logs
```

Görmek istediğiniz:

```
Starting application...
Initializing database...
✅ Database connection successful!
✅ All tables created successfully!
✅ Loaded X training examples from ...
✅ Gemini 2.0 Flash API configured
INFO: Application startup complete
```

### Health Check

Backend URL'inize gidin:

```
https://your-backend.onrender.com/api/health
```

Başarılı yanıt:

```json
{
  "status": "healthy",
  "model": "gemini-2.0-flash-exp"
}
```

## 🎯 Özellik Durumu

Tüm özellikler çalışacak:

- ✅ Kullanıcı kayıt/giriş
- ✅ Tek yorum tahmini
- ✅ Toplu yorum tahmini
- ✅ CSV dosyası yükleme
- ✅ **Instagram URL analizi** (Selenium ile)
- ✅ Gemini AI tahminleri

## 🐛 Sorun Giderme

### Docker Build Failed

**Hata**: Chrome kurulum hatası

**Çözüm**: Dockerfile'daki apt paketlerini kontrol edin, gerekirse güncelle:

```dockerfile
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*
```

### Selenium Hataları

**Hata**: ChromeDriver bulunamıyor

**Çözüm**: webdriver-manager environment variables:

```
WDM_LOG_LEVEL=0
WDM_LOCAL=1
```

Bu değerler Dockerfile'da zaten ayarlı.

### Memory Limit

**Hata**: Out of memory (OOM)

**Sebep**: Free tier 512MB RAM ile sınırlı, Chrome fazla RAM kullanıyor.

**Çözüm**:
1. Chrome headless options ekleyin (zaten `config/settings.py`'de var)
2. Paid plan'e geçin (daha fazla RAM)

## 💡 Optimizasyon İpuçları

### Build Cache

Docker layer caching kullanılıyor. Kod değişikliklerinde sadece son katmanlar rebuild edilir.

### Image Boyutu

- Base: `python:3.11.9-slim` (küçük image)
- Chrome: ~200-300 MB
- Dependencies: ~500 MB
- **Toplam**: ~1 GB civarı

### Startup Süresi

- **İlk request**: 30-60 saniye (free tier - cold start)
- **Sonraki istekler**: Hızlı
- **15 dakika hareketsizlik sonrası**: Tekrar cold start

## 📊 Free Tier Limitler

- **RAM**: 512 MB (Chrome ile sınırda)
- **CPU**: Shared
- **Disk**: Geçici (container restart'ta kaybolur)
- **Sleep**: 15 dakika hareketsizlik sonrası
- **Build süresi**: Unlimited (ama yavaş olabilir)

## 🔄 Güncelleme

Kod değişikliği sonrası:

```bash
git add .
git commit -m "Update feature"
git push origin main

# Render otomatik deploy eder
```

Manuel deploy:

```
Dashboard → Service → Manual Deploy → Deploy latest commit
```

## ⚠️ Önemli Notlar

1. **Instagram Login**: Render IP'si her deploy'da değişebilir, Instagram güvenlik nedeniyle login engelleyebilir
2. **Rate Limiting**: Instagram çok fazla istek yaparsanız geçici ban atabilir
3. **Chrome Memory**: Free tier'da Chrome kullanımı zorlanabilir, çökme olabilir
4. **Build Time**: İlk build uzun sürer, sonrakiler hızlıdır

## 🆘 Yardım

Sorun yaşarsanız:

1. Logs'u kontrol edin
2. Health check yapın
3. Environment variables'ları doğrulayın
4. Local'de Docker ile test edin:

```bash
docker build -t cyberbullying-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL="your_db_url" \
  -e GOOGLE_API_KEY="your_key" \
  cyberbullying-backend
```

---

**Başarılar! 🎉**

Instagram scraping artık production'da çalışıyor!

