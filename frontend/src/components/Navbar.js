import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FaShieldAlt, FaCircle, FaUser, FaSignOutAlt } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const Navbar = ({ apiStatus }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    
    // Başarı mesajı göster
    const toast = document.createElement('div');
    toast.className = 'custom-toast success';
    toast.innerHTML = `
      <div class="toast-content">
        <i class="fas fa-check-circle"></i>
        <span>Başarıyla çıkış yaptınız!</span>
      </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{ background: 'rgba(44, 62, 80, 0.95)', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/">
          <FaShieldAlt className="me-2" style={{ fontSize: '1.5rem' }} />
          SocialGuard Pro
        </Link>
        
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {isAuthenticated && (
              <>
                <li className="nav-item">
                  <Link 
                    className={`nav-link ${isActive('/') ? 'active' : ''}`} 
                    to="/"
                  >
                    Sosyal Medya Analizi
                  </Link>
                </li>
                <li className="nav-item">
                  <Link 
                    className={`nav-link ${isActive('/manual-analysis') ? 'active' : ''}`} 
                    to="/manual-analysis"
                  >
                    Manuel Analiz
                  </Link>
                </li>
              </>
            )}
          </ul>

          <div className="d-flex align-items-center gap-3">
            {isAuthenticated ? (
              <>
                {/* User Dropdown */}
                <div className="dropdown">
                  <button 
                    className="btn btn-link text-white text-decoration-none d-flex align-items-center gap-2 p-2"
                    onClick={() => setShowDropdown(!showDropdown)}
                    onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                  >
                    <div 
                      className="d-flex align-items-center justify-content-center rounded-circle bg-white text-primary"
                      style={{ width: '35px', height: '35px', fontWeight: 'bold' }}
                    >
                      {user?.name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <span className="d-none d-md-inline fw-500">{user?.name || 'Kullanıcı'}</span>
                  </button>
                  
                  {showDropdown && (
                    <div 
                      className="dropdown-menu dropdown-menu-end show" 
                      style={{ 
                        position: 'absolute', 
                        right: 0, 
                        top: '100%',
                        minWidth: '200px',
                        boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                        borderRadius: '10px',
                        marginTop: '0.5rem'
                      }}
                    >
                      <div className="px-3 py-2 border-bottom">
                        <p className="mb-0 fw-bold">{user?.name}</p>
                        <small className="text-muted">{user?.email}</small>
                      </div>
                      <Link 
                        className="dropdown-item d-flex align-items-center gap-2 py-2" 
                        to="/profile"
                      >
                        <FaUser /> Profil
                      </Link>
                      <hr className="dropdown-divider" />
                      <button 
                        className="dropdown-item d-flex align-items-center gap-2 py-2 text-danger"
                        onClick={handleLogout}
                      >
                        <FaSignOutAlt /> Çıkış Yap
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="d-flex gap-2">
                <Link 
                  to="/login" 
                  className="btn btn-outline-light btn-sm"
                  style={{ borderRadius: '20px', padding: '0.5rem 1.5rem' }}
                >
                  Giriş Yap
                </Link>
                <Link 
                  to="/register" 
                  className="btn btn-light btn-sm"
                  style={{ borderRadius: '20px', padding: '0.5rem 1.5rem' }}
                >
                  Kayıt Ol
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
