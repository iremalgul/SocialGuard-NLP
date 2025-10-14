from typing import List, Dict
import pandas as pd
from pathlib import Path
import os
import google.generativeai as genai
import unicodedata
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import DATA_DIR

class FewShotLearningModel:
    """
    Few-Shot Learning model using Gemini API with static training data.
    """
    def __init__(self):
        self.training_data = self._load_training_data()
        self.static_examples = self._select_static_examples()
        
        # TF-IDF vectorizer oluştur
        self._prepare_tfidf_vectorizer()
        
        # Gemini API'yi yapılandır
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini 2.0 Flash API configured for few-shot learning")
        else:
            self.model = None
            print("⚠️ GEMINI_API_KEY not found, falling back to majority vote")
    
    def _load_training_data(self) -> List[Dict[str, any]]:
        """Load training data from static CSV file."""
        try:
            dataset_path: Path = DATA_DIR / "dataset.csv"
            df = pd.read_csv(
                dataset_path,
                encoding='utf-8',
                on_bad_lines='skip',  # Skip problematic lines
                engine='python',      # Better error handling
                na_values=['', ' ', 'nan', 'NaN', 'null', 'NULL']
            )
            
            # Convert to list of dictionaries
            training_data = []
            for idx, row in df.iterrows():
                try:
                    # Check if label is not null/empty
                    if pd.isna(row["label"]) or row["label"] == "":
                        continue
                    
                    # Try to convert label to int
                    label_value = row["label"]
                    if isinstance(label_value, str):
                        # Remove any non-numeric characters and try to convert
                        label_clean = ''.join(filter(str.isdigit, str(label_value)))
                        if not label_clean:
                            continue
                        label_int = int(label_clean)
                    else:
                        label_int = int(label_value)
                    
                    # Check if label is in valid range (0-4)
                    if label_int not in range(5):
                        continue
                    
                    training_data.append({
                        "text": str(row["text"]),
                        "label": label_int
                    })
                    
                except (ValueError, KeyError, TypeError) as e:
                    continue
            
            print(f"✅ Loaded {len(training_data)} training examples from {dataset_path}")
            print(f"📊 Dataset shape: {df.shape}")
            print(f"📊 Label distribution:")
            if len(training_data) > 0:
                labels = [ex["label"] for ex in training_data]
                from collections import Counter
                label_counts = Counter(labels)
                for label, count in sorted(label_counts.items()):
                    print(f"   Category {label}: {count} examples")
            return training_data
            
        except Exception as e:
            print(f"❌ Error loading training data: {e}")
            return []
    
    def _select_static_examples(self) -> Dict[int, List[Dict[str, any]]]:
        """Her kategoriden 5 manuel seçilmiş karakteristik örnek"""
        static_examples = {
            # Kategori 0: Zararsız/Nötr - Olumlu veya nötr yorumlar
            0: [
                {"text": "Bu çok güzel bir paylaşım olmuş teşekkürler", "label": 0},
                {"text": "Harika bir içerik eline sağlık", "label": 0},
                {"text": "Çok beğendim başarılar dilerim", "label": 0},
                {"text": "Süper olmuş devamını bekliyorum", "label": 0},
                {"text": "İyi akşamlar herkese güzel videoymuş", "label": 0}
            ],
            
            # Kategori 1: Doğrudan Hakaret/Küfür - Açık hakaret ve küfür
            1: [
                {"text": "Sen gerçekten aptalsın ya", "label": 1},
                {"text": "Ne kadar salak bir insansın", "label": 1},
                {"text": "Gerizekalı mısın sen", "label": 1},
                {"text": "Mal mısın nesin anlamadım", "label": 1},
                {"text": "Senin gibi dangalaklar yüzünden", "label": 1}
            ],
            
            # Kategori 2: Cinsiyetçi/Cinsel İmada - Cinsiyet ayrımcılığı
            2: [
                {"text": "Kadınlar hep böyle yapar işte", "label": 2},
                {"text": "Kızlar anlamaz bunları erkek işi", "label": 2},
                {"text": "Sen kadınsın ne anlarsın", "label": 2},
                {"text": "Erkekler böyle şeyleri yapamaz", "label": 2},
                {"text": "Kadın olduğun belli zaten", "label": 2}
            ],
            
            # Kategori 3: Alaycılık/Mikroagresyon - İma yoluyla rahatsız edici
            3: [
                {"text": "Haha ne kadar komiksin (!) gerçekten", "label": 3},
                {"text": "Vay be ne kadar zekilsin sen öyle", "label": 3},
                {"text": "Aferin sana çok başarılısın (!) devam et", "label": 3},
                {"text": "Hmm anladık ne kadar özelsin", "label": 3},
                {"text": "Eee tabii sen bilirsin en iyisini", "label": 3}
            ],
            
            # Kategori 4: Görünüm Temelli Eleştiri - Fiziksel görünüm
            4: [
                {"text": "Çok çirkinsin ya böyle olunmaz", "label": 4},
                {"text": "Ne kadar şişmansın sen", "label": 4},
                {"text": "Çok zayıfsın hiç güzel değil", "label": 4},
                {"text": "Bu kıyafetle çok kötü görünüyorsun", "label": 4},
                {"text": "Saçların berbat keşke değiştirsen", "label": 4}
            ]
        }
        
        print("📌 Manuel Statik Örnekler Yüklendi:")
        for cat, examples in static_examples.items():
            category_name = self._get_category_name(cat)
            print(f"   Kategori {cat} ({category_name}): {len(examples)} örnek")
        
        return static_examples
    
    def get_few_shot_examples(self, text: str, limit: int = 3) -> List[Dict[str, any]]:
        """
        Get few-shot examples similar to input text using similarity.
        
        Args:
            text: Input text to find similar examples for
            limit: Number of examples to return
            
        Returns:
            List of examples with text, label, and similarity score
        """
        try:
            if not self.training_data:
                return []
            
            # Calculate similarities
            similarities = []
            for example in self.training_data:
                similarity = self._calculate_similarity(text, example["text"])
                similarities.append({
                    "text": example["text"],
                    "label": example["label"],
                    "similarity": similarity
                })
            
            # Sort by similarity and return top examples
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error getting similar examples: {e}")
            return []
    
    def _normalize_text(self, text: str) -> str:
        """Normalize Turkish text for better similarity matching."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Normalize Turkish characters (optional - can be enabled if needed)
        # text = unicodedata.normalize('NFD', text)
        # text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        return text
    
    def _prepare_tfidf_vectorizer(self):
        """TF-IDF vectorizer'ı training data ile hazırla"""
        try:
            if not self.training_data:
                self.vectorizer = None
                self.tfidf_matrix = None
                return
            
            # Tüm training text'lerini al
            training_texts = [ex['text'] for ex in self.training_data]
            
            # TF-IDF vectorizer oluştur
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),  # Unigram ve bigram
                lowercase=True,
                analyzer='word',
                token_pattern=r'\b\w+\b'
            )
            
            # Training data'yı vektorize et
            self.tfidf_matrix = self.vectorizer.fit_transform(training_texts)
            
            print("✅ TF-IDF vectorizer hazırlandı")
            print(f"   - Vocabulary boyutu: {len(self.vectorizer.vocabulary_)}")
            print(f"   - Training data vektörleri: {self.tfidf_matrix.shape}")
        except Exception as e:
            print(f"⚠️ TF-IDF hazırlama hatası: {e}")
            self.vectorizer = None
            self.tfidf_matrix = None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using TF-IDF + Cosine Similarity.
        Fallback: Jaccard similarity if TF-IDF fails.
        """
        try:
            # TF-IDF + Cosine Similarity (Daha gelişmiş)
            if self.vectorizer is not None:
                # text1'i vektorize et
                vec1 = self.vectorizer.transform([text1])
                # text2'yi vektorize et
                vec2 = self.vectorizer.transform([text2])
                # Cosine similarity hesapla
                similarity = cosine_similarity(vec1, vec2)[0][0]
                return float(similarity)
        except Exception as e:
            # TF-IDF başarısız olursa Jaccard'a düş
            pass
        
        # Fallback: Jaccard Similarity (Basit ama hızlı)
        norm_text1 = self._normalize_text(text1)
        norm_text2 = self._normalize_text(text2)
        
        words1 = set(norm_text1.split())
        words2 = set(norm_text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def create_enhanced_prompt(self, text: str) -> str:
        """
        Create enhanced prompt with static + dynamic few-shot examples.
        
        Args:
            text: Text to analyze
            
        Returns:
            Enhanced prompt string
        """
        print(f"\n🔍 Input Text: '{text}'")
        print("="*60)
        
        # 1. Statik örnekler (her kategoriden 5'er)
        static_examples_str = "\n🔸 SABİT ÖRNEKLER (Her kategoriden 5'er):\n"
        for category in range(5):
            category_name = self._get_category_name(category)
            static_examples_str += f"\n--- Kategori {category}: {category_name} ---\n"
            
            examples = self.static_examples.get(category, [])[:5]
            for i, ex in enumerate(examples, 1):
                static_examples_str += f'{i}. "{ex["text"]}" -> {category}\n'
        
        print(static_examples_str)
        
        # 2. Dinamik benzer örnekler (en benzer 5)
        similar_examples = self.get_few_shot_examples(text, limit=5)
        
        dynamic_examples_str = "\n🔸 DİNAMİK BENZER ÖRNEKLER (En benzer 5):\n"
        print("\n📊 En Benzer 5 Örnek:")
        print("-" * 60)
        
        for i, ex in enumerate(similar_examples, 1):
            category_name = self._get_category_name(ex["label"])
            similarity = ex.get("similarity", 0)
            dynamic_examples_str += f'{i}. "{ex["text"]}" -> {ex["label"]} ({category_name}) [Benzerlik: {similarity:.2f}]\n'
            
            print(f"{i}. \"{ex['text']}\"")
            print(f"   → Category: {ex['label']} ({category_name})")
            print(f"   → Similarity: {similarity:.3f}\n")
        
        # Prompt'u oluştur
        examples_for_prompt = "\n\nEĞİTİM ÖRNEKLERİ:\n"
        
        # Statik örnekleri ekle
        for category in range(5):
            examples = self.static_examples.get(category, [])[:5]
            for ex in examples:
                category_name = self._get_category_name(ex["label"])
                examples_for_prompt += f'"{ex["text"]}" -> {ex["label"]} ({category_name})\n'
        
        # Dinamik benzer örnekleri ekle
        examples_for_prompt += "\n💡 İNPUT'A EN BENZER ÖRNEKLER:\n"
        for ex in similar_examples:
            category_name = self._get_category_name(ex["label"])
            similarity = ex.get("similarity", 0)
            examples_for_prompt += f'"{ex["text"]}" -> {ex["label"]} ({category_name}) [Benzerlik: {similarity:.2f}]\n'
        
        # Enhanced prompt
        prompt = f"""
Sen bir yorum sınıflandırma uzmanısın. Aşağıdaki yorumu analiz et ve kategorilerden birine sınıflandır.

KATEGORİLER:
0: No Harassment / Neutral (Zararsız/Nötr) - Normal, zararsız yorumlar
1: Direct Insult / Profanity (Doğrudan Hakaret/Küfür) - Açık hakaret ve küfür
2: Sexist / Sexual Implication (Cinsiyetçi/Cinsel İmada Bulunma) - Cinsiyetçi veya cinsel içerik
3: Sarcasm / Microaggression (Alaycı/Mikroagresyon) - Alaycı veya gizli saldırganlık
4: Appearance-based Criticism (Görünüm Temelli Eleştiri) - Fiziksel görünüm eleştirisi

ÖNEMLİ KURALLAR:
- "kadın", "erkek" gibi kelimeler tek başına zararlı DEĞİLDİR
- Önce eğitim örneklerini öğren, sonra input'a benzer örneklere odaklan
{examples_for_prompt}

ŞİMDİ ANALİZ EDİLECEK YORUM:
"{text}"

Sadece kategori numarasını (0-4 arası) döndür. Açıklama yapma, sadece sayıyı ver.
"""
        print("\n" + "="*60)
        print("✅ Prompt hazırlandı:")
        print(f"   - Statik örnekler: {sum(len(exs) for exs in self.static_examples.values())} adet")
        print(f"   - Dinamik örnekler: {len(similar_examples)} adet")
        print("="*60 + "\n")
        
        return prompt
    
    def _get_category_name(self, category: int) -> str:
        """Get category name from number."""
        category_names = {
            0: "No Harassment / Neutral",
            1: "Direct Insult / Profanity",
            2: "Sexist / Sexual Implication",
            3: "Sarcasm / Microaggression",
            4: "Appearance-based Criticism"
        }
        return category_names.get(category, "Unknown")
    
    def predict_with_few_shot(self, text: str) -> Dict[str, any]:
        """
        Predict using Gemini with few-shot learning from static training data.
        
        Args:
            text: Text to analyze
            
        Returns:
            Prediction results
        """
        try:
            if self.model:
                try:
                    # Gemini API ile analiz
                    enhanced_prompt = self.create_enhanced_prompt(text)
                    response = self.model.generate_content(enhanced_prompt)
                    prediction_text = response.text.strip()
                    
                    # Sayıyı çıkar
                    prediction = int(''.join(filter(str.isdigit, prediction_text[:5])))
                    
                    if prediction in range(5):
                        # Confidence hesaplama - benzer örneklerin ortalamasına göre
                        similar_examples = self.get_few_shot_examples(text, limit=5)
                        confidence = self._calculate_confidence(text, prediction, similar_examples)
                        
                        return {
                            "category": prediction,
                            "confidence": round(confidence, 3),
                            "message": "Gemini API + Few-shot learning"
                        }
                except Exception as api_error:
                    print(f"Gemini API hatası: {api_error}")
                    # API hatası durumunda fallback'e geç
            
            # Fallback: majority vote from similar examples
            examples = self.get_few_shot_examples(text, limit=5)
            if not examples:
                return self._default_response()
            
            from collections import Counter
            labels = [ex["label"] for ex in examples]
            most_common = Counter(labels).most_common(1)[0]
            prediction = most_common[0]
            confidence = most_common[1] / len(labels) * 0.7
            
            return {
                "category": prediction,
                "confidence": round(confidence, 3),
                "message": "Majority vote from similar examples"
            }
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                "category": 0,
                "confidence": 0.5,
                "message": f"Error: {str(e)}"
            }
    
    def _calculate_confidence(self, text: str, predicted_category: int, similar_examples: List[Dict]) -> float:
        """
        Confidence skorunu akıllıca hesapla.
        
        Faktörler:
        1. En benzer örneğin similarity skoru (ağırlık: 0.4)
        2. Benzer örneklerdeki kategori tutarlılığı (ağırlık: 0.4)
        3. Base confidence (ağırlık: 0.2)
        """
        if not similar_examples:
            return 0.50  # Düşük confidence
        
        # 1. En yüksek benzerlik skoru
        max_similarity = similar_examples[0].get('similarity', 0)
        similarity_score = max_similarity  # 0.0 - 1.0
        
        # 2. Kategori tutarlılığı (benzer örneklerin kaçı aynı kategoriyi gösteriyor?)
        same_category_count = sum(1 for ex in similar_examples if ex['label'] == predicted_category)
        consistency_score = same_category_count / len(similar_examples)  # 0.0 - 1.0
        
        # 3. Base confidence
        base_confidence = 0.70
        
        # Ağırlıklı ortalama
        final_confidence = (
            similarity_score * 0.4 +
            consistency_score * 0.4 +
            base_confidence * 0.2
        )
        
        # Minimum ve maksimum sınırları
        final_confidence = max(0.50, min(0.95, final_confidence))
        
        print(f"📊 Confidence Hesaplama:")
        print(f"   - En yüksek benzerlik: {max_similarity:.3f}")
        print(f"   - Tutarlılık ({same_category_count}/{len(similar_examples)}): {consistency_score:.3f}")
        print(f"   - Base: {base_confidence:.3f}")
        print(f"   - Final Confidence: {final_confidence:.3f}")
        
        return final_confidence
    
    def _default_response(self) -> Dict[str, any]:
        """Default response when prediction fails."""
        return {
            "category": 0,
            "confidence": 0.5,
            "message": "Varsayılan kategori"
        }

# Global few-shot learning model instance
few_shot_model = FewShotLearningModel()
