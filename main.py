from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import google.generativeai as genai
import pandas as pd
import os
import json
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime, timedelta
from scrapers.instagram_comments_scraper import scrape_instagram_comments
from config import LABEL_MAP, REVERSE_LABEL_MAP
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from utils import clean_unicode_text, load_dataset, generate_mock_user_report
from few_shot.fewshot_model import few_shot_model
from models import (
    CommentRequest,
    PredictionResponse,
    DatasetUploadResponse,
    ErrorResponse,
    SocialMediaAnalysisRequest,
    UserAnalysisResponse,
    SocialMediaAnalysisResponse,
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from database import get_db, User, Analysis, ManualPrediction, PredictionType
from database.auth_utils import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_user_by_email,
)

app = FastAPI(
    title="Yorum Kategorisi Tahmin Sistemi",
    description="Gemini 2.0 Flash ile Gelişmiş Metin Analizi API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# React frontend statik dosyaları kendi sunucusunda servis ediyor
# Static files artık gerekli değil

# Gemini API konfigürasyonu (fewshot_model kendi yapılandırmasını yapıyor)


@app.get("/")
async def read_root():
    """Ana sayfa - React frontend'e yönlendir"""
    return {
        "message": "SocialGuard Pro API",
        "version": "1.0.0",
        "frontend": "http://localhost:3000",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Sağlık kontrolü"""
    return {"status": "healthy", "model": "gemini-2.0-flash-exp"}


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Kullanıcı kaydı oluştur"""
    try:
        # Email kontrolü
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Bu e-posta adresi zaten kullanılıyor"
            )
        
        # Şifre uzunluğu kontrolü
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Şifre en az 8 karakter olmalıdır"
            )
        
        # Kullanıcı oluştur
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            last_login=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Token oluştur
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.id)},
            expires_delta=access_token_expires
        )
        
        # UserResponse oluştur
        user_response = UserResponse(
            id=str(new_user.id),
            name=new_user.name,
            email=new_user.email,
            created_at=new_user.created_at,
            last_login=new_user.last_login
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Kayıt hatası: {str(e)}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Kullanıcı girişi"""
    try:
        # Kullanıcı doğrulama
        user = authenticate_user(db, user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="E-posta veya şifre hatalı"
            )
        
        # Son giriş zamanını güncelle
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Token oluştur
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # UserResponse oluştur
        user_response = UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Giriş hatası: {str(e)}")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


# ============================================================================
# Existing Endpoints
# ============================================================================

@app.get("/api/labels")
async def get_labels():
    """Mevcut kategorileri getir"""
    return {
        "labels": LABEL_MAP,
        "reverse_labels": REVERSE_LABEL_MAP
    }

@app.get("/api/dataset-stats")
async def get_dataset_stats():
    """Gerçek dataset istatistiklerini getir (data/dataset.csv)."""
    try:
        from config.settings import DATA_DIR
        dataset_path = str(DATA_DIR / "dataset.csv")
        df = pd.read_csv(
            dataset_path,
            encoding="utf-8",
            on_bad_lines="skip",
            engine="python",
            na_values=["", " ", "nan", "NaN", "null", "NULL"],
        )

        # Etiketleri güvenli biçimde sayısala çevir
        def to_label(val):
            try:
                s = str(val)
                digits = "".join(ch for ch in s if ch.isdigit())
                if not digits:
                    return None
                i = int(digits)
                return i if i in range(5) else None
            except Exception:
                return None

        labels = df.get("label") if "label" in df.columns else None
        if labels is None:
            raise ValueError("'label' sütunu bulunamadı")

        label_series = labels.map(to_label)
        valid = label_series.dropna().astype(int)

        # Dağılım
        counts = {str(i): int((valid == i).sum()) for i in range(5)}
        total_examples = int(valid.shape[0])

        return {
            "total_examples": total_examples,
            "label_statistics": counts,
            "fewshot_enabled": True,
            "dataset_path": dataset_path,
            "columns": df.columns.tolist(),
        }
    except Exception as e:
        print(f"Dataset stats error: {e}")
        raise HTTPException(status_code=500, detail=f"İstatistik hatası: {str(e)}")

@app.post("/api/similar-examples")
async def get_similar_examples(request: CommentRequest):
    """Verilen yoruma benzer örnekleri getir"""
    try:
        if not request.comment.strip():
            raise HTTPException(status_code=400, detail="Yorum boş olamaz")
        examples = few_shot_model.get_few_shot_examples(request.comment, limit=10)
        return {"query": request.comment, "similar_examples": examples, "total_found": len(examples)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benzer örnek bulma hatası: {str(e)}")

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_comment(
    request: CommentRequest, 
    fewshot: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yorum kategorisini tahmin et"""
    start_time = datetime.utcnow()
    try:
        if not request.comment.strip():
            raise HTTPException(status_code=400, detail="Yorum boş olamaz")
        
        # Few-shot tahmin
        fs = few_shot_model.predict_with_few_shot(request.comment)
        prediction_id = int(fs.get("category", 0))
        prediction_name = REVERSE_LABEL_MAP.get(prediction_id, "No Harassment / Neutral")
        confidence = float(fs.get("confidence", 0.7))
        
        # Database'e kaydet
        try:
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Kategori sayacını hazırla
            category_counts = {f"category_{i}_count": 0 for i in range(5)}
            category_counts[f"category_{prediction_id}_count"] = 1
            
            manual_prediction = ManualPrediction(
                user_id=current_user.id,
                prediction_type=PredictionType.SINGLE,
                total_comments=1,
                predictions=[{
                    "comment": request.comment,
                    "category_id": prediction_id,
                    "category_name": prediction_name,
                    "confidence": confidence
                }],
                processing_time=processing_time,
                **category_counts
            )
            
            db.add(manual_prediction)
            db.commit()
            print(f"Single prediction saved to database with ID: {manual_prediction.id}")
        except Exception as db_error:
            print(f"Database save error: {db_error}")
            db.rollback()
        
        return PredictionResponse(
            prediction_id=prediction_id,
            prediction_name=prediction_name,
            comment=request.comment,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin hatası: {str(e)}")

@app.post("/api/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Veri seti yükle ve her yorum için AI ile label hesapla"""
    start_time = datetime.utcnow()
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Dosya seçilmedi")
        
        # Geçici olarak kaydet
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Veri setini yükle
        df = load_dataset(file_path)
        
        if df is None:
            raise HTTPException(status_code=400, detail="Veri seti yüklenemedi")
        
        # Gerekli sütunları kontrol et
        required_columns = ['comment', 'username', 'platform']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV'de şu sütunlar olmalı: {', '.join(required_columns)}"
            )
        
        # Her yorum için AI ile label hesapla
        labels = []
        predictions_data = []
        category_counts = {i: 0 for i in range(5)}
        
        for idx, comment in enumerate(df['comment']):
            try:
                result = few_shot_model.predict_with_few_shot(str(comment))
                label = int(result.get("category", 0))
                confidence = float(result.get("confidence", 0.7))
                category_name = REVERSE_LABEL_MAP.get(label, "Unknown")
                
                predictions_data.append({
                    "comment": str(comment),
                    "category_id": label,
                    "category_name": category_name,
                    "confidence": confidence,
                    "username": str(df.iloc[idx]['username']) if 'username' in df.columns else None,
                    "platform": str(df.iloc[idx]['platform']) if 'platform' in df.columns else None
                })
                
                category_counts[label] += 1
            except Exception as e:
                print(f"Tahmin hatası: {e}")
                label = 0
            labels.append(label)
        
        # Label sütununu ekle
        df['label'] = labels
        
        # Sütun sırasını düzenle: comment, label, username, platform
        df = df[['comment', 'label', 'username', 'platform']]
        
        # JSON dosyası olarak kaydet
        output_filename = f"labeled_{file.filename.replace('.csv', '')}.json"
        output_path = f"data/{output_filename}"
        df.to_json(output_path, orient='records', force_ascii=False, indent=2)
        
        # Geçici dosyayı sil
        os.remove(file_path)
        
        # Database'e kaydet
        try:
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            manual_prediction = ManualPrediction(
                user_id=current_user.id,
                prediction_type=PredictionType.DATASET,
                filename=file.filename,
                total_comments=len(df),
                category_0_count=category_counts[0],
                category_1_count=category_counts[1],
                category_2_count=category_counts[2],
                category_3_count=category_counts[3],
                category_4_count=category_counts[4],
                predictions=predictions_data,
                processing_time=processing_time
            )
            
            db.add(manual_prediction)
            db.commit()
            print(f"Dataset prediction saved to database with ID: {manual_prediction.id}")
        except Exception as db_error:
            print(f"Database save error: {db_error}")
            db.rollback()
        
        # İlk 5 satırı kategori isimleriyle birlikte hazırla
        sample_data = []
        for _, row in df.head(5).iterrows():
            sample_data.append({
                'comment': row['comment'],
                'label': int(row['label']),
                'label_name': REVERSE_LABEL_MAP.get(int(row['label']), 'Bilinmeyen'),
                'username': row['username'],
                'platform': row['platform']
            })
        
        return {
            "message": "Veri seti başarıyla işlendi",
            "total_rows": len(df),
            "columns": df.columns.tolist(),
            "sample_data": sample_data,
            "output_file": output_filename,
            "download_url": f"/api/download-dataset/{output_filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya yükleme hatası: {str(e)}")

@app.get("/api/download-dataset/{filename}")
async def download_dataset(filename: str):
    """İşlenmiş dataset'i indir"""
    try:
        file_path = f"data/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/json'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İndirme hatası: {str(e)}")

@app.post("/api/batch-predict")
async def batch_predict(
    comments: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toplu tahmin"""
    start_time = datetime.utcnow()
    try:
        results = []
        category_counts = {i: 0 for i in range(5)}
        
        for comment in comments:
            fs = few_shot_model.predict_with_few_shot(comment)
            prediction_id = int(fs.get("category", 0))
            prediction_name = REVERSE_LABEL_MAP.get(prediction_id, "No Harassment / Neutral")
            confidence = float(fs.get("confidence", 0.7))
            
            results.append({
                "comment": comment,
                "category_id": prediction_id,
                "category_name": prediction_name,
                "confidence": confidence,
                "prediction_id": prediction_id,
                "prediction_name": prediction_name,
            })
            
            category_counts[prediction_id] += 1
        
        # Database'e kaydet
        try:
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            manual_prediction = ManualPrediction(
                user_id=current_user.id,
                prediction_type=PredictionType.BATCH,
                total_comments=len(comments),
                category_0_count=category_counts[0],
                category_1_count=category_counts[1],
                category_2_count=category_counts[2],
                category_3_count=category_counts[3],
                category_4_count=category_counts[4],
                predictions=results,
                processing_time=processing_time
            )
            
            db.add(manual_prediction)
            db.commit()
            print(f"Batch prediction saved to database with ID: {manual_prediction.id}")
        except Exception as db_error:
            print(f"Database save error: {db_error}")
            db.rollback()
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Toplu tahmin hatası: {str(e)}")

@app.post("/api/social-media-analysis", response_model=SocialMediaAnalysisResponse)
async def analyze_social_media(
    request: SocialMediaAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sosyal medya URL'sini analiz et ve kullanıcıları tespit et"""
    start_time = datetime.utcnow()
    try:
        # Instagram yorumlarını çıkar
        scrape_result = scrape_instagram_comments(request.url, request.max_comments)
        
        # Yeni format: {'comments': [...], 'post_owner': '...', 'total_comments': N}
        # Eski format uyumluluğu için kontrol
        if isinstance(scrape_result, dict) and 'comments' in scrape_result:
            comments = scrape_result['comments']
            post_owner = scrape_result.get('post_owner', 'unknown')
        else:
            # Eski format (sadece liste)
            comments = scrape_result if isinstance(scrape_result, list) else []
            post_owner = 'unknown'
        
        if not comments:
            raise HTTPException(status_code=400, detail="Bu URL'den yorum çıkarılamadı")
        
        # Yorumları olduğu gibi bırak (temizleme yok)
        print(f"Post Sahibi: {post_owner}")
        print(f"Çekilen yorum sayısı: {len(comments)}")
        if comments:
            print(f"İlk yorum örneği: {comments[0]['text'][:50]}...")
        
        # Platform tespit et
        platform = "instagram"  # Şimdilik sadece Instagram
        
        # Kullanıcıları grupla
        users_data = {}
        for comment in comments:
            author = comment['author']
            if author not in users_data:
                users_data[author] = []
            users_data[author].append(comment)
        
        # Her kullanıcıyı analiz et
        user_analyses = {}
        flagged_count = 0
        
        for user_id, user_comments in users_data.items():
            try:
                # Mock kullanıcı analizi
                user_profile = {
                    'total_comments': len(user_comments),
                    'harmful_comments': 0,
                    'harmful_ratio': 0.0,
                    'risk_category': 'safe',
                    'flagged': False,
                    'analysis_timestamp': datetime.now().isoformat()
                }
                
                # Zararlı yorum tespiti (unified predictor + few-shot)
                harmful_count = 0
                for comment in user_comments:
                    try:
                        fs = few_shot_model.predict_with_few_shot(comment['text'])
                        pred_id = int(fs.get("category", 0))
                        pred_name = REVERSE_LABEL_MAP.get(pred_id, "No Harassment / Neutral")
                        pred_conf = float(fs.get("confidence", 0.7))
                        comment['predicted_category_id'] = pred_id
                        comment['predicted_category_name'] = pred_name
                        comment['predicted_confidence'] = pred_conf
                        if pred_id > 0:
                            harmful_count += 1
                    except Exception:
                        continue
                
                user_profile['harmful_comments'] = harmful_count
                user_profile['harmful_ratio'] = harmful_count / len(user_comments) if user_comments else 0
                
                # Risk kategorisi belirle
                if user_profile['harmful_ratio'] > 0.3:
                    user_profile['risk_category'] = 'high_risk'
                elif user_profile['harmful_ratio'] > 0.1:
                    user_profile['risk_category'] = 'medium_risk'
                elif user_profile['harmful_ratio'] > 0.05:
                    user_profile['risk_category'] = 'low_risk'
                else:
                    user_profile['risk_category'] = 'safe'
                
                # Flagged durumu belirle (Frontend'den gelen threshold değerini kullan)
                user_profile['flagged'] = user_profile['harmful_ratio'] > request.threshold
                
                if user_profile['total_comments'] >= 1:  # En az 1 yorum
                    report = generate_mock_user_report(user_profile, user_id)
                    
                    user_analyses[user_id] = UserAnalysisResponse(
                        user_id=user_id,
                        total_comments=user_profile['total_comments'],
                        harmful_comments=user_profile['harmful_comments'],
                        harmful_ratio=user_profile['harmful_ratio'],
                        risk_category=user_profile['risk_category'],
                        flagged=user_profile['flagged'],
                        recommendations=report['recommendations'],
                        analysis_timestamp=user_profile['analysis_timestamp']
                    )
                    
                    if user_profile['flagged']:
                        flagged_count += 1
                        
            except Exception as e:
                print(f"Kullanıcı analiz hatası ({user_id}): {e}")
                continue
        
        print(f"Returning {len(comments)} comments in response")
        if comments:
            # Güvenli şekilde ilk yorumu yazdır
            first_comment_text = comments[0]['text'][:50]
            print(f"First comment: {first_comment_text}...")
            print(f"Comment structure: {list(comments[0].keys())}")
        else:
            print("No comments")
        
        response_data = {
            "url": request.url,
            "platform": platform,
            "post_owner": post_owner,
            "total_comments": len(comments),
            "analyzed_users": len(user_analyses),
            "flagged_users": flagged_count,
            "user_analyses": user_analyses,
            "analysis_timestamp": datetime.now().isoformat(),
            "comments": comments
        }
        
        print(f"Response data keys: {list(response_data.keys())}")
        
        # Analiz sonucunu veritabanına kaydet
        try:
            end_time = datetime.utcnow()
            analysis_duration = (end_time - start_time).total_seconds()
            
            # Kullanıcı analizlerini serileştirilebilir formata dönüştür
            serializable_user_analyses = {}
            for username, analysis in user_analyses.items():
                serializable_user_analyses[username] = {
                    "user_id": analysis.user_id,
                    "total_comments": analysis.total_comments,
                    "harmful_comments": analysis.harmful_comments,
                    "harmful_ratio": analysis.harmful_ratio,
                    "risk_category": analysis.risk_category,
                    "flagged": analysis.flagged,
                    "recommendations": analysis.recommendations,
                    "analysis_timestamp": analysis.analysis_timestamp
                }
            
            new_analysis = Analysis(
                user_id=current_user.id,
                url=request.url,
                platform=platform,
                post_owner=post_owner,
                total_comments=len(comments),
                analyzed_users=len(user_analyses),
                flagged_users=flagged_count,
                threshold=request.threshold,
                user_analyses=serializable_user_analyses,
                comments=comments,
                analysis_duration=analysis_duration
            )
            
            db.add(new_analysis)
            db.commit()
            db.refresh(new_analysis)
            
            print(f"Analysis saved to database with ID: {new_analysis.id}")
        except Exception as db_error:
            print(f"Database save error: {db_error}")
            # Analiz kaydedilemese bile sonucu döndür
            db.rollback()
        
        return SocialMediaAnalysisResponse(**response_data)
        
    except Exception as e:
        # Unicode karakterleri güvenli şekilde işle
        error_message = str(e)
        # Güvenli şekilde temizle
        safe_error = clean_unicode_text(error_message) if error_message else "Bilinmeyen hata"
        raise HTTPException(status_code=500, detail=f"Sosyal medya analiz hatası: {safe_error}")


@app.get("/api/detection-threshold")
async def get_detection_threshold():
    """Tespit eşik değerini getir (mock)"""
    return {
        "threshold": 0.8,
        "min_comments": 1,
        "risk_categories": ["safe", "low_risk", "medium_risk", "high_risk"]
    }

@app.post("/api/update-threshold")
async def update_detection_threshold(threshold: float):
    """Tespit eşik değerini güncelle"""
    if not 0.0 <= threshold <= 1.0:
        raise HTTPException(status_code=400, detail="Eşik değeri 0.0-1.0 arasında olmalı")
    
    # Mock threshold update
    return {"message": f"Eşik değeri {threshold} olarak güncellendi"}


# ============================================================================
# Analysis History Endpoints
# ============================================================================

@app.get("/api/analyses/history")
async def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Kullanıcının analiz geçmişini getir"""
    try:
        # Kullanıcının analizlerini getir (en yeni önce)
        analyses = db.query(Analysis).filter(
            Analysis.user_id == current_user.id
        ).order_by(
            Analysis.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Toplam analiz sayısı
        total_count = db.query(Analysis).filter(
            Analysis.user_id == current_user.id
        ).count()
        
        # Response formatı
        results = []
        for analysis in analyses:
            results.append({
                "id": str(analysis.id),
                "url": analysis.url,
                "platform": analysis.platform,
                "post_owner": analysis.post_owner,
                "total_comments": analysis.total_comments,
                "analyzed_users": analysis.analyzed_users,
                "flagged_users": analysis.flagged_users,
                "threshold": analysis.threshold,
                "created_at": analysis.created_at.isoformat(),
                "analysis_duration": analysis.analysis_duration
            })
        
        return {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "analyses": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geçmiş getirme hatası: {str(e)}")


@app.get("/api/analyses/{analysis_id}")
async def get_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir analizin detaylarını getir"""
    try:
        # Analizi getir
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analiz bulunamadı")
        
        return {
            "id": str(analysis.id),
            "url": analysis.url,
            "platform": analysis.platform,
            "post_owner": analysis.post_owner,
            "total_comments": analysis.total_comments,
            "analyzed_users": analysis.analyzed_users,
            "flagged_users": analysis.flagged_users,
            "threshold": analysis.threshold,
            "user_analyses": analysis.user_analyses,
            "comments": analysis.comments,
            "created_at": analysis.created_at.isoformat(),
            "analysis_duration": analysis.analysis_duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detay getirme hatası: {str(e)}")


@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir analizi sil"""
    try:
        # Analizi getir
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analiz bulunamadı")
        
        db.delete(analysis)
        db.commit()
        
        return {"message": "Analiz başarıyla silindi"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Silme hatası: {str(e)}")


@app.get("/api/analyses/stats/summary")
async def get_analysis_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının analiz istatistiklerini getir"""
    try:
        # Toplam analiz sayısı
        total_analyses = db.query(Analysis).filter(
            Analysis.user_id == current_user.id
        ).count()
        
        # Tüm analizleri getir
        analyses = db.query(Analysis).filter(
            Analysis.user_id == current_user.id
        ).all()
        
        total_comments_analyzed = sum(a.total_comments for a in analyses)
        total_flagged_users = sum(a.flagged_users for a in analyses)
        total_users_analyzed = sum(a.analyzed_users for a in analyses)
        
        # Platform dağılımı
        platform_stats = {}
        for analysis in analyses:
            platform = analysis.platform
            if platform not in platform_stats:
                platform_stats[platform] = 0
            platform_stats[platform] += 1
        
        return {
            "total_analyses": total_analyses,
            "total_comments_analyzed": total_comments_analyzed,
            "total_users_analyzed": total_users_analyzed,
            "total_flagged_users": total_flagged_users,
            "platform_distribution": platform_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistik hatası: {str(e)}")


# ============================================================================
# Manual Predictions Endpoints
# ============================================================================

@app.get("/api/manual-predictions/history")
async def get_manual_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Kullanıcının manuel tahmin geçmişini getir"""
    try:
        query = db.query(ManualPrediction).filter(
            ManualPrediction.user_id == current_user.id
        )
        
        # Tip filtreleme
        if prediction_type:
            if prediction_type == "single":
                query = query.filter(ManualPrediction.prediction_type == PredictionType.SINGLE)
            elif prediction_type == "batch":
                query = query.filter(ManualPrediction.prediction_type == PredictionType.BATCH)
            elif prediction_type == "dataset":
                query = query.filter(ManualPrediction.prediction_type == PredictionType.DATASET)
        
        # Toplam sayı
        total_count = query.count()
        
        # Sonuçları getir
        predictions = query.order_by(
            ManualPrediction.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Response formatı
        results = []
        for pred in predictions:
            results.append({
                "id": str(pred.id),
                "prediction_type": pred.prediction_type.value,
                "filename": pred.filename,
                "total_comments": pred.total_comments,
                "category_0_count": pred.category_0_count,
                "category_1_count": pred.category_1_count,
                "category_2_count": pred.category_2_count,
                "category_3_count": pred.category_3_count,
                "category_4_count": pred.category_4_count,
                "created_at": pred.created_at.isoformat(),
                "processing_time": pred.processing_time
            })
        
        return {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "predictions": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geçmiş getirme hatası: {str(e)}")


@app.get("/api/manual-predictions/{prediction_id}")
async def get_manual_prediction_detail(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir manuel tahminin detaylarını getir"""
    try:
        prediction = db.query(ManualPrediction).filter(
            ManualPrediction.id == prediction_id,
            ManualPrediction.user_id == current_user.id
        ).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Tahmin bulunamadı")
        
        return {
            "id": str(prediction.id),
            "prediction_type": prediction.prediction_type.value,
            "filename": prediction.filename,
            "total_comments": prediction.total_comments,
            "category_0_count": prediction.category_0_count,
            "category_1_count": prediction.category_1_count,
            "category_2_count": prediction.category_2_count,
            "category_3_count": prediction.category_3_count,
            "category_4_count": prediction.category_4_count,
            "predictions": prediction.predictions,
            "created_at": prediction.created_at.isoformat(),
            "processing_time": prediction.processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detay getirme hatası: {str(e)}")


@app.delete("/api/manual-predictions/{prediction_id}")
async def delete_manual_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir manuel tahmini sil"""
    try:
        prediction = db.query(ManualPrediction).filter(
            ManualPrediction.id == prediction_id,
            ManualPrediction.user_id == current_user.id
        ).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Tahmin bulunamadı")
        
        db.delete(prediction)
        db.commit()
        
        return {"message": "Tahmin başarıyla silindi"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Silme hatası: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
