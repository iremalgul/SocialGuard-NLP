import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaEnvelope, FaLock, FaSignInAlt, FaShieldAlt, FaEye, FaEyeSlash } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Lütfen tüm alanları doldurun!');
      return;
    }

    setLoading(true);

    const result = await login(email, password);
    
    setLoading(false);

    if (result.success) {
      // Başarı mesajı göster
      const toast = document.createElement('div');
      toast.className = 'custom-toast success';
      toast.innerHTML = `
        <div class="toast-content">
          <i class="fas fa-check-circle"></i>
          <span>Giriş başarılı! Yönlendiriliyorsunuz...</span>
        </div>
      `;
      document.body.appendChild(toast);
      
      setTimeout(() => {
        document.body.removeChild(toast);
        navigate('/');
      }, 1500);
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="auth-shape shape-1"></div>
        <div className="auth-shape shape-2"></div>
        <div className="auth-shape shape-3"></div>
      </div>

      <div className="container">
        <div className="row justify-content-center align-items-center min-vh-100">
          <div className="col-lg-5 col-md-7">
            <div className="auth-card">
              <div className="auth-header text-center">
                <div className="auth-logo">
                  <FaShieldAlt />
                </div>
                <h2 className="auth-title">SocialGuard Pro</h2>
                <p className="auth-subtitle">Sosyal Medya Analiz Platformuna Hoş Geldiniz</p>
              </div>

              <form onSubmit={handleSubmit} className="auth-form">
                {error && (
                  <div className="alert alert-danger alert-dismissible fade show" role="alert">
                    <i className="fas fa-exclamation-circle me-2"></i>
                    {error}
                    <button type="button" className="btn-close" onClick={() => setError('')}></button>
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">
                    <FaEnvelope className="me-2" />
                    E-posta Adresi
                  </label>
                  <input
                    type="email"
                    className="form-control auth-input"
                    placeholder="ornek@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <FaLock className="me-2" />
                    Şifre
                  </label>
                  <div className="password-input-group">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      className="form-control auth-input"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                  </div>
                </div>

                <div className="form-group d-flex justify-content-between align-items-center">
                  <div className="form-check">
                    <input type="checkbox" className="form-check-input" id="rememberMe" />
                    <label className="form-check-label" htmlFor="rememberMe">
                      Beni Hatırla
                    </label>
                  </div>
                  <Link to="/forgot-password" className="auth-link">
                    Şifremi Unuttum
                  </Link>
                </div>

                <button
                  type="submit"
                  className="btn auth-btn w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Giriş Yapılıyor...
                    </>
                  ) : (
                    <>
                      <FaSignInAlt className="me-2" />
                      Giriş Yap
                    </>
                  )}
                </button>
              </form>

              <div className="auth-footer text-center">
                <p className="mb-0">
                  Hesabınız yok mu?{' '}
                  <Link to="/register" className="auth-link fw-bold">
                    Hemen Kayıt Olun
                  </Link>
                </p>
              </div>
            </div>

            <div className="auth-demo-info text-center mt-4">
              <div className="alert alert-info">
                <strong>Demo Bilgileri:</strong>
                <br />
                E-posta: demo@socialguard.com
                <br />
                Şifre: Demo1234
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

