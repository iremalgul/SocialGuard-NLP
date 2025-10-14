// MANUEL YORUM ANALİZİ - Tek yorum kategori tahmini
import React, { useState } from 'react';
import { FaBrain, FaCommentDots, FaChartPie, FaSearch, FaList, FaUpload, FaCircle } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const ManualAnalysisPage = () => {
  const { api } = useAuth();
  const [comment, setComment] = useState('');
  const [batchComments, setBatchComments] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [datasetResult, setDatasetResult] = useState(null);

  // Kategori isimlerini Türkçe olarak döndür
  const getCategoryNameTurkish = (categoryId) => {
    const categoryNames = {
      0: 'Zararsız / Nötr',
      1: 'Doğrudan Hakaret / Küfür',
      2: 'Cinsiyetçi / Cinsel İmada',
      3: 'Alaycılık / Mikroagresyon',
      4: 'Görünüm Temelli Eleştiri'
    };
    return categoryNames[categoryId] || 'Bilinmeyen Kategori';
  };

  const checkApiStatus = React.useCallback(async () => {
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

  const predictCategory = async () => {
    if (!comment.trim()) {
      alert('Lütfen bir yorum girin!');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await api.post('/api/predict', {
        comment: comment
      });

      setResult(response.data);
    } catch (error) {
      alert('Hata: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const batchPredict = async () => {
    const comments = batchComments.split('\n').filter(c => c.trim());
    
    if (comments.length === 0) {
      alert('Lütfen en az bir yorum girin!');
      return;
    }

    setLoading(true);
    setBatchResults(null);

    try {
      const response = await api.post('/api/batch-predict', comments);
      setBatchResults(response.data.results);
    } catch (error) {
      alert('Hata: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setDatasetResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/upload-dataset', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setDatasetResult(response.data);
      
      // Başarı mesajı
      const toast = document.createElement('div');
      toast.className = 'position-fixed top-0 end-0 m-3 alert alert-success';
      toast.style.zIndex = '9999';
      toast.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        Veri seti başarıyla işlendi! ${response.data.total_rows} yorum AI ile analiz edildi.
      `;
      document.body.appendChild(toast);
      
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 4000);
      
    } catch (error) {
      alert('Dosya yükleme hatası: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadDataset = () => {
    if (!datasetResult || !datasetResult.download_url) return;
    
    const downloadUrl = `${API_BASE.replace('/api', '')}${datasetResult.download_url}`;
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="gradient-bg">
      {/* API Status */}
      <div className="api-status">
        <span className={`badge ${apiStatus === 'connected' ? 'bg-success' : 'bg-danger'}`}>
          <FaCircle className="me-1" />
          {apiStatus === 'connected' ? 'API Bağlı' : 'API Bağlantısı Yok'}
        </span>
      </div>

      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            {/* Ana Başlık */}
            <div className="text-center mb-5">
              <h1 className="text-white mb-3">
                <FaBrain className="me-2" />
                Yorum Kategorisi Tahmin Sistemi
              </h1>
              <p className="text-white-50 fs-5">AI ile Gelişmiş Metin Analizi</p>
              <small className="text-white-50">Powered by Google Gemini 2.0 Flash</small>
            </div>

            {/* Ana Kart */}
            <div className="card">
              <div className="card-body p-4">
                {/* Tahmin Bölümü */}
                <div className="mb-5">
                  <h3 className="mb-4">
                    <FaCommentDots className="text-primary me-2" />
                    Yorum Analizi
                  </h3>
                  <div className="mb-3">
                    <label htmlFor="commentInput" className="form-label fw-bold">Yorumunuzu Girin:</label>
                    <textarea 
                      className="form-control" 
                      id="commentInput" 
                      rows="4" 
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Analiz edilecek yorumu buraya yazın..."
                    />
                  </div>
                  <button 
                    className="btn btn-primary btn-lg" 
                    onClick={predictCategory}
                    disabled={loading}
                  >
                    <FaSearch className="me-2" />
                    Kategori Tahmin Et
                  </button>
                </div>

                {/* Loading */}
                {loading && (
                  <div className="text-center py-4">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Yükleniyor...</span>
                    </div>
                    <p className="mt-2 text-muted">Yorum analiz ediliyor...</p>
                  </div>
                )}

                {/* Sonuç Kartı */}
                {result && (
                  <div className="mb-5">
                    <h4 className="mb-3">
                      <FaChartPie className="text-success me-2" />
                      Tahmin Sonucu
                    </h4>
                    <div className="alert alert-info">
                      <strong>Orijinal Yorum:</strong>
                      <p className="mb-0 mt-2">{result.comment}</p>
                    </div>
                    <div className="text-center">
                      <span className={`category-badge category-${result.prediction_id}`}>
                        {result.prediction_id}
                      </span>
                      <h5 className="mt-3 mb-2">{getCategoryNameTurkish(result.prediction_id)}</h5>
                      <div className="mt-3">
                        <small className="text-muted">Güven Skoru:</small>
                        <div className="progress mt-1" style={{ height: '8px' }}>
                          <div 
                            className="progress-bar" 
                            role="progressbar" 
                            style={{ width: `${Math.round((result.confidence || 0.5) * 100)}%` }}
                          />
                        </div>
                        <small className="text-muted">{Math.round((result.confidence || 0.5) * 100)}%</small>
                      </div>
                    </div>
                  </div>
                )}

                <hr className="my-5" />

                {/* Toplu Tahmin */}
                <div className="mb-4">
                  <h3 className="mb-4">
                    <FaList className="text-info me-2" />
                    Toplu Tahmin
                  </h3>
                  <div className="mb-3">
                    <label htmlFor="batchInput" className="form-label">Birden Fazla Yorum (Her satıra bir yorum):</label>
                    <textarea 
                      className="form-control" 
                      id="batchInput" 
                      rows="3" 
                      value={batchComments}
                      onChange={(e) => setBatchComments(e.target.value)}
                      placeholder="Yorum 1&#10;Yorum 2&#10;Yorum 3"
                    />
                  </div>
                  <button 
                    className="btn btn-info" 
                    onClick={batchPredict}
                    disabled={loading}
                  >
                    <FaList className="me-2" />
                    Toplu Tahmin Et
                  </button>
                </div>

                {/* Toplu Sonuçlar */}
                {batchResults && (
                  <div className="mb-4">
                    <h5 className="mb-3">Toplu Tahmin Sonuçları</h5>
                    <div>
                      {batchResults.map((result, index) => (
                        <div key={index} className="card mb-2">
                          <div className="card-body p-3">
                            <div className="d-flex justify-content-between align-items-start">
                              <div className="flex-grow-1">
                                <p className="mb-2"><strong>Yorum {index + 1}:</strong> {result.comment}</p>
                                <span className={`category-badge category-${result.prediction_id}`}>
                                  {result.prediction_id}
                                </span>
                                <span className="ms-2">{getCategoryNameTurkish(result.prediction_id)}</span>
                              </div>
                              <small className="text-muted">
                                {Math.round((result.confidence || 0.5) * 100)}%
                              </small>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <hr className="my-5" />

                {/* Veri Seti Yükleme */}
                <div className="mb-4">
                  <h3 className="mb-4">
                    <FaUpload className="text-warning me-2" />
                    Veri Seti Yükle ve AI ile Analiz Et
                  </h3>
                  <div className="alert alert-info mb-3">
                    <strong>Beklenen CSV Formatı:</strong> comment, username, platform
                    <br />
                    <small>AI her yorum için otomatik olarak kategori (0-4) hesaplayacak ve JSON olarak indirebilirsiniz.</small>
                  </div>
                  <div className="upload-area" onClick={() => document.getElementById('fileInput').click()}>
                    <FaUpload className="fa-3x text-muted mb-3" />
                    <h5>CSV Dosyasını Sürükleyin veya Tıklayın</h5>
                    <p className="text-muted">Format: comment, username, platform</p>
                    <input 
                      type="file" 
                      id="fileInput" 
                      accept=".csv" 
                      style={{ display: 'none' }}
                      onChange={handleFileUpload}
                    />
                  </div>
                </div>

                {/* Dataset Sonuçları */}
                {datasetResult && (
                  <div className="mb-4">
                    <div className="card">
                      <div className="card-header bg-success text-white">
                        <h5 className="mb-0">
                          <i className="fas fa-check-circle me-2"></i>
                          İşlem Başarılı - {datasetResult.total_rows} Yorum Analiz Edildi
                        </h5>
                      </div>
                      <div className="card-body">
                        <div className="mb-3">
                          <button 
                            className="btn btn-primary btn-lg"
                            onClick={handleDownloadDataset}
                          >
                            <i className="fas fa-download me-2"></i>
                            JSON Dosyasını İndir ({datasetResult.output_file})
                          </button>
                        </div>

                        <h6 className="mb-3">
                          <i className="fas fa-table me-2"></i>
                          İlk 5 Satır Önizleme:
                        </h6>
                        <div className="table-responsive">
                          <table className="table table-bordered table-hover">
                            <thead className="table-light">
                              <tr>
                                <th style={{ width: '40%' }}>Yorum</th>
                                <th style={{ width: '10%' }}>Kategori</th>
                                <th style={{ width: '25%' }}>Kategori Adı</th>
                                <th style={{ width: '15%' }}>Kullanıcı</th>
                                <th style={{ width: '10%' }}>Platform</th>
                              </tr>
                            </thead>
                            <tbody>
                              {datasetResult.sample_data.map((row, index) => (
                                <tr key={index}>
                                  <td>{row.comment}</td>
                                  <td>
                                    <span className={`category-badge category-${row.label}`}>
                                      {row.label}
                                    </span>
                                  </td>
                                  <td>
                                    <strong>{getCategoryNameTurkish(row.label)}</strong>
                                  </td>
                                  <td>@{row.username}</td>
                                  <td>
                                    <span className={`badge bg-${row.platform === 'youtube' ? 'danger' : row.platform === 'instagram' ? 'warning' : 'info'}`}>
                                      {row.platform}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Kategori Açıklamaları */}
                <div className="mt-5">
                  <h4 className="mb-4">
                    <FaList className="text-warning me-2" />
                    Kategori Açıklamaları
                  </h4>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <div className="d-flex align-items-center">
                        <span className="category-badge category-0 me-3">0</span>
                        <div>
                          <strong>Zararsız / Nötr</strong>
                          <br /><small className="text-muted">No Harassment / Neutral</small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6 mb-3">
                      <div className="d-flex align-items-center">
                        <span className="category-badge category-1 me-3">1</span>
                        <div>
                          <strong>Doğrudan Hakaret / Küfür</strong>
                          <br /><small className="text-muted">Direct Insult / Profanity</small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6 mb-3">
                      <div className="d-flex align-items-center">
                        <span className="category-badge category-2 me-3">2</span>
                        <div>
                          <strong>Cinsiyetçi / Cinsel İmada</strong>
                          <br /><small className="text-muted">Sexist / Sexual Implication</small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6 mb-3">
                      <div className="d-flex align-items-center">
                        <span className="category-badge category-3 me-3">3</span>
                        <div>
                          <strong>Alaycılık / Mikroagresyon</strong>
                          <br /><small className="text-muted">Sarcasm / Microaggression</small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6 mb-3">
                      <div className="d-flex align-items-center">
                        <span className="category-badge category-4 me-3">4</span>
                        <div>
                          <strong>Görünüm Temelli Eleştiri</strong>
                          <br /><small className="text-muted">Appearance-based Criticism</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManualAnalysisPage;

