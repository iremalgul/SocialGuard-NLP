from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# Authentication Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Existing Models
class CommentRequest(BaseModel):
    comment: str


class PredictionResponse(BaseModel):
    prediction_id: int
    prediction_name: str
    comment: str
    confidence: Optional[float] = None


class DatasetUploadResponse(BaseModel):
    message: str
    shape: List[int]
    columns: List[str]
    sample_data: List[dict]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SocialMediaAnalysisRequest(BaseModel):
    url: str
    max_comments: Optional[int] = 100
    threshold: Optional[float] = 0.8
    scraping_mode: Optional[str] = "standard"


class UserAnalysisResponse(BaseModel):
    user_id: str
    total_comments: int
    harmful_comments: int
    harmful_ratio: float
    risk_category: str
    flagged: bool
    recommendations: List[str]
    analysis_timestamp: str


class SocialMediaAnalysisResponse(BaseModel):
    url: str
    platform: str
    post_owner: Optional[str] = "unknown"
    total_comments: int
    analyzed_users: int
    flagged_users: int
    user_analyses: Dict[str, UserAnalysisResponse]
    analysis_timestamp: str
    comments: Optional[List[Dict]] = []  # Yorumları ekle


