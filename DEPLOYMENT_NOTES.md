# 🚀 Render Blueprint Deployment - Final Yapılandırma

## 📁 Yeni Proje Yapısı

```
IBM/
├── backend/                    # Backend kodları
│   ├── main.py                # FastAPI app (import: backend.main:app)
│   ├── models.py              # Pydantic models
│   ├── utils.py               # Utilities
│   ├── few_shot/              # ML model
│   ├── requirements.txt       # ← Python dependencies BURADA
│   └── runtime.txt            # ← Python version BURADA
│
├── frontend/                   # Frontend (React)
│   ├── src/                   # React kodları
│   ├── package.json           # npm dependencies
│   └── ...
│
├── config/                     # Shared config
├── database/                   # DB models
├── scrapers/                   # Instagram scraper
├── data/                       # Training data
│
├── Dockerfile                  # Docker build
└── render.yaml                 # Deployment config
```

## ✅ Önemli Değişiklikler

### 1. requirements.txt Taşındı
**Önceki**: `/requirements.txt`
**Şimdi**: `/backend/requirements.txt`

**Neden?** Frontend build sırasında Python kurulumunu önlemek için.

### 2. Import Path'leri Güncellendi
**Backend/main.py**:
```python
from backend.utils import ...
from backend.models import ...
from backend.few_shot.fewshot_model import ...
```

### 3. Dockerfile Güncellendi
```dockerfile
COPY backend/requirements.txt .
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 4. render.yaml Düzeltildi

**Frontend**:
```yaml
- type: web
  name: cyberbullying-frontend
  env: node                              # Node environment
  buildCommand: "cd frontend && npm install && npm run build && cd .."
  startCommand: "npx serve -s frontend/build -l $PORT"
```

**Backend**:
```yaml
- type: web
  name: cyberbullying-backend
  env: docker
  dockerCommand: "cd /app && uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
```

## 🎯 Deployment Adımları

### 1. Tüm Değişiklikleri Commit Edin

```bash
git add .
git commit -m "Backend klasörü yapılandırması - requirements.txt taşındı"
git push origin main
```

### 2. Render'da Tüm Servisleri Silin

```
Dashboard → Her servisi sil:
- cyberbullying-backend
- cyberbullying-frontend
- cyberbullying-db
```

### 3. Blueprint ile Yeniden Oluşturun

```
Dashboard → New → Blueprint
Repository: SocialGuard-NLP
render.yaml otomatik algılanacak
Create Blueprint
```

### 4. Environment Variables Ekleyin

**Backend** servisi oluşturulduktan sonra:

```
Dashboard → cyberbullying-backend → Environment
```

Ekle:
```
GOOGLE_API_KEY=your_gemini_api_key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

**Frontend URL'i güncelleyin** (backend oluştuktan sonra):
```
Dashboard → cyberbullying-backend → Environment
FRONTEND_URL=[frontend'in gerçek URL'i]
```

**Backend URL'i güncelleyin** (backend oluştuktan sonra):
```
Dashboard → cyberbullying-frontend → Environment
REACT_APP_API_URL=[backend'in gerçek URL'i]
```

## 📊 Beklenen Sonuç

### Backend Logs:
```
==> Building Docker image
==> Installing dependencies from backend/requirements.txt
✅ Loaded X training examples
✅ Gemini 2.0 Flash API configured
✅ CORS: Added frontend URL
INFO: Application startup complete
```

### Frontend Logs:
```
==> Running: cd frontend && npm install && npm run build
==> Installing packages...
==> Building React app...
==> Starting server with serve
```

**Artık Python kurulumu YOK!** ✅

## 🔍 Sorun Giderme

### Frontend Hala Python Kuruyor?

1. Servisi silin
2. `git push` yaptığınızdan emin olun
3. Blueprint yeniden oluşturun (cache temizlenir)

### Import Hatası (ModuleNotFoundError)?

```python
# backend/main.py içinde:
from backend.utils import ...  # ✅ Doğru
from utils import ...          # ❌ Yanlış
```

### Backend Başlamıyor?

```
Dashboard → Backend → Logs
```

`uvicorn backend.main:app` şeklinde başlamalı.

## ✅ Son Kontrol Listesi

- [ ] `backend/requirements.txt` var
- [ ] `backend/runtime.txt` var
- [ ] `backend/__init__.py` var
- [ ] `backend/main.py` import'ları `backend.` ile başlıyor
- [ ] `Dockerfile` `COPY backend/requirements.txt` kullanıyor
- [ ] `render.yaml` frontend `env: node` kullanıyor
- [ ] `render.yaml` backend `dockerCommand` doğru
- [ ] Git push yapıldı
- [ ] Eski servisler silindi
- [ ] Blueprint ile yeniden oluşturuldu

---

**Başarılar! 🎉**

