#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Instagram Comments Scraper - Advanced XPath Method
Instagram yorumlarını XPath ile çeken gelişmiş scraper
"""

import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import (
    INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, DEFAULT_MAX_COMMENTS,
    SCROLL_TIMEOUT, SCROLL_DELAY, LONG_SCROLL_DELAY, CHROME_OPTIONS,
    COMMENT_XPATH, USERNAME_XPATH, LOGIN_BUTTON_XPATH, NOT_NOW_BUTTON_XPATH
)
from config import DATA_DIR

def scrape_instagram_comments(post_url, max_comments=DEFAULT_MAX_COMMENTS, username=None, password=None):
    """Advanced XPath method ile Instagram yorumlarını çek"""
    
    # Use default credentials if not provided
    username = username or INSTAGRAM_USERNAME
    password = password or INSTAGRAM_PASSWORD
    
    post_owner = None  # Post sahibinin kullanıcı adı
    
    # Chrome WebDriver kurulum
    chrome_options = ChromeOptions()
    for option in CHROME_OPTIONS:
        chrome_options.add_argument(option)
    
    # Timeout ayarları
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Headless modda maximize_window() kullanma
        driver.set_page_load_timeout(30)  # 30 saniye timeout (azaltıldı)
        driver.set_script_timeout(20)  # 20 saniye (azaltıldı)
        
        print(f"Post sayfasina gidiliyor: {post_url}")
        driver.get(post_url)
        time.sleep(5)  # Sayfa yüklenmesini bekle (azaltıldı: 10→5)
        
        # Popup'tan giriş yapma
        if username and password:
            try:
                # "Giriş yap" butonunu bul ve tıkla
                login_button = driver.find_element(By.XPATH, LOGIN_BUTTON_XPATH)
                print("Giris yap popup'i bulundu, giris yapiliyor...")
                login_button.click()
                time.sleep(3)
                
                # Kullanıcı adı alanını bul ve doldur
                username_field = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
                username_field.clear()
                username_field.send_keys(username)
                time.sleep(2)
                
                # Şifre alanını bul ve doldur
                password_field = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
                password_field.clear()
                password_field.send_keys(password)
                time.sleep(2)
                
                # Giriş butonuna tıkla
                submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_button.click()
                time.sleep(5)  # Azaltıldı: 8→5
                
                print("Popup'tan giris yapildi!")
                
                # Giriş bilgilerini kaydetme uyarısını geç
                try:
                    not_now_button = driver.find_element(By.XPATH, NOT_NOW_BUTTON_XPATH)
                    print("Giris bilgilerini kaydetme uyarisi bulundu, 'Simdi degil' seciliyor...")
                    not_now_button.click()
                    time.sleep(3)
                except Exception as e:
                    print(f"Giris bilgilerini kaydetme uyarisi bulunamadi: {e}")
                
                # Ana sayfaya yönlendirildikten sonra tekrar post URL'sine git
                print("Ana sayfaya yonlendirildi, tekrar post sayfasina gidiliyor...")
                driver.get(post_url)
                time.sleep(5)  # Post sayfasının yüklenmesini bekle (azaltıldı: 10→5)
                
            except Exception as e:
                print(f"Popup giris yapilamadi: {e}")
                pass
        
        # Post sahibinin kullanıcı adını al (SCROLL YAPMADAN ÖNCE!)
        post_owner = None
        try:
            print("\n" + "="*50)
            print("POST SAHİBİ ARANIYOR...")
            print("="*50)
            
            # Yöntem 1: Tüm span'leri tara, username'e benzer olanı bul
            try:
                all_spans = driver.find_elements(By.TAG_NAME, 'span')
                print(f"Toplam {len(all_spans)} span elementi bulundu")
                
                # İlk 30 span'i kontrol et
                for idx, span in enumerate(all_spans[:30]):
                    try:
                        text = span.text.strip()
                        # Username kriterleri: 3-30 karakter, boşluksuz, özel karakter yok
                        if (text and 
                            3 < len(text) < 30 and 
                            ' ' not in text and 
                            '\n' not in text and
                            '?' not in text and
                            '@' not in text and
                            not text.isdigit() and
                            text.lower() not in ['takip', 'following', 'followers', 'posts', 'reels', 'tagged']):
                            
                            # Parent'ı kontrol et - header içinde mi?
                            parent_html = driver.execute_script("return arguments[0].parentElement.parentElement.parentElement.tagName", span)
                            if parent_html and parent_html.upper() in ['HEADER', 'A', 'DIV']:
                                post_owner = text
                                print(f"✓✓✓ Post sahibi BULUNDU (Span #{idx}): {post_owner}")
                                break
                    except:
                        continue
                        
                if post_owner:
                    print(f"✅ SUCCESS: {post_owner}")
            except Exception as e:
                print(f"Yöntem 1 başarısız: {e}")
            
            # Yöntem 2: Header a tag'lerinin text'lerini kontrol et
            if not post_owner:
                try:
                    header_links = driver.find_elements(By.CSS_SELECTOR, 'header a')
                    print(f"Header'da {len(header_links)} link bulundu")
                    for idx, link in enumerate(header_links[:10]):
                        text = link.text.strip()
                        print(f"  Link {idx} text: '{text}'")
                        if text and 3 < len(text) < 30 and ' ' not in text and '?' not in text:
                            post_owner = text
                            print(f"✓ Post sahibi (Header Link Text): {post_owner}")
                            break
                except Exception as e:
                    print(f"Yöntem 2 başarısız: {e}")
            
            # Yöntem 3: Article section içindeki ilk birkaç link'in text'i
            if not post_owner:
                try:
                    article_links = driver.find_elements(By.CSS_SELECTOR, 'article a')
                    for idx, link in enumerate(article_links[:15]):
                        text = link.text.strip()
                        if text and 3 < len(text) < 30 and ' ' not in text and '?' not in text:
                            post_owner = text
                            print(f"✓ Post sahibi (Article Link Text): {post_owner}")
                            break
                except Exception as e:
                    print(f"Yöntem 3 başarısız: {e}")
            
            if not post_owner:
                print("❌ POST SAHİBİ BULUNAMADI!")
                
        except Exception as e:
            print(f"❌ HATA: {e}")
        
        print(f"\n{'='*50}")
        print(f"FINAL POST SAHİBİ: {post_owner}")
        print("="*50 + "\n")
        
        # XPath ile yorumları bul
        xpath = COMMENT_XPATH
        
        print("XPath ile yorumlar araniyor...")
        comments = driver.find_elements(By.XPATH, xpath)
        
        if len(comments) > 0:
            print(f"İlk yorum bulundu, scroll container araniyor...")
            first_comment = comments[0]
            
            # Scroll container'ı bul
            scroll_container = driver.execute_script("""
            let el = arguments[0];
            function isScrollable(node){
                const style = window.getComputedStyle(node);
                const y = style.overflowY;
                return (y === 'auto' || y === 'scroll') && node.scrollHeight > node.clientHeight;
            }
            while (el && el !== document.body){
                if (isScrollable(el)) return el;
                el = el.parentElement;
            }
            return document.scrollingElement || document.documentElement;
            """, first_comment)
            
            print("Scroll container bulundu, yorumlar yukleniyor...")
            
            # Scroll yaparak daha fazla yorum yükle
            last_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 100  # Daha fazla scroll denemesi
            start_time = time.time()
            max_duration = SCROLL_TIMEOUT  # 2 dakika
            
            while scroll_attempts < max_scroll_attempts:
                # 2 dakika kontrolü
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_duration:
                    print(f"2 dakika doldu, scroll durduruluyor... (Toplam süre: {elapsed_time:.1f} saniye)")
                    break
                
                new_height = driver.execute_script(
                    "return arguments[0].scrollHeight;", scroll_container
                )
                
                driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    scroll_container
                )
                
                # 3. scroll'dan sonra daha uzun bekleme
                if scroll_attempts >= 2:
                    print("3. scroll'dan sonra uzun bekleme...")
                    time.sleep(LONG_SCROLL_DELAY)  # 10 saniye bekleme
                else:
                    time.sleep(SCROLL_DELAY)  # Normal bekleme
                
                if new_height == last_height:  # yeni yükleme olmadıysa dur
                    print("Yeni yorum yuklenmedi, scroll durduruluyor...")
                    break
                
                # Yeterli yorum bulundu mu kontrol et
                current_comments = driver.find_elements(By.XPATH, xpath)
                current_texts = [c.text.strip() for c in current_comments if c.text.strip()]
                
                if max_comments > 0 and len(current_texts) >= max_comments:
                    print(f"İstenen yorum sayısı ({max_comments}) bulundu, scroll durduruluyor...")
                    break
                
                last_height = new_height
                scroll_attempts += 1
                elapsed_time = time.time() - start_time
                print(f"Scroll {scroll_attempts}: Yeni yukseklik: {new_height}, Bulunan yorum: {len(current_texts)} (Geçen süre: {elapsed_time:.1f}s)")
            
            # Güncel yorumları al
            comments = driver.find_elements(By.XPATH, xpath)
            
            texts = [c.text.strip() for c in comments if c.text.strip()]
            
            print(f"Toplam {len(texts)} yorum bulundu")
            
            # Eğer max_comments çok küçükse, bulunan yorum sayısını kullan
            actual_limit = min(len(texts), max_comments) if max_comments > 0 else len(texts)
            print(f"İşlenecek yorum sayısı: {actual_limit}")
            
            # Yorumları formatla - her yorum için kendi container'ından kullanıcı adını al
            formatted_comments = []
            empty_count = 0
            for i, text in enumerate(texts[:actual_limit]):
                if text and len(text.strip()) > 0:  # Sadece boş olmayanları al
                    try:
                        # Her yorum için kendi container'ından kullanıcı adını bul
                        comment_element = comments[i]
                        
                        # Yorumun parent container'ından kullanıcı adını ara
                        try:
                            # Yorumun üst container'ında kullanıcı adını ara
                            username_element = comment_element.find_element(By.XPATH, "./ancestor::div[contains(@class, '_ae5q') or contains(@class, '_ae5r')]//a[contains(@href,'/')]/span[@class='_ap3a _aaco _aacw _aacx _aad7 _aade']")
                            author_name = username_element.text.strip()
                        except:
                            try:
                                # Alternatif yol: yorumun üstündeki a elementinden kullanıcı adını al
                                username_element = comment_element.find_element(By.XPATH, "./ancestor::div[contains(@class, '_ae5q') or contains(@class, '_ae5r')]//a[contains(@href,'/')]//span")
                                author_name = username_element.text.strip()
                            except:
                                try:
                                    # Başka bir alternatif: yorumun parent'ından kullanıcı adını ara
                                    username_element = comment_element.find_element(By.XPATH, "./ancestor::div[1]/preceding-sibling::div//a//span")
                                    author_name = username_element.text.strip()
                                except:
                                    # Son çare: sıra numarası kullan
                                    author_name = f"user_{i+1}"
                        
                    except Exception as e:
                        print(f"Kullanıcı adı bulunamadı yorum {i+1}: {e}")
                        author_name = f"user_{i+1}"
                    
                    formatted_comment = {
                        'text': text.strip(),  # Sadece başta/sonda boşluk temizle
                        'author': author_name,
                        'likes': 0,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'platform': 'instagram',
                        'comment_id': f"xpath_{i+1}"
                    }
                    formatted_comments.append(formatted_comment)
                else:
                    empty_count += 1
                    print(f"Boş yorum atlandı #{i+1}: '{text}'")
            
            print(f"Sonuc: {len(formatted_comments)} yorum cekildi")
            print(f"Filtrelenen yorum sayısı: {actual_limit - len(formatted_comments)}")
            print(f"Başarı oranı: {(len(formatted_comments)/actual_limit)*100:.1f}%")
            
            # Post sahibi bilgisini ekle
            result = {
                'comments': formatted_comments,
                'post_owner': post_owner,
                'total_comments': len(formatted_comments)
            }
            
            return result
        else:
            print("Hic yorum bulunamadi")
            return {
                'comments': [],
                'post_owner': post_owner or 'unknown',
                'total_comments': 0
            }
            
    except Exception as e:
        print(f"Hata: {e}")
        return {
            'comments': [],
            'post_owner': 'unknown',
            'total_comments': 0
        }
    finally:
        if driver:
            try:
                driver.quit()
                print("Chrome driver kapatıldı")
            except Exception as e:
                print(f"Driver kapatma hatası: {e}")

# Test
if __name__ == "__main__":
    print("Instagram Comments Scraper - Advanced XPath Method")
    print("=" * 50)
    
    # Test URL
    test_url = "https://www.instagram.com/p/DNJPCfno8s4/?hl=tr&img_index=1"
    
    print(f"Test URL: {test_url}")
    
    # Yorumları çek (config'den otomatik kullanıcı adı/şifre)
    comments = scrape_instagram_comments(test_url, max_comments=100)
    
    print(f"\nSonuc: {len(comments)} yorum cekildi")
    
    if comments: 
        print("\n" + "="*80)
        print("TÜM ÇEKİLEN YORUMLAR:")
        print("="*80)
        
        for i, comment in enumerate(comments, 1):
            print(f"\n{i}. @{comment['author']}:")
            print(f"   Metin: {comment['text']}")
            print(f"   Platform: {comment['platform']}")
            print(f"   Timestamp: {comment['timestamp']}")
            print("-" * 60)
        
        # JSON dosyasına kaydet
        filename = f"instagram_comments_xpath_{int(time.time())}.json"
        filepath = DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        print(f"\nYorumlar {filepath} dosyasina kaydedildi")
        
    else:
        print("Hic yorum cekilemedi")
