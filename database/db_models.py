"""SQLAlchemy Database Models"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from .database import Base


class PredictionType(enum.Enum):
    """Manuel tahmin türleri"""
    SINGLE = "single"  # Tekli yorum
    BATCH = "batch"    # Çoklu yorum
    DATASET = "dataset"  # Veri seti yükleme


class User(Base):
    """User model - stores registered user information"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)  # 1: active, 0: inactive

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    manual_predictions = relationship("ManualPrediction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Analysis(Base):
    """Analysis model - stores social media analysis results"""
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User relation
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="analyses")
    
    # Analysis metadata
    url = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, twitter, etc.
    post_owner = Column(String(255), nullable=True)  # Gönderi sahibinin kullanıcı adı
    
    # Analysis results
    total_comments = Column(Integer, default=0)
    analyzed_users = Column(Integer, default=0)
    flagged_users = Column(Integer, default=0)
    threshold = Column(Float, default=0.8)
    
    # Detailed results stored as JSON
    # Structure: {"username": {"total_comments": int, "harmful_comments": int, ...}}
    user_analyses = Column(JSON, nullable=True)
    
    # Comments stored as JSON
    # Structure: [{"text": str, "author": str, "predicted_category_id": int, ...}]
    comments = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    analysis_duration = Column(Float, nullable=True)  # seconds

    def __repr__(self):
        return f"<Analysis(id={self.id}, user_id={self.user_id}, platform={self.platform}, url={self.url[:50]})>"


class ManualPrediction(Base):
    """Manuel tahmin modeli - Tekli, çoklu ve veri seti yükleme tahminleri"""
    __tablename__ = "manual_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User relation
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="manual_predictions")
    
    # Tahmin türü
    prediction_type = Column(Enum(PredictionType), nullable=False)
    
    # Dosya bilgisi (sadece dataset için)
    filename = Column(String(255), nullable=True)
    
    # Tahmin sonuçları
    total_comments = Column(Integer, default=0)
    
    # Kategori dağılımı
    category_0_count = Column(Integer, default=0)  # Zararsız / Nötr
    category_1_count = Column(Integer, default=0)  # Hakaret / Küfür
    category_2_count = Column(Integer, default=0)  # Cinsel İma
    category_3_count = Column(Integer, default=0)  # Alaycılık
    category_4_count = Column(Integer, default=0)  # Görünüm Eleştiri
    
    # Detaylı sonuçlar (JSON)
    # Yapı: [{"comment": "...", "category_id": 0, "category_name": "...", "confidence": 0.95}]
    predictions = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time = Column(Float, nullable=True)  # saniye

    def __repr__(self):
        return f"<ManualPrediction(id={self.id}, user_id={self.user_id}, type={self.prediction_type}, total={self.total_comments})>"


