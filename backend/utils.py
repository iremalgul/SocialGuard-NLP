import re
import unicodedata
from datetime import datetime
from typing import Optional
import pandas as pd


def clean_unicode_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\s.,!?;:()\-@#\u00C0-\u017F]', '', text)
    text = ' '.join(text.split())
    return text.strip()


def load_dataset(file_path: str) -> Optional[pd.DataFrame]:
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Desteklenen format: CSV veya JSON")
        return df
    except Exception as e:
        print(f"Veri seti yükleme hatası: {e}")
        return None


def generate_mock_user_report(user_profile, user_id):
    recommendations = []
    if user_profile['risk_category'] == 'high_risk':
        recommendations.append("Bu kullanıcı yüksek risk kategorisinde. Dikkatli izleme önerilir.")
    elif user_profile['risk_category'] == 'medium_risk':
        recommendations.append("Bu kullanıcı orta risk kategorisinde. Periyodik kontrol önerilir.")
    else:
        recommendations.append("Bu kullanıcı güvenli kategorisinde.")
    return {
        'recommendations': recommendations,
        'analysis_timestamp': datetime.now().isoformat()
    }


