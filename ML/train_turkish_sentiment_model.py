#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Türkçe Duygu/Saldırganlık Analizi Modeli Eğitimi
BERTurk ve ElecTRa-tr modelleri ile fine-tuning
"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import warnings
warnings.filterwarnings('ignore')

# CUDA kontrolü
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Kullanılan cihaz: {device}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Yok'}")

class TurkishSentimentDataset(Dataset):
    """Türkçe duygu analizi veri seti"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def load_and_preprocess_data(file_path):
    """Veri setini yükle ve ön işle"""
    print("Veri seti yükleniyor...")
    df = pd.read_csv(file_path)
    
    # Veri temizliği
    df = df.dropna()
    df['text'] = df['text'].astype(str)
    df['label'] = pd.to_numeric(df['label'], errors='coerce')
    df = df.dropna()
    
    # Label'ları temizle (sadece 0-4 arası sayıları kabul et)
    df = df[df['label'].isin([0, 1, 2, 3, 4])]
    
    print(f"Temizlenmiş veri seti boyutu: {len(df)}")
    print(f"Label dağılımı:")
    print(df['label'].value_counts().sort_index())
    
    return df

def compute_metrics(eval_pred):
    """Model performans metrikleri"""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
    accuracy = accuracy_score(labels, predictions)
    
    return {
        'accuracy': accuracy,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def train_model(model_name, train_dataset, val_dataset, num_labels=5, output_dir=None):
    """Model eğitimi"""
    print(f"\n{model_name} modeli eğitiliyor...")
    
    # Tokenizer ve model yükle
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        problem_type="single_label_classification"
    )
    
    # Model'i GPU'ya taşı
    model.to(device)
    
    # Eğitim parametreleri
    training_args = TrainingArguments(
        output_dir=output_dir or f'./results_{model_name.replace("/", "_")}',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f'./logs_{model_name.replace("/", "_")}',
        logging_steps=100,
        evaluation_strategy="steps",
        eval_steps=500,
        save_strategy="steps",
        save_steps=500,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        report_to=None,  # TensorBoard'u kapat
        save_total_limit=2,
        learning_rate=2e-5,
        fp16=torch.cuda.is_available(),  # GPU varsa mixed precision kullan
    )
    
    # Trainer oluştur
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    # Eğitimi başlat
    print("Eğitim başlıyor...")
    trainer.train()
    
    # En iyi modeli kaydet
    trainer.save_model()
    tokenizer.save_pretrained(output_dir or f'./results_{model_name.replace("/", "_")}')
    
    # Test seti üzerinde değerlendirme
    print("\nModel değerlendiriliyor...")
    eval_results = trainer.evaluate()
    print(f"Değerlendirme sonuçları: {eval_results}")
    
    return trainer, tokenizer, model

def main():
    """Ana fonksiyon"""
    # Veri setini yükle
    df = load_and_preprocess_data('E:/Melike/IBM/ml_model/nlpaug_turkish_augmented.csv')
    
    # Train/validation split
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].values, df['label'].values, 
        test_size=0.2, random_state=42, stratify=df['label']
    )
    
    print(f"Eğitim seti: {len(train_texts)} örnek")
    print(f"Validation seti: {len(val_texts)} örnek")
    
    # Türkçe modeller
    models = [
        "dbmdz/bert-base-turkish-cased",  # BERTurk
        "dbmdz/electra-base-turkish-discriminator"  # ElecTRa-tr (doğru model adı)
    ]
    
    results = {}
    
    for model_name in models:
        print(f"\n{'='*60}")
        print(f"Model: {model_name}")
        print(f"{'='*60}")
        
        try:
            # Tokenizer yükle
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Dataset'leri oluştur
            train_dataset = TurkishSentimentDataset(train_texts, train_labels, tokenizer)
            val_dataset = TurkishSentimentDataset(val_texts, val_labels, tokenizer)
            
            # Model eğit
            trainer, tokenizer, model = train_model(
                model_name, train_dataset, val_dataset,
                num_labels=5,
                output_dir=f'./turkish_sentiment_{model_name.replace("/", "_")}'
            )
            
            # Sonuçları kaydet
            results[model_name] = trainer.evaluate()
            
            # Model'i temizle (GPU memory için)
            del model, trainer, tokenizer
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"Hata: {model_name} eğitilirken hata oluştu: {str(e)}")
            continue
    
    # Sonuçları yazdır
    print(f"\n{'='*60}")
    print("FINAL SONUÇLAR")
    print(f"{'='*60}")
    
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")

if __name__ == "__main__":
    main()
