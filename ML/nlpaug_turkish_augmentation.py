import pandas as pd
import numpy as np
import random
import warnings
warnings.filterwarnings('ignore')

# NLPAug kütüphanelerini import et
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.char as nac

class TurkishNLPAugmentation:
    def __init__(self):
        # Random seed ayarla
        random.seed(35)
        np.random.seed(35)
        
        # Türkçe synonym sözlüğü
        self.turkish_synonyms = {
            'aptal': ['salak', 'ahmak', 'gerizekalı', 'budala', 'akılsız', 'düşüncesiz'],
            'boş': ['anlamsız', 'saçma', 'gereksiz', 'manasız', 'değersiz', 'işe yaramaz'],
            'kötü': ['berbat', 'fena', 'çirkin', 'rezil', 'korkunç', 'dehşet'],
            'güzel': ['hoş', 'şirin', 'tatlı', 'mükemmel', 'harika', 'muhteşem'],
            'harika': ['muhteşem', 'süper', 'mükemmel', 'olağanüstü', 'fevkalade', 'müthiş'],
            'çok': ['çok fazla', 'aşırı', 'fazlasıyla', 'oldukça', 'hayli', 'epey'],
            'sen': ['siz', 'seni', 'sizi', 'sana', 'size'],
            'ben': ['biz', 'bizi', 'bana', 'bize', 'beni'],
            'ne': ['nasıl', 'neden', 'niçin', 'niye', 'neden'],
            'yapıyorsun': ['ediyorsun', 'davranıyorsun', 'gösteriyorsun', 'sergiliyorsun'],
            'inanıyorsun': ['sanıyorsun', 'düşünüyorsun', 'zannediyorsun', 'varsayıyorsun'],
            'akıllı': ['zeki', 'akıllıca', 'mantıklı', 'bilgili', 'zeki', 'parlak'],
            'insan': ['kişi', 'birey', 'adam', 'kadın', 'fert', 'şahıs'],
            'davranıyorsun': ['hareket ediyorsun', 'davranış sergiliyorsun', 'gösteriyorsun'],
            'utanç': ['ayıp', 'rezalet', 'skandal', 'mahcubiyet', 'utanma'],
            'verici': ['yaratıcı', 'neden olan', 'sebep olan', 'doğuran'],
            'kaldırması': ['kaldırmak', 'yüklenmek', 'taşımak', 'kaldırma'],
            'kendini': ['kendinizi', 'seni', 'sizi', 'kendin'],
            'sanıyorsun': ['zannediyorsun', 'düşünüyorsun', 'inanıyorsun', 'varsayıyorsun']
        }
        
    def load_sample_data(self):
        """Sample dataset'i yükle ve temizle"""
        print("📊 Sample dataset yükleniyor...")
        
        try:
            # CSV'yi daha esnek şekilde oku
            df = pd.read_csv('sample_dataset.csv', encoding='utf-8', on_bad_lines='skip')
            print(f"✅ Toplam {len(df)} satır yüklendi")
            
            # Sadece text ve label sütunlarını al
            if 'text' in df.columns and 'label' in df.columns:
                df = df[['text', 'label']].dropna()
                print(f"✅ Temizlenmiş veri: {len(df)} satır")
            else:
                print("❌ 'text' ve 'label' sütunları bulunamadı!")
                return None
                
        except Exception as e:
            print(f"❌ Dosya okuma hatası: {e}")
            return None
            
        return df
    
    def analyze_labels(self, df):
        """Label dağılımını analiz et"""
        print(f"\n📊 Label Dağılımı:")
        label_counts = df['label'].value_counts().sort_index()
        for label, count in label_counts.items():
            print(f"   Label {label}: {count} adet")
        
        return label_counts
    
    def filter_non_zero_labels(self, df):
        """Sadece label 0 hariç diğer kategorileri al"""
        print(f"\n🎯 Label 0 hariç diğer kategoriler filtreleniyor...")
        
        # Label 0 hariç diğer kategoriler
        non_zero_df = df[df['label'] != 0].copy()
        
        print(f"✅ Label 0 hariç toplam: {len(non_zero_df)} örnek")
        
        # Label 0 hariç dağılım
        print(f"\n📊 Label 0 Hariç Dağılım:")
        label_counts = non_zero_df['label'].value_counts().sort_index()
        for label, count in label_counts.items():
            print(f"   Label {label}: {count} adet")
        
        return non_zero_df
    
    def turkish_synonym_augmentation(self, text):
        """Türkçe synonym augmentation - benzer anlamda farklı cümleler"""
        augmented_texts = [text]  # Orijinal metni ekle
        
        text_lower = text.lower()
        
        # Cümlenin genel anlamına göre tamamen farklı cümleler oluştur
        if 'yiyorsun' in text_lower and 'miden' in text_lower:
            alternatives = [
                'Çok fazla yemek yiyorsun, karnın şişmiş',
                'Aşırı yemek yiyorsun, miden patlayacak',
                'Fazla yemek yiyorsun, karnın büyümüş',
                'Çok yemek yiyorsun, miden genişlemiş',
                'Aşırı yemek yiyorsun, karnın şişmiş',
                'Fazla yemek yiyorsun, miden büyümüş'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'kapatmazsan' in text_lower and 'boş' in text_lower:
            alternatives = [
                'Ağzını kapatmazsan anlamsız konuşacaksın',
                'Ağzını kapatmazsan saçma sapan konuşacaksın',
                'Ağzını kapatmazsan gereksiz laflar edeceksin',
                'Ağzını kapatmazsan manasız şeyler söyleyeceksin',
                'Ağzını kapatmazsan boş laflar edeceksin',
                'Ağzını kapatmazsan anlamsız konuşacaksın'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'kendini' in text_lower and 'sanıyorsun' in text_lower:
            alternatives = [
                'Kendini çok büyük görüyorsun',
                'Haddini bilmiyorsun',
                'Kendini bir şey sanıyorsun',
                'Burnun havada',
                'Kibirli davranıyorsun',
                'Kendini üstün görüyorsun',
                'Haddinden fazla büyükleniyorsun',
                'Kendini çok önemli sanıyorsun'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'boş' in text_lower and 'yapıyorsun' in text_lower:
            alternatives = [
                'Hiçbir şey söylemiyorsun',
                'Laf salatası yapıyorsun',
                'Boş laflar ediyorsun',
                'Anlamsız konuşuyorsun',
                'Saçma sapan şeyler söylüyorsun',
                'Gereksiz yere konuşuyorsun',
                'Manasız laflar ediyorsun',
                'Boşuna nefes tüketiyorsun'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'akıllı' in text_lower and 'inanıyorsun' in text_lower:
            alternatives = [
                'Çok zeki olduğunu sanıyorsun',
                'Akıllı olduğuna inanıyorsun',
                'Bilgili olduğunu düşünüyorsun',
                'Mantıklı davrandığını sanıyorsun',
                'Çok akıllı olduğunu zannediyorsun',
                'Zeka küpü olduğunu düşünüyorsun',
                'Akıllıca hareket ettiğini sanıyorsun',
                'Bilge olduğunu zannediyorsun'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'aptal' in text_lower or 'salak' in text_lower:
            alternatives = [
                'Çok aptalca davranıyorsun',
                'Salak gibi hareket ediyorsun',
                'Ahmakça davranıyorsun',
                'Gerizekalı gibi davranıyorsun',
                'Akılsızca hareket ediyorsun',
                'Mantıksız davranıyorsun',
                'Düşüncesizce hareket ediyorsun',
                'Zeka seviyesi düşük davranıyorsun'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'utanç' in text_lower or 'ayıp' in text_lower:
            alternatives = [
                'Bu çok ayıp bir durum',
                'Rezil bir olay bu',
                'Utanç verici bir durum',
                'Skandal yaratacak bir hareket',
                'Mahcubiyet yaratan bir olay',
                'Ayıp veren bir davranış',
                'Rezil edici bir durum',
                'Utanılacak bir olay'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        elif 'insanlara' in text_lower and 'boşluk' in text_lower:
            alternatives = [
                'Senin gibi kişilere boşluk deniyor',
                'Senin gibi bireylere anlamsızlık deniyor',
                'Senin gibi insanlara saçmalık deniyor',
                'Senin gibi kişilere gereksizlik deniyor',
                'Senin gibi bireylere manasızlık deniyor',
                'Senin gibi insanlara boşluk deniyor',
                'Senin gibi kişilere anlamsızlık deniyor',
                'Senin gibi bireylere saçmalık deniyor'
            ]
            for alt in alternatives:
                augmented_texts.append(alt)
        
        return augmented_texts
    
    def nlpaug_synonym_augmentation(self, text):
        """NLPAug ile synonym augmentation"""
        try:
            # WordNet tabanlı synonym augmentation
            synonym_aug = naw.SynonymAug(aug_src='wordnet', lang='tur')
            augmented_text = synonym_aug.augment(text)
            return [text, augmented_text] if augmented_text != text else [text]
        except:
            # WordNet çalışmazsa manuel synonym kullan
            return self.turkish_synonym_augmentation(text)
    
    def nlpaug_random_swap(self, text):
        """NLPAug ile random word swap"""
        try:
            swap_aug = naw.RandomWordAug(action="swap", aug_p=0.3)
            augmented_text = swap_aug.augment(text)
            return [text, augmented_text] if augmented_text != text else [text]
        except:
            return [text]
    
    def nlpaug_random_deletion(self, text):
        """NLPAug ile random word deletion"""
        try:
            deletion_aug = naw.RandomWordAug(action="delete", aug_p=0.2)
            augmented_text = deletion_aug.augment(text)
            return [text, augmented_text] if augmented_text != text else [text]
        except:
            return [text]
    
    def nlpaug_random_insertion(self, text):
        """NLPAug ile random word insertion"""
        try:
            insertion_aug = naw.RandomWordAug(action="insert", aug_p=0.2)
            augmented_text = insertion_aug.augment(text)
            return [text, augmented_text] if augmented_text != text else [text]
        except:
            return [text]
    
    def apply_all_augmentations(self, df):
        """Tüm augmentation tekniklerini uygula"""
        print("📝 NLPAug ile metin augmentation başlıyor...")
        
        augmented_data = []
        
        for _, row in df.iterrows():
            text = row['text']
            label = row['label']
            
            # 1. Türkçe Synonym Augmentation
            synonym_texts = self.turkish_synonym_augmentation(text)
            for aug_text in synonym_texts:
                augmented_data.append({'text': aug_text, 'label': label})
            
            # 2. NLPAug Synonym (eğer çalışırsa)
            try:
                nlpaug_synonym_texts = self.nlpaug_synonym_augmentation(text)
                for aug_text in nlpaug_synonym_texts:
                    if aug_text not in [item['text'] for item in augmented_data[-len(synonym_texts):]]:
                        augmented_data.append({'text': aug_text, 'label': label})
            except:
                pass
            
            # 3. Random Word Swap
            swap_texts = self.nlpaug_random_swap(text)
            for aug_text in swap_texts:
                if aug_text not in [item['text'] for item in augmented_data]:
                    augmented_data.append({'text': aug_text, 'label': label})
            
            # 4. Random Word Deletion
            deletion_texts = self.nlpaug_random_deletion(text)
            for aug_text in deletion_texts:
                if aug_text not in [item['text'] for item in augmented_data]:
                    augmented_data.append({'text': aug_text, 'label': label})
            
            # 5. Random Word Insertion
            insertion_texts = self.nlpaug_random_insertion(text)
            for aug_text in insertion_texts:
                if aug_text not in [item['text'] for item in augmented_data]:
                    augmented_data.append({'text': aug_text, 'label': label})
        
        augmented_df = pd.DataFrame(augmented_data)
        print(f"✅ NLPAug augmentation: {len(df)} -> {len(augmented_df)} örnek")
        
        return augmented_df
    
    def save_augmented_data(self, df, filename):
        """Augmented verileri tek dosya olarak kaydet"""
        print(f"\n💾 {filename} verileri kaydediliyor...")
        
        # Tek CSV dosyası olarak kaydet
        df.to_csv(f'{filename}.csv', index=False)
        
        print(f"✅ {filename} verileri kaydedildi!")
        print(f"   - {filename}.csv")

def main():
    """Ana fonksiyon"""
    print("🚀 TÜRKÇE NLPAUG AUGMENTATION")
    print("=" * 50)
    
    # Augmentation sınıfını oluştur
    aug = TurkishNLPAugmentation()
    
    # Sample dataset'i yükle
    df = aug.load_sample_data()
    if df is None:
        return
    
    # Label dağılımını analiz et
    aug.analyze_labels(df)
    
    # Label 0 hariç kategorileri filtrele
    non_zero_df = aug.filter_non_zero_labels(df)
    
    if len(non_zero_df) == 0:
        print("❌ Label 0 hariç kategori bulunamadı!")
        return
    
    # NLPAug ile augmentation uygula
    print(f"\n{'='*20} NLPAUG AUGMENTATION {'='*20}")
    augmented_df = aug.apply_all_augmentations(non_zero_df)
    
    # Sonuçları kaydet
    aug.save_augmented_data(augmented_df, 'nlpaug_turkish_augmented')
    
    # Final dağılım
    print(f"\n📊 Final Dağılım:")
    final_counts = augmented_df['label'].value_counts().sort_index()
    for label, count in final_counts.items():
        print(f"   Label {label}: {count} adet")
    
    print(f"\n🎉 NLPAug Türkçe augmentation tamamlandı!")
    print(f"📁 Augmented veriler 'nlpaug_turkish_augmented.csv' olarak kaydedildi")

if __name__ == "__main__":
    main()
