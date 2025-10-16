// SOSYAL MEDYA ANALİZİ - DASHBOARD İÇERİĞİ (ŞİMDİ HOMEPAGE)
import React, { useState, useCallback } from 'react';
import { 
  FaSearch, FaPlay, FaCog, FaChartBar, FaExclamationTriangle, 
  FaComments, FaUsers, FaEye, FaEyeSlash, FaCopy, FaCircle, FaUser, FaClock 
} from 'react-icons/fa';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { useAuth } from '../context/AuthContext';

// Chart.js'i kaydet
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const HomePage = () => {
  const { api } = useAuth(); // Auth context'ten api instance'ını al
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [maxComments, setMaxComments] = useState(10);
  const [threshold, setThreshold] = useState(80);
  const [scrapingMode, setScrapingMode] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [analysis, setAnalysis] = useState(null);
  const [showComments, setShowComments] = useState(true);
  const [commentSearch, setCommentSearch] = useState('');
  const [commentFilter, setCommentFilter] = useState('all');
  const [commentSort, setCommentSort] = useState('newest');
  const [apiStatus, setApiStatus] = useState('checking');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserModal, setShowUserModal] = useState(false);

  const checkApiStatus = useCallback(async () => {
    try {
      const response = await api.get('/api/health');
      setApiStatus('connected');
    } catch (error) {
      setApiStatus('disconnected');
    }
  }, [api]);

  React.useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiStatus]);

  const analyzeSocialMedia = async () => {
    if (!url.trim()) {
      alert('Lütfen bir sosyal medya URL\'si girin!');
      return;
    }

    setLoading(true);
    setLoadingProgress(0);
    setAnalysis(null);

    // Progress bar animasyonu
    const progressInterval = setInterval(() => {
      setLoadingProgress(prev => {
        if (prev >= 90) return prev; // 90'da dur, tamamlandığında 100'e gider
        return prev + Math.random() * 15;
      });
    }, 1000);

    try {
      const response = await api.post('/api/social-media-analysis', {
        url: url,
        max_comments: maxComments,
        threshold: threshold / 100,
        scraping_mode: scrapingMode
      }, {
        timeout: 0  // Timeout yok
      });

      setLoadingProgress(100); // İşlem tamamlandı
      setAnalysis(response.data);
      
      // Debug: Response'u console'a yazdır
      console.log('Analiz Sonucu:', response.data);
      console.log('Post Owner:', response.data.post_owner);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      alert('Hata: ' + errorMessage);
      console.error('Analiz hatası:', error);
    } finally {
      clearInterval(progressInterval);
      setTimeout(() => {
        setLoading(false);
        setLoadingProgress(0);
      }, 500);
    }
  };

  const copyComment = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Başarı mesajı göster
      const toast = document.createElement('div');
      toast.className = 'toast position-fixed top-0 end-0 m-3';
      toast.innerHTML = `
        <div class="toast-body bg-success text-white">
          <i class="fas fa-check me-2"></i>Yorum kopyalandı!
        </div>
      `;
      document.body.appendChild(toast);
      
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 3000);
    });
  };

  const isCommentHarmful = (comment) => {
    // AI tahmin sonucu varsa onu kullan
    if (comment.predicted_category_id !== undefined) {
      return comment.predicted_category_id > 0; // 0 = Güvenli, 1-4 = Zararlı
    }
    
    // Fallback: basit kelime kontrolü
    const harmfulKeywords = [
      'gerizekalı', 'aptal', 'salak', 'mal', 'dangalak', 'defol',
      'kadınlar', 'erkek', 'adam', 'şişman', 'zayıf', 'çirkin'
    ];
    
    const lowerText = (comment.text || '').toLowerCase();
    return harmfulKeywords.some(keyword => lowerText.includes(keyword));
  };

  const getCategoryName = (categoryId) => {
    const categoryNames = {
      0: 'Zararsız / Nötr',
      1: 'Doğrudan Hakaret / Küfür',
      2: 'Cinsiyetçi / Cinsel İmada',
      3: 'Alaycılık / Mikroagresyon',
      4: 'Görünüm Temelli Eleştiri'
    };
    return categoryNames[categoryId] || 'Zararsız / Nötr';
  };

  const getFilteredComments = () => {
    if (!analysis?.comments) return [];
    
    let filtered = analysis.comments;
    
    // Arama filtresi
    if (commentSearch) {
      const searchTerm = commentSearch.toLowerCase();
      filtered = filtered.filter(comment => 
        (comment.text || '').toLowerCase().includes(searchTerm) ||
        (comment.author || '').toLowerCase().includes(searchTerm)
      );
    }
    
    // Zararlı/Güvenli filtresi
    if (commentFilter === 'harmful') {
      filtered = filtered.filter(comment => isCommentHarmful(comment));
    } else if (commentFilter === 'safe') {
      filtered = filtered.filter(comment => !isCommentHarmful(comment));
    }
    
    // Sıralama
    filtered.sort((a, b) => {
      if (commentSort === 'author') {
        return (a.author || '').localeCompare(b.author || '');
      } else if (commentSort === 'newest') {
        return new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
      } else if (commentSort === 'oldest') {
        return new Date(a.timestamp || 0) - new Date(b.timestamp || 0);
      }
      return 0;
    });
    
    return filtered;
  };

  const getRiskChartData = () => {
    if (!analysis?.user_analyses) return null;
    
    const riskCounts = {
      'high_risk': 0,
      'medium_risk': 0,
      'low_risk': 0,
      'safe': 0
    };
    
    Object.values(analysis.user_analyses).forEach(user => {
      riskCounts[user.risk_category]++;
    });
    
    return {
      labels: ['Yüksek Risk', 'Orta Risk', 'Düşük Risk', 'Güvenli'],
      datasets: [{
        data: Object.values(riskCounts),
        backgroundColor: ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60'],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    };
  };

  const getPlatformChartData = () => {
    if (!analysis) return null;
    
    return {
      labels: ['Toplam Yorum', 'Analiz Edilen Kullanıcı', 'Tespit Edilen'],
      datasets: [{
        label: 'Sayılar',
        data: [analysis.total_comments, analysis.analyzed_users, analysis.flagged_users],
        backgroundColor: ['#3498db', '#2ecc71', '#e74c3c'],
        borderWidth: 1
      }]
    };
  };

  const getRiskText = (category) => {
    const riskTexts = {
      'high_risk': 'Yüksek Risk',
      'medium_risk': 'Orta Risk',
      'low_risk': 'Düşük Risk',
      'safe': 'Güvenli'
    };
    return riskTexts[category] || category;
  };

  const showUserDetails = (userId, user) => {
    setSelectedUser({ userId, ...user });
    setShowUserModal(true);
  };

  const closeUserModal = () => {
    setShowUserModal(false);
    setSelectedUser(null);
  };

  return (
    <div>
      {/* API Status */}
      <div className="api-status">
        <span className={`badge ${apiStatus === 'connected' ? 'bg-success' : 'bg-danger'}`}>
          <FaCircle className="me-1" />
          {apiStatus === 'connected' ? 'API Bağlı' : 'API Bağlantısı Yok'}
        </span>
      </div>

      {/* Modern Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-content-modern">
            {/* Modern Spinner */}
            <div className="loading-icon-wrapper">
              <div className="spinner-modern"></div>
            </div>
            
            {/* Başlık */}
            <h4 className="loading-title">Sosyal Medya Analizi Yapılıyor</h4>
            
            {/* Açıklama */}
            <p className="loading-description">
              {scrapingMode === 'advanced' 
                ? 'Gelişmiş Selenium ile yorumlar çekiliyor ve AI ile analiz ediliyor...'
                : 'Instagram yorumları çekiliyor ve AI ile analiz ediliyor...'
              }
            </p>
            
            {/* Progress Bar */}
            <div className="progress-bar-container">
              <div className="progress-bar-modern">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${loadingProgress}%` }}
                >
                  <span className="progress-percentage">{Math.round(loadingProgress)}%</span>
                </div>
              </div>
            </div>
            
            {/* Tahmini Süre */}
            <div className="estimated-time">
              <FaClock className="me-2" />
              <span>Tahmini Süre: 5-10 dakika</span>
            </div>
            
            {/* Bilgilendirme */}
            <p className="loading-info">
              Lütfen sayfayı kapatmayın, işlem devam ediyor...
            </p>
          </div>
        </div>
      )}

      <div className="container py-4">
        {/* Ana Analiz Bölümü */}
        <div className="analysis-section">
          <div className="row align-items-center mb-4">
            <div className="col-md-12">
              <h2 className="mb-3">
                <FaSearch className="me-2 text-primary" />
                Sosyal Medya Analizi
              </h2>
              <p className="text-muted">Instagram URL'lerini analiz edin ve zararlı içerikleri tespit edin</p>
            </div>
          </div>
          
          <div className="row">
            <div className="col-md-7">
              <input 
                type="text" 
                className="form-control url-input" 
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Instagram post URL'sini buraya yapıştırın"
              />
              <small className="text-muted mt-2 d-block">
                <i className="fas fa-lightbulb me-1" style={{ color: '#f39c12' }}></i>
                Örnek URL: 
                <button 
                  className="btn btn-link btn-sm p-0 ms-1"
                  style={{ textDecoration: 'none', fontSize: '0.875rem' }}
                  onClick={() => setUrl('https://www.instagram.com/p/DPErH0FDHom/')}
                >
                  <i className="fas fa-copy me-1"></i>
                  https://www.instagram.com/p/DPErH0FDHom/
                </button>
              </small>
            </div>
            <div className="col-md-2">
              <select 
                className="form-select" 
                style={{ 
                  borderRadius: '25px',
                  border: '2px solid #e9ecef',
                  padding: '1rem 1.5rem',
                  fontSize: '1.1rem'
                }}
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
              >
                <option value="instagram">
                  <i className="fab fa-instagram"></i> Instagram
                </option>
              </select>
            </div>
            <div className="col-md-3">
              <button 
                className="btn btn-analyze w-100" 
                onClick={analyzeSocialMedia}
                disabled={loading}
              >
                <FaPlay className="me-2" />
                Analiz Et
              </button>
            </div>
          </div>
          
          <div className="row mt-3">
            <div className="col-md-4">
              <label className="form-label">Maksimum Yorum Sayısı</label>
              <select 
                className="form-select" 
                value={maxComments}
                onChange={(e) => setMaxComments(parseInt(e.target.value))}
              >
                <option value={10}>10 Yorum (Deneme)</option>
                <option value={50}>50 Yorum (Hızlı)</option>
                <option value={100}>100 Yorum (Standart)</option>
                <option value={200}>200 Yorum (Detaylı)</option>
                <option value={500}>500 Yorum (Kapsamlı)</option>
                <option value={0}>Tüm Yorumları Çek</option>
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Tespit Eşiği ({threshold}%)</label>
              <input 
                type="range" 
                className="form-range" 
                min="0" 
                max="100" 
                value={threshold}
                onChange={(e) => setThreshold(parseInt(e.target.value))}
              />
              <div className="d-flex justify-content-between">
                <small>0%</small>
                <small>{threshold}%</small>
                <small>100%</small>
              </div>
            </div>
              <div className="col-md-4">
                <label className="form-label">Scraping Modu</label>
                <select 
                  className="form-select" 
                  value={scrapingMode}
                  onChange={(e) => setScrapingMode(e.target.value)}
                >
                  <option value="standard">Standart (Selenium)</option>
                </select>
              </div>
          </div>
        </div>

        {/* Sonuçlar Bölümü */}
        {analysis && (
          <div>
            {/* Post Sahibi Bilgisi */}
            {analysis.post_owner && analysis.post_owner !== 'unknown' && (
              <div className="card mb-4" style={{ 
                background: 'white',
                border: 'none',
                borderRadius: '15px',
                boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                overflow: 'hidden'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  padding: '0.5rem 1.5rem'
                }}>
                  <small className="text-white fw-bold">
                    <i className="fas fa-image me-2"></i>
                    POST SAHİBİ
                  </small>
                </div>
                <div className="card-body p-4">
                  <div className="d-flex align-items-center">
                    <div className="me-4">
                      <div className="rounded-circle d-flex align-items-center justify-content-center" style={{ 
                        width: '70px', 
                        height: '70px',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        boxShadow: '0 8px 20px rgba(102, 126, 234, 0.3)'
                      }}>
                        <FaUser style={{ fontSize: '2rem', color: 'white' }} />
                      </div>
                    </div>
                    <div className="flex-grow-1">
                      <h3 className="mb-2" style={{ color: '#2c3e50' }}>
                        <i className="fas fa-at me-2" style={{ color: '#667eea' }}></i>
                        <strong>{analysis.post_owner}</strong>
                      </h3>
                      <p className="mb-0" style={{ color: '#7f8c8d', fontSize: '0.95rem' }}>
                        <i className="fab fa-instagram me-2" style={{ color: '#E4405F' }}></i>
                        Instagram Profil Sahibi
                      </p>
                    </div>
                    <div>
                      <a 
                        href={`https://www.instagram.com/${analysis.post_owner}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-sm"
                        style={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          borderRadius: '20px',
                          padding: '0.5rem 1.5rem',
                          fontWeight: '600'
                        }}
                      >
                        <i className="fas fa-external-link-alt me-2"></i>
                        Profili Görüntüle
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Özet İstatistikler */}
            <div className="row mb-4">
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="card-body text-center">
                    <div className="stat-number">{analysis.total_comments}</div>
                    <div className="stat-label">Toplam Yorum</div>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="card-body text-center">
                    <div className="stat-number">{analysis.analyzed_users}</div>
                    <div className="stat-label">Analiz Edilen Kullanıcı</div>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="card-body text-center">
                    <div className="stat-number text-warning">{analysis.flagged_users}</div>
                    <div className="stat-label">Tespit Edilen Kullanıcı</div>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="card-body text-center">
                    <div className="stat-number">{analysis.platform?.toUpperCase() || '-'}</div>
                    <div className="stat-label">Platform</div>
                  </div>
                </div>
              </div>
                </div>

            {/* Risk Dağılımı Grafiği */}
            <div className="row mb-4">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h5 className="mb-0">
                      <FaChartBar className="me-2" />
                      Risk Dağılımı
                    </h5>
                  </div>
                  <div className="card-body">
                    <div className="chart-container">
                      {getRiskChartData() && (
                        <Doughnut 
                          data={getRiskChartData()} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: {
                                position: 'bottom'
                              }
                            }
                          }}
                        />
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h5 className="mb-0">
                      <FaChartBar className="me-2" />
                      Platform İstatistikleri
                    </h5>
                  </div>
                  <div className="card-body">
                    <div className="chart-container">
                      {getPlatformChartData() && (
                        <Bar 
                          data={getPlatformChartData()} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                              y: {
                                beginAtZero: true
                              }
                            }
                          }}
                        />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tespit Edilen Kullanıcılar */}
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <FaExclamationTriangle className="me-2 text-warning" />
                  Tespit Edilen Kullanıcılar
                </h5>
              </div>
              <div className="card-body">
                {Object.entries(analysis.user_analyses || {})
                  .filter(([_, user]) => user.flagged)
                  .length === 0 ? (
                  <div className="alert alert-success">
                    <FaCircle className="me-2" />
                    Tespit edilen kullanıcı bulunamadı!
                  </div>
                ) : (
                  Object.entries(analysis.user_analyses || {})
                    .filter(([_, user]) => user.flagged)
                    .map(([userId, user]) => (
                      <div key={userId} className="card user-card flagged mb-3">
                        <div className="card-body">
                          <div className="row align-items-center">
                            <div className="col-md-3">
                              <h6 className="mb-1">@{userId}</h6>
                              <span className={`risk-badge risk-${user.risk_category}`}>
                                {getRiskText(user.risk_category)}
                      </span>
                            </div>
                            <div className="col-md-2">
                              <small className="text-muted">Toplam Yorum</small>
                              <div className="fw-bold">{user.total_comments}</div>
                            </div>
                            <div className="col-md-2">
                              <small className="text-muted">Zararlı Yorum</small>
                              <div className="fw-bold text-danger">{user.harmful_comments}</div>
                            </div>
                            <div className="col-md-2">
                              <small className="text-muted">Zararlı Oranı</small>
                              <div className="fw-bold">{(user.harmful_ratio * 100).toFixed(1)}%</div>
                            </div>
                            <div className="col-md-3">
                              <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => showUserDetails(userId, user)}
                              >
                                <FaEye className="me-1" />
                                Detaylar
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                )}
              </div>
            </div>

            {/* Yorum Detayları */}
            <div className="card mt-4">
              <div className="card-header">
                <h5 className="mb-0">
                  <FaComments className="me-2 text-info" />
                  Yorum Detayları
                  <button 
                    className="btn btn-sm btn-outline-secondary float-end" 
                    onClick={() => setShowComments(!showComments)}
                  >
                    {showComments ? <FaEyeSlash className="me-1" /> : <FaEye className="me-1" />}
                    {showComments ? 'Gizle' : 'Göster'}
                  </button>
                </h5>
              </div>
              {showComments && (
                <div className="card-body">
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <input 
                        type="text" 
                        className="form-control" 
                        value={commentSearch}
                        onChange={(e) => setCommentSearch(e.target.value)}
                        placeholder="Yorumlarda ara..."
                      />
                    </div>
                    <div className="col-md-3">
                      <select 
                        className="form-select" 
                        value={commentFilter}
                        onChange={(e) => setCommentFilter(e.target.value)}
                      >
                        <option value="all">Tüm Yorumlar</option>
                        <option value="harmful">Zararlı Yorumlar</option>
                        <option value="safe">Güvenli Yorumlar</option>
                      </select>
                    </div>
                    <div className="col-md-3">
                      <select 
                        className="form-select" 
                        value={commentSort}
                        onChange={(e) => setCommentSort(e.target.value)}
                      >
                        <option value="newest">En Yeni</option>
                        <option value="oldest">En Eski</option>
                        <option value="author">Yazara Göre</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    {getFilteredComments().length === 0 ? (
                      <div className="alert alert-info">
                        <FaCircle className="me-2" />
                        Yorum bulunamadı!
                </div>
                    ) : (
                      getFilteredComments().map((comment, index) => {
                        const harmful = isCommentHarmful(comment);
                        const categoryId = comment.predicted_category_id !== undefined ? comment.predicted_category_id : 0;
                        const categoryName = getCategoryName(categoryId);
                        const confidence = comment.predicted_confidence !== undefined ? Math.round(comment.predicted_confidence * 100) : 50;
                        
                        const categoryColors = {
                          0: 'success',
                          1: 'danger',
                          2: 'warning',
                          3: 'info',
                          4: 'secondary'
                        };
                        const categoryColor = categoryColors[categoryId] || 'success';
                        
                        return (
                          <div key={index} className={`card comment-card mb-3 ${harmful ? 'border-danger' : 'border-success'}`}>
                            <div className="card-body">
                              <div className="row">
                                <div className="col-md-1">
                                  <div className="comment-avatar">
                                    <FaCircle className="fa-2x text-muted" />
                                  </div>
                                </div>
                                <div className="col-md-11">
                                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                                      <h6 className="mb-1">
                                        @{comment.author || 'Unknown'}
                                        <span className={`badge bg-${categoryColor} ms-2`}>
                                          {categoryName}
                                        </span>
                                        <span className={`badge bg-${harmful ? 'danger' : 'success'} ms-1`}>
                                          {harmful ? 'Zararlı' : 'Güvenli'}
                                </span>
                                      </h6>
                                      <p className="mb-2 comment-text">{comment.text || 'Yorum metni bulunamadı'}</p>
                                      <div className="mb-2">
                                        <small className="text-muted">
                                          <i className="fas fa-brain me-1"></i>AI Tahmin: {categoryName} ({confidence}%)
                                        </small>
                                      </div>
                                      <small className="text-muted">
                                        <FaCircle className="me-1" />
                                        {comment.platform || 'Unknown'}
                                        {comment.timestamp && (
                                          <>
                                            <FaCircle className="ms-2 me-1" />
                                            {comment.timestamp}
                                          </>
                                        )}
                                        {comment.likes && (
                                          <>
                                            <FaCircle className="ms-2 me-1" />
                                            {comment.likes}
                                          </>
                                        )}
                                      </small>
                                    </div>
                                    <div className="comment-actions">
                                      <button 
                                        className="btn btn-sm btn-outline-primary"
                                        onClick={() => copyComment(comment.text || '')}
                                      >
                                        <FaCopy />
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              )}
                </div>

            {/* Tüm Kullanıcılar */}
            <div className="card mt-4">
              <div className="card-header">
                <h5 className="mb-0">
                  <FaUsers className="me-2" />
                  Tüm Kullanıcılar
                </h5>
              </div>
              <div className="card-body">
                {Object.entries(analysis.user_analyses || {}).map(([userId, user]) => (
                  <div key={userId} className="card user-card mb-3">
                    <div className="card-body">
                      <div className="row align-items-center">
                        <div className="col-md-3">
                          <h6 className="mb-1">@{userId}</h6>
                          <span className={`risk-badge risk-${user.risk_category}`}>
                            {getRiskText(user.risk_category)}
                          </span>
                        </div>
                        <div className="col-md-2">
                          <small className="text-muted">Toplam Yorum</small>
                          <div className="fw-bold">{user.total_comments}</div>
                        </div>
                        <div className="col-md-2">
                          <small className="text-muted">Zararlı Yorum</small>
                          <div className="fw-bold text-danger">{user.harmful_comments}</div>
                        </div>
                        <div className="col-md-2">
                          <small className="text-muted">Zararlı Oranı</small>
                          <div className="fw-bold">{(user.harmful_ratio * 100).toFixed(1)}%</div>
                        </div>
                        <div className="col-md-3">
                          <button 
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => showUserDetails(userId, user)}
                          >
                            <FaEye className="me-1" />
                            Detaylar
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {showUserModal && selectedUser && (
        <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }} onClick={closeUserModal}>
          <div className="modal-dialog modal-lg modal-dialog-centered" onClick={(e) => e.stopPropagation()}>
            <div className="modal-content" style={{ borderRadius: '15px', overflow: 'hidden' }}>
              <div className="modal-header" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none' }}>
                <h5 className="modal-title">
                  <FaUser className="me-2" />
                  @{selectedUser.userId} - Detaylı Analiz
                </h5>
                <button type="button" className="btn-close btn-close-white" onClick={closeUserModal}></button>
              </div>
              <div className="modal-body p-4">
                {/* Özet Bilgiler */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <div className="d-flex align-items-center mb-3">
                      <div className="p-3 rounded-circle me-3" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                        <FaComments className="text-white" style={{ fontSize: '1.5rem' }} />
                      </div>
                        <div>
                        <small className="text-muted d-block">Toplam Yorum</small>
                        <h4 className="mb-0">{selectedUser.total_comments}</h4>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="d-flex align-items-center mb-3">
                      <div className="p-3 rounded-circle me-3" style={{ background: '#e74c3c' }}>
                        <FaExclamationTriangle className="text-white" style={{ fontSize: '1.5rem' }} />
                      </div>
                        <div>
                        <small className="text-muted d-block">Zararlı Yorum</small>
                        <h4 className="mb-0 text-danger">{selectedUser.harmful_comments}</h4>
                      </div>
                    </div>
                  </div>
                </div>

                {/* İstatistikler */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <div className="p-3 rounded" style={{ backgroundColor: '#f8f9fa' }}>
                      <small className="text-muted d-block mb-2">Zararlı Oranı</small>
                      <div className="d-flex align-items-center">
                        <h3 className="mb-0 me-3">{(selectedUser.harmful_ratio * 100).toFixed(1)}%</h3>
                        <div className="progress flex-grow-1" style={{ height: '10px' }}>
                          <div 
                            className="progress-bar bg-danger" 
                            style={{ width: `${(selectedUser.harmful_ratio * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="p-3 rounded" style={{ backgroundColor: '#f8f9fa' }}>
                      <small className="text-muted d-block mb-2">Risk Kategorisi</small>
                      <span className={`risk-badge risk-${selectedUser.risk_category}`}>
                        {getRiskText(selectedUser.risk_category)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Öneriler */}
                {selectedUser.recommendations && selectedUser.recommendations.length > 0 && (
                  <div className="mb-4">
                    <h6 className="mb-3">
                      <i className="fas fa-lightbulb me-2 text-warning"></i>
                      Öneriler
                    </h6>
                    <div className="recommendations-list">
                      {selectedUser.recommendations.map((rec, index) => (
                        <div key={index} className="recommendation-item mb-2">
                          <i className="fas fa-check-circle me-2 text-success"></i>
                          {rec}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analiz Zamanı */}
                <div className="border-top pt-3">
                  <small className="text-muted">
                    <i className="fas fa-clock me-2"></i>
                    Analiz Zamanı: {new Date(selectedUser.analysis_timestamp).toLocaleString('tr-TR')}
                  </small>
                </div>
              </div>
              <div className="modal-footer" style={{ border: 'none', backgroundColor: '#f8f9fa' }}>
                <button type="button" className="btn btn-secondary" onClick={closeUserModal}>
                  Kapat
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
