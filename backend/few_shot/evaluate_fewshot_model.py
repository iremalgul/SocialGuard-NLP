"""
Few-Shot Model Değerlendirme Scripti
Test veri seti üzerinde classification report çıkartır.
"""

import pandas as pd
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import numpy as np
from few_shot.fewshot_model import few_shot_model
from config import DATA_DIR
import time

def evaluate_fewshot_model(test_file: str = "test_set_siber_zorbalik_v2.csv"):
    """
    Test veri seti üzerinde few-shot modeli değerlendir.
    
    Args:
        test_file: Test veri seti dosya adı
    """
    print("=" * 80)
    print("FEW-SHOT MODEL DEĞERLENDİRME")
    print("=" * 80)
    
    # Test veri setini yükle
    test_path = DATA_DIR / test_file
    print(f"\n📂 Test veri seti yükleniyor: {test_path}")
    
    try:
        df = pd.read_csv(test_path, encoding='utf-8')
        # Boş satırları temizle
        df = df.dropna(subset=['comment', 'label'])
        print(f"✅ {len(df)} test örneği yüklendi")
        
    except Exception as e:
        print(f"❌ Veri yükleme hatası: {e}")
        return
    
    # Kategori isimleri
    category_names = {
        0: "No Harassment / Neutral",
        1: "Direct Insult / Profanity",
        2: "Sexist / Sexual Implication",
        3: "Sarcasm / Microaggression",
        4: "Appearance-based Criticism"
    }
    
    # Tahminleri topla
    y_true = []
    y_pred = []
    confidences = []
    
    print("\n" + "=" * 80)
    print("TAHMİNLER YAPILIYOR...")
    print("=" * 80)
    
    for idx, row in df.iterrows():
        comment = row['comment']
        true_label = int(row['label'])
        
        print(f"\n[{idx + 1}/{len(df)}] Yorum: '{comment}'")
        print(f"Gerçek Label: {true_label} ({category_names[true_label]})")
        
        # Tahmin yap
        try:
            result = few_shot_model.predict_with_few_shot(comment)
            predicted_label = result['category']
            confidence = result['confidence']
            
            y_true.append(true_label)
            y_pred.append(predicted_label)
            confidences.append(confidence)
            
            # Sonuç
            match_status = "✅" if predicted_label == true_label else "❌"
            print(f"{match_status} Tahmin: {predicted_label} ({category_names[predicted_label]})")
            print(f"   Güven: {confidence:.3f}")
            
            # API rate limit için kısa bekleme
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Tahmin hatası: {e}")
            # Hata durumunda varsayılan değer
            y_true.append(true_label)
            y_pred.append(0)  # Varsayılan: Zararsız
            confidences.append(0.5)
            time.sleep(1)  # Hata durumunda daha uzun bekle
    
    # Değerlendirme metrikleri hesapla
    print("\n" + "=" * 80)
    print("DEĞERLENDIRME SONUÇLARI")
    print("=" * 80)
    
    # Accuracy
    accuracy = accuracy_score(y_true, y_pred)
    print(f"\n📊 Genel Doğruluk (Accuracy): {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Ortalama güven
    avg_confidence = np.mean(confidences)
    print(f"📊 Ortalama Güven Skoru: {avg_confidence:.4f}")
    
    # Classification Report
    print("\n" + "=" * 80)
    print("CLASSIFICATION REPORT")
    print("=" * 80)
    
    target_names = [f"{i}: {category_names[i]}" for i in range(5)]
    report = classification_report(
        y_true, 
        y_pred, 
        target_names=target_names,
        digits=4,
        zero_division=0
    )
    print(report)
    
    # Confusion Matrix
    print("\n" + "=" * 80)
    print("CONFUSION MATRIX")
    print("=" * 80)
    
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3, 4])
    
    print("\n    ", end="")
    for i in range(5):
        print(f"Pred-{i:>2}", end=" ")
    print()
    print("    " + "-" * 50)
    
    for i in range(5):
        print(f"True-{i} |", end=" ")
        for j in range(5):
            print(f"{cm[i][j]:>6}", end=" ")
        print()
    
    # Her kategori için detaylı analiz
    print("\n" + "=" * 80)
    print("KATEGORİ BAZINDA DETAYLI ANALİZ")
    print("=" * 80)
    
    for i in range(5):
        true_count = np.sum(np.array(y_true) == i)
        pred_count = np.sum(np.array(y_pred) == i)
        correct_count = np.sum((np.array(y_true) == i) & (np.array(y_pred) == i))
        
        if true_count > 0:
            category_accuracy = correct_count / true_count
        else:
            category_accuracy = 0.0
        
        print(f"\n📌 Kategori {i}: {category_names[i]}")
        print(f"   - Gerçek örnekler: {true_count}")
        print(f"   - Tahmin edilen: {pred_count}")
        print(f"   - Doğru tahmin: {correct_count}")
        print(f"   - Kategori doğruluğu: {category_accuracy:.4f} ({category_accuracy*100:.2f}%)")
    
    # Sonuçları kaydet
    results_df = pd.DataFrame({
        'comment': df['comment'],
        'true_label': y_true,
        'predicted_label': y_pred,
        'confidence': confidences,
        'correct': [1 if t == p else 0 for t, p in zip(y_true, y_pred)]
    })
    
    output_path = DATA_DIR / "fewshot_evaluation_results.csv"
    results_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n💾 Detaylı sonuçlar kaydedildi: {output_path}")
    
    print("\n" + "=" * 80)
    print("DEĞERLENDİRME TAMAMLANDI")
    print("=" * 80)


if __name__ == "__main__":
    evaluate_fewshot_model()

