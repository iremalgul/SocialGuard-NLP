import React, { useState, useEffect } from 'react';
import { 
  FaUser, FaEnvelope, FaCalendarAlt, FaClock, FaChartLine, 
  FaComments, FaUsers, FaExclamationTriangle, FaEye, FaTrash,
  FaInstagram, FaTwitter, FaFacebook, FaLink, FaFilter, FaBrain
} from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const ProfilePage = () => {
  const { user, api } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [commentFilter, setCommentFilter] = useState('all'); // all, harmful, safe
  
  // Manuel tahminler
  const [activeTab, setActiveTab] = useState('social'); // social, manual
  const [manualPredictions, setManualPredictions] = useState([]);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [showPredictionModal, setShowPredictionModal] = useState(false);
  
  // Silme onay modal'ları
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null); // { type: 'analysis' | 'prediction', id: string }

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      // İstatistikleri çek
      const statsResponse = await api.get('/api/analyses/stats/summary');
      setStats(statsResponse.data);
      
      // Analiz geçmişini çek
      const historyResponse = await api.get('/api/analyses/history?limit=10');
      setAnalyses(historyResponse.data.analyses);
      
      // Manuel tahminleri çek
      const manualResponse = await api.get('/api/manual-predictions/history?limit=20');
      setManualPredictions(manualResponse.data.predictions);
      
    } catch (error) {
      console.error('Profil verisi yükleme hatası:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewAnalysisDetail = async (analysisId) => {
    try {
      const response = await api.get(`/api/analyses/${analysisId}`);
      setSelectedAnalysis(response.data);
      setShowModal(true);
    } catch (error) {
      console.error('Analiz detayı yükleme hatası:', error);
      alert('Analiz detayları yüklenirken hata oluştu');
    }
  };

  const confirmDelete = (type, id) => {
    setDeleteTarget({ type, id });
    setShowDeleteModal(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    
    try {
      if (deleteTarget.type === 'analysis') {
        await api.delete(`/api/analyses/${deleteTarget.id}`);
      } else if (deleteTarget.type === 'prediction') {
        await api.delete(`/api/manual-predictions/${deleteTarget.id}`);
      }
      
      setShowDeleteModal(false);
      setDeleteTarget(null);
      fetchProfileData();
      
      // Başarı toast'ı
      const toast = document.createElement('div');
      toast.className = 'position-fixed top-0 end-0 m-3 alert alert-success alert-dismissible fade show';
      toast.style.zIndex = '9999';
      toast.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${deleteTarget.type === 'analysis' ? 'Analiz' : 'Tahmin'} başarıyla silindi!
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `;
      document.body.appendChild(toast);
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast);
        }
      }, 3000);
      
    } catch (error) {
      console.error('Silme hatası:', error);
      alert('Silinirken hata oluştu');
    }
  };

  const viewPredictionDetail = async (predictionId) => {
    try {
      const response = await api.get(`/api/manual-predictions/${predictionId}`);
      setSelectedPrediction(response.data);
      setShowPredictionModal(true);
    } catch (error) {
      console.error('Tahmin detayı yükleme hatası:', error);
      alert('Tahmin detayları yüklenirken hata oluştu');
    }
  };

  const getPredictionTypeLabel = (type) => {
    const labels = {
      'single': 'Tekli Yorum',
      'batch': 'Toplu Yorum',
      'dataset': 'Veri Seti'
    };
    return labels[type] || type;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPlatformIcon = (platform) => {
    switch (platform?.toLowerCase()) {
      case 'instagram': return <FaInstagram className="text-danger" />;
      case 'twitter': return <FaTwitter className="text-info" />;
      case 'facebook': return <FaFacebook className="text-primary" />;
      default: return <FaLink />;
    }
  };

  const getCategoryBadge = (categoryId, categoryName) => {
    const colors = {
      0: 'success',
      1: 'warning',
      2: 'danger',
      3: 'danger',
      4: 'dark'
    };
    return (
      <span className={`badge bg-${colors[categoryId] || 'secondary'}`}>
        {categoryName || 'Bilinmeyen'}
      </span>
    );
  };

  const getFilteredComments = () => {
    if (!selectedAnalysis?.comments) return [];
    
    switch (commentFilter) {
      case 'harmful':
        return selectedAnalysis.comments.filter(c => c.predicted_category_id > 0);
      case 'safe':
        return selectedAnalysis.comments.filter(c => c.predicted_category_id === 0);
      default:
        return selectedAnalysis.comments;
    }
  };

  if (loading) {
    return (
      <div className="container mt-5 pt-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Yükleniyor...</span>
        </div>
        <p className="mt-3">Profil bilgileri yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className="container mt-4 mb-5">
      {/* Profil Header */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body p-4">
              <div className="row align-items-center">
                <div className="col-auto">
                  <div 
                    className="d-flex align-items-center justify-content-center rounded-circle bg-primary text-white"
                    style={{ width: '80px', height: '80px', fontSize: '2rem', fontWeight: 'bold' }}
                  >
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                </div>
                <div className="col">
                  <h2 className="mb-2">{user?.name}</h2>
                  <div className="text-muted mb-2">
                    <FaEnvelope className="me-2" />
                    {user?.email}
                  </div>
                  <div className="d-flex gap-3 text-muted small">
                    <span>
                      <FaCalendarAlt className="me-1" />
                      Üyelik: {formatDate(user?.created_at)}
                    </span>
                    {user?.last_login && (
                      <span>
                        <FaClock className="me-1" />
                        Son Giriş: {formatDate(user?.last_login)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* İstatistikler */}
      {stats && (
        <div className="row g-3 mb-4">
          <div className="col-md-3 col-sm-6">
            <div className="card shadow-sm h-100">
              <div className="card-body text-center">
                <div className="display-6 text-primary mb-2">
                  <FaChartLine />
                </div>
                <h3 className="mb-1">{stats.total_analyses}</h3>
                <p className="text-muted mb-0">Toplam Analiz</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-sm-6">
            <div className="card shadow-sm h-100">
              <div className="card-body text-center">
                <div className="display-6 text-info mb-2">
                  <FaComments />
                </div>
                <h3 className="mb-1">{stats.total_comments_analyzed}</h3>
                <p className="text-muted mb-0">İncelenen Yorum</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-sm-6">
            <div className="card shadow-sm h-100">
              <div className="card-body text-center">
                <div className="display-6 text-success mb-2">
                  <FaUsers />
                </div>
                <h3 className="mb-1">{stats.total_users_analyzed}</h3>
                <p className="text-muted mb-0">Analiz Edilen Kullanıcı</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-sm-6">
            <div className="card shadow-sm h-100">
              <div className="card-body text-center">
                <div className="display-6 text-danger mb-2">
                  <FaExclamationTriangle />
                </div>
                <h3 className="mb-1">{stats.total_flagged_users}</h3>
                <p className="text-muted mb-0">İşaretlenen Kullanıcı</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sekmeler */}
      <div className="row mb-3">
        <div className="col-12">
          <ul className="nav nav-tabs">
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'social' ? 'active' : ''}`}
                onClick={() => setActiveTab('social')}
              >
                <FaChartLine className="me-2" />
                Sosyal Medya Analizleri ({analyses.length})
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'manual' ? 'active' : ''}`}
                onClick={() => setActiveTab('manual')}
              >
                <FaBrain className="me-2" />
                Manuel Tahminler ({manualPredictions.length})
              </button>
            </li>
          </ul>
        </div>
      </div>

      {/* Sosyal Medya Analizleri Sekmesi */}
      {activeTab === 'social' && (
      <div className="row">
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-header bg-white py-3">
              <h4 className="mb-0">
                <FaChartLine className="me-2" />
                Son Analizler
              </h4>
            </div>
            <div className="card-body p-0">
              {analyses.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <FaChartLine className="display-4 mb-3 opacity-25" />
                  <p>Henüz analiz yapmadınız.</p>
                  <button 
                    className="btn btn-primary mt-2"
                    onClick={() => navigate('/')}
                  >
                    İlk Analizinizi Yapın
                  </button>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Platform</th>
                        <th>Gönderi Sahibi</th>
                        <th className="text-center">Yorumlar</th>
                        <th className="text-center">Kullanıcılar</th>
                        <th className="text-center">İşaretlenenler</th>
                        <th>Tarih</th>
                        <th className="text-end">İşlemler</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyses.map((analysis) => (
                        <tr key={analysis.id}>
                          <td>
                            <span className="d-flex align-items-center gap-2">
                              {getPlatformIcon(analysis.platform)}
                              <span className="text-capitalize">{analysis.platform}</span>
                            </span>
                          </td>
                          <td>
                            <strong>@{analysis.post_owner || 'unknown'}</strong>
                          </td>
                          <td className="text-center">
                            <span className="badge bg-info">{analysis.total_comments}</span>
                          </td>
                          <td className="text-center">
                            <span className="badge bg-primary">{analysis.analyzed_users}</span>
                          </td>
                          <td className="text-center">
                            <span className={`badge ${analysis.flagged_users > 0 ? 'bg-danger' : 'bg-success'}`}>
                              {analysis.flagged_users}
                            </span>
                          </td>
                          <td>
                            <small className="text-muted">
                              {formatDate(analysis.created_at)}
                            </small>
                          </td>
                          <td className="text-end">
                            <button
                              className="btn btn-sm btn-outline-primary me-2"
                              onClick={() => viewAnalysisDetail(analysis.id)}
                              title="Detayları Görüntüle"
                            >
                              <FaEye />
                            </button>
                            <button
                              className="btn btn-sm btn-outline-danger"
                              onClick={() => confirmDelete('analysis', analysis.id)}
                              title="Sil"
                            >
                              <FaTrash />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      )}

      {/* Manuel Tahminler Sekmesi */}
      {activeTab === 'manual' && (
      <div className="row">
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-header bg-white py-3">
              <h4 className="mb-0">
                <FaBrain className="me-2" />
                Manuel Tahminler
              </h4>
            </div>
            <div className="card-body p-0">
              {manualPredictions.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <FaBrain className="display-4 mb-3 opacity-25" />
                  <p>Henüz manuel tahmin yapmadınız.</p>
                  <button 
                    className="btn btn-primary mt-2"
                    onClick={() => navigate('/manual-analysis')}
                  >
                    Manuel Analiz Sayfasına Git
                  </button>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Tür</th>
                        <th>Dosya/Bilgi</th>
                        <th className="text-center">Toplam Yorum</th>
                        <th className="text-center">Zararsız</th>
                        <th className="text-center">Zararlı</th>
                        <th>Tarih</th>
                        <th className="text-end">İşlemler</th>
                      </tr>
                    </thead>
                    <tbody>
                      {manualPredictions.map((prediction) => {
                        const harmfulCount = prediction.category_1_count + 
                                            prediction.category_2_count + 
                                            prediction.category_3_count + 
                                            prediction.category_4_count;
                        
                        return (
                          <tr key={prediction.id}>
                            <td>
                              <span className="badge bg-secondary">
                                {getPredictionTypeLabel(prediction.prediction_type)}
                              </span>
                            </td>
                            <td>
                              {prediction.filename || '-'}
                            </td>
                            <td className="text-center">
                              <span className="badge bg-info">{prediction.total_comments}</span>
                            </td>
                            <td className="text-center">
                              <span className="badge bg-success">{prediction.category_0_count}</span>
                            </td>
                            <td className="text-center">
                              <span className="badge bg-danger">{harmfulCount}</span>
                            </td>
                            <td>
                              <small className="text-muted">
                                {formatDate(prediction.created_at)}
                              </small>
                            </td>
                            <td className="text-end">
                              <button
                                className="btn btn-sm btn-outline-primary me-2"
                                onClick={() => viewPredictionDetail(prediction.id)}
                                title="Detayları Görüntüle"
                              >
                                <FaEye />
                              </button>
                              <button
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => confirmDelete('prediction', prediction.id)}
                                title="Sil"
                              >
                                <FaTrash />
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      )}

      {/* Analiz Detay Modal */}
      {showModal && selectedAnalysis && (
        <div 
          className="modal fade show d-block" 
          tabIndex="-1" 
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setShowModal(false)}
        >
          <div 
            className="modal-dialog modal-xl modal-dialog-scrollable"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Analiz Detayları</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                {/* Genel Bilgiler */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <strong>Platform:</strong> 
                      <span className="ms-2">
                        {getPlatformIcon(selectedAnalysis.platform)}
                        <span className="ms-1 text-capitalize">{selectedAnalysis.platform}</span>
                      </span>
                    </div>
                    <div className="mb-3">
                      <strong>Gönderi Sahibi:</strong> 
                      <span className="ms-2">@{selectedAnalysis.post_owner}</span>
                    </div>
                    <div className="mb-3">
                      <strong>URL:</strong> 
                      <div className="mt-1">
                        <a href={selectedAnalysis.url} target="_blank" rel="noopener noreferrer" className="text-break">
                          {selectedAnalysis.url}
                        </a>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <strong>Toplam Yorum:</strong> 
                      <span className="badge bg-info ms-2">{selectedAnalysis.total_comments}</span>
                    </div>
                    <div className="mb-3">
                      <strong>Analiz Edilen Kullanıcı:</strong> 
                      <span className="badge bg-primary ms-2">{selectedAnalysis.analyzed_users}</span>
                    </div>
                    <div className="mb-3">
                      <strong>İşaretlenen Kullanıcılar:</strong> 
                      <span className={`badge ${selectedAnalysis.flagged_users > 0 ? 'bg-danger' : 'bg-success'} ms-2`}>
                        {selectedAnalysis.flagged_users}
                      </span>
                    </div>
                    <div className="mb-3">
                      <strong>Analiz Süresi:</strong> 
                      <span className="ms-2">{selectedAnalysis.analysis_duration?.toFixed(2)} saniye</span>
                    </div>
                    <div className="mb-3">
                      <strong>Tarih:</strong> 
                      <span className="ms-2">{formatDate(selectedAnalysis.created_at)}</span>
                    </div>
                  </div>
                </div>

                <hr />

                {/* Yorumlar Bölümü */}
                <div className="mt-4">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h6 className="mb-0">
                      <FaComments className="me-2" />
                      Yorumlar ({getFilteredComments().length})
                    </h6>
                    <div className="btn-group btn-group-sm" role="group">
                      <button
                        type="button"
                        className={`btn ${commentFilter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setCommentFilter('all')}
                      >
                        Tümü ({selectedAnalysis.comments?.length || 0})
                      </button>
                      <button
                        type="button"
                        className={`btn ${commentFilter === 'harmful' ? 'btn-danger' : 'btn-outline-danger'}`}
                        onClick={() => setCommentFilter('harmful')}
                      >
                        Zararlı ({selectedAnalysis.comments?.filter(c => c.predicted_category_id > 0).length || 0})
                      </button>
                      <button
                        type="button"
                        className={`btn ${commentFilter === 'safe' ? 'btn-success' : 'btn-outline-success'}`}
                        onClick={() => setCommentFilter('safe')}
                      >
                        Güvenli ({selectedAnalysis.comments?.filter(c => c.predicted_category_id === 0).length || 0})
                      </button>
                    </div>
                  </div>

                  <div className="list-group" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {getFilteredComments().length === 0 ? (
                      <div className="text-center py-4 text-muted">
                        <FaComments className="display-4 mb-3 opacity-25" />
                        <p>Bu filtre için yorum bulunamadı.</p>
                      </div>
                    ) : (
                      getFilteredComments().map((comment, index) => (
                        <div key={index} className="list-group-item">
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <div className="d-flex align-items-center gap-2">
                              <div 
                                className="d-flex align-items-center justify-content-center rounded-circle bg-primary text-white"
                                style={{ width: '30px', height: '30px', fontSize: '0.75rem', fontWeight: 'bold' }}
                              >
                                {comment.author?.charAt(0).toUpperCase() || 'U'}
                              </div>
                              <strong>@{comment.author}</strong>
                            </div>
                            <div className="d-flex gap-2 align-items-center">
                              {getCategoryBadge(comment.predicted_category_id, comment.predicted_category_name)}
                              {comment.predicted_confidence && (
                                <small className="text-muted">
                                  {(comment.predicted_confidence * 100).toFixed(0)}%
                                </small>
                              )}
                            </div>
                          </div>
                          <p className="mb-0 text-break">{comment.text}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => {
                    setShowModal(false);
                    setCommentFilter('all'); // Reset filter
                  }}
                >
                  Kapat
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manuel Tahmin Detay Modal */}
      {showPredictionModal && selectedPrediction && (
        <div 
          className="modal fade show d-block" 
          tabIndex="-1" 
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setShowPredictionModal(false)}
        >
          <div 
            className="modal-dialog modal-xl modal-dialog-scrollable"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {getPredictionTypeLabel(selectedPrediction.prediction_type)} - Detaylar
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowPredictionModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                {/* Genel Bilgiler */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <strong>Tür:</strong> 
                      <span className="badge bg-secondary ms-2">
                        {getPredictionTypeLabel(selectedPrediction.prediction_type)}
                      </span>
                    </div>
                    {selectedPrediction.filename && (
                      <div className="mb-3">
                        <strong>Dosya:</strong> 
                        <span className="ms-2">{selectedPrediction.filename}</span>
                      </div>
                    )}
                    <div className="mb-3">
                      <strong>Toplam Yorum:</strong> 
                      <span className="badge bg-info ms-2">{selectedPrediction.total_comments}</span>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <strong>Kategori Dağılımı:</strong>
                      <div className="mt-2">
                        <div className="d-flex justify-content-between mb-1">
                          <span>Zararsız / Nötr:</span>
                          <span className="badge bg-success">{selectedPrediction.category_0_count}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-1">
                          <span>Hakaret / Küfür:</span>
                          <span className="badge bg-warning">{selectedPrediction.category_1_count}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-1">
                          <span>Cinsel İma:</span>
                          <span className="badge bg-danger">{selectedPrediction.category_2_count}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-1">
                          <span>Alaycılık:</span>
                          <span className="badge bg-danger">{selectedPrediction.category_3_count}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-1">
                          <span>Görünüm Eleştiri:</span>
                          <span className="badge bg-dark">{selectedPrediction.category_4_count}</span>
                        </div>
                      </div>
                    </div>
                    <div className="mb-3">
                      <strong>İşlem Süresi:</strong> 
                      <span className="ms-2">{selectedPrediction.processing_time?.toFixed(2)} saniye</span>
                    </div>
                    <div className="mb-3">
                      <strong>Tarih:</strong> 
                      <span className="ms-2">{formatDate(selectedPrediction.created_at)}</span>
                    </div>
                  </div>
                </div>

                <hr />

                {/* Tahminler Listesi */}
                <div className="mt-4">
                  <h6 className="mb-3">
                    <FaComments className="me-2" />
                    Tahmin Sonuçları ({selectedPrediction.predictions?.length || 0})
                  </h6>
                  <div className="list-group" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {selectedPrediction.predictions?.map((pred, index) => (
                      <div key={index} className="list-group-item">
                        <div className="d-flex justify-content-between align-items-start mb-2">
                          <div>
                            {pred.username && (
                              <small className="text-muted">@{pred.username}</small>
                            )}
                          </div>
                          <div className="d-flex gap-2 align-items-center">
                            {getCategoryBadge(pred.category_id, pred.category_name)}
                            {pred.confidence && (
                              <small className="text-muted">
                                {(pred.confidence * 100).toFixed(0)}%
                              </small>
                            )}
                          </div>
                        </div>
                        <p className="mb-0 text-break">{pred.comment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowPredictionModal(false)}
                >
                  Kapat
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Silme Onay Modal */}
      {showDeleteModal && deleteTarget && (
        <div 
          className="modal fade show d-block" 
          tabIndex="-1" 
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setShowDeleteModal(false)}
        >
          <div 
            className="modal-dialog modal-dialog-centered"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content">
              <div className="modal-header bg-danger text-white">
                <h5 className="modal-title">
                  <FaExclamationTriangle className="me-2" />
                  Silme Onayı
                </h5>
                <button 
                  type="button" 
                  className="btn-close btn-close-white" 
                  onClick={() => setShowDeleteModal(false)}
                ></button>
              </div>
              <div className="modal-body text-center py-4">
                <div className="mb-3">
                  <FaTrash className="display-1 text-danger" />
                </div>
                <h5 className="mb-3">
                  {deleteTarget.type === 'analysis' 
                    ? 'Bu analizi silmek istediğinizden emin misiniz?' 
                    : 'Bu tahmini silmek istediğinizden emin misiniz?'}
                </h5>
                <p className="text-muted">
                  Bu işlem geri alınamaz. Tüm veriler kalıcı olarak silinecektir.
                </p>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setShowDeleteModal(false)}
                >
                  <i className="fas fa-times me-2"></i>
                  İptal
                </button>
                <button 
                  type="button" 
                  className="btn btn-danger"
                  onClick={handleDelete}
                >
                  <FaTrash className="me-2" />
                  Evet, Sil
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;

