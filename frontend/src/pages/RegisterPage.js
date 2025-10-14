import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaUser, FaEnvelope, FaLock, FaUserPlus, FaShieldAlt, FaEye, FaEyeSlash, FaCheck, FaTimes } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validatePassword = (password) => {
    const requirements = {
      minLength: password.length >= 8,
      hasUpperCase: /[A-Z]/.test(password),
      hasLowerCase: /[a-z]/.test(password),
      hasNumber: /[0-9]/.test(password)
    };
    return requirements;
  };

  const passwordRequirements = validatePassword(formData.password);
  const isPasswordValid = Object.values(passwordRequirements).every(req => req);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validasyon kontrolleri
    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Lütfen tüm alanları doldurun!');
      return;
    }

    if (!acceptTerms) {
      setError('Kullanım koşullarını kabul etmelisiniz!');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Şifreler eşleşmiyor!');
      return;
    }

    if (!isPasswordValid) {
      setError('Şifre gereksinimleri karşılanmıyor!');
      return;
    }

    setLoading(true);

    const result = await register(formData.name, formData.email, formData.password);
    
    setLoading(false);

    if (result.success) {
      // Başarı mesajı göster
      const toast = document.createElement('div');
      toast.className = 'custom-toast success';
      toast.innerHTML = `
        <div class="toast-content">
          <i class="fas fa-check-circle"></i>
          <span>Kayıt başarılı! Yönlendiriliyorsunuz...</span>
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
        <div className="row justify-content-center align-items-center min-vh-100 py-5">
          <div className="col-lg-6 col-md-8">
            <div className="auth-card">
              <div className="auth-header text-center">
                <div className="auth-logo">
                  <FaShieldAlt />
                </div>
                <h2 className="auth-title">Kayıt Ol</h2>
                <p className="auth-subtitle">Hemen hesap oluşturun ve analize başlayın</p>
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
                    <FaUser className="me-2" />
                    Ad Soyad
                  </label>
                  <input
                    type="text"
                    name="name"
                    className="form-control auth-input"
                    placeholder="Ad Soyad"
                    value={formData.name}
                    onChange={handleChange}
                    disabled={loading}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <FaEnvelope className="me-2" />
                    E-posta Adresi
                  </label>
                  <input
                    type="email"
                    name="email"
                    className="form-control auth-input"
                    placeholder="ornek@email.com"
                    value={formData.email}
                    onChange={handleChange}
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
                      name="password"
                      className="form-control auth-input"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleChange}
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
                  
                  {/* Şifre Gereksinimleri */}
                  {formData.password && (
                    <div className="password-requirements mt-2">
                      <small className={passwordRequirements.minLength ? 'text-success' : 'text-muted'}>
                        {passwordRequirements.minLength ? <FaCheck /> : <FaTimes />} En az 8 karakter
                      </small>
                      <br />
                      <small className={passwordRequirements.hasUpperCase ? 'text-success' : 'text-muted'}>
                        {passwordRequirements.hasUpperCase ? <FaCheck /> : <FaTimes />} En az bir büyük harf
                      </small>
                      <br />
                      <small className={passwordRequirements.hasLowerCase ? 'text-success' : 'text-muted'}>
                        {passwordRequirements.hasLowerCase ? <FaCheck /> : <FaTimes />} En az bir küçük harf
                      </small>
                      <br />
                      <small className={passwordRequirements.hasNumber ? 'text-success' : 'text-muted'}>
                        {passwordRequirements.hasNumber ? <FaCheck /> : <FaTimes />} En az bir rakam
                      </small>
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <FaLock className="me-2" />
                    Şifre Tekrar
                  </label>
                  <div className="password-input-group">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      name="confirmPassword"
                      className="form-control auth-input"
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                  </div>
                  {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                    <small className="text-danger">
                      <FaTimes /> Şifreler eşleşmiyor
                    </small>
                  )}
                  {formData.confirmPassword && formData.password === formData.confirmPassword && (
                    <small className="text-success">
                      <FaCheck /> Şifreler eşleşiyor
                    </small>
                  )}
                </div>

                <div className="form-group">
                  <div className="form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="acceptTerms"
                      checked={acceptTerms}
                      onChange={(e) => setAcceptTerms(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="acceptTerms">
                      <Link to="/terms" className="auth-link">Kullanım Koşullarını</Link> ve{' '}
                      <Link to="/privacy" className="auth-link">Gizlilik Politikasını</Link> kabul ediyorum
                    </label>
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn auth-btn w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Kayıt Yapılıyor...
                    </>
                  ) : (
                    <>
                      <FaUserPlus className="me-2" />
                      Kayıt Ol
                    </>
                  )}
                </button>
              </form>

              <div className="auth-footer text-center">
                <p className="mb-0">
                  Zaten hesabınız var mı?{' '}
                  <Link to="/login" className="auth-link fw-bold">
                    Giriş Yapın
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

