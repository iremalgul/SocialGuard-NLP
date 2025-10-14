import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

// API base URL - Production'da REACT_APP_API_URL environment variable'ından al
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axios instance with interceptor for auth token
const api = axios.create({
  baseURL: API_URL,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token geçersiz, kullanıcıyı çıkış yap
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // localStorage'dan kullanıcı bilgilerini yükle ve doğrula
    const initAuth = async () => {
      const storedUser = localStorage.getItem('user');
      const token = localStorage.getItem('token');
      
      if (storedUser && token) {
        try {
          // Token'ın geçerliliğini kontrol et
          const response = await api.get('/api/auth/me');
          setUser(response.data);
          // Kullanıcı bilgisini güncelle
          localStorage.setItem('user', JSON.stringify(response.data));
        } catch (e) {
          console.error('Token validation failed:', e);
          localStorage.removeItem('user');
          localStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };
    
    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      // API'ye gerçek login isteği
      const response = await api.post('/api/auth/login', { email, password });
      
      const { access_token, user: userData } = response.data;
      
      // Token ve kullanıcı bilgilerini kaydet
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.' 
      };
    }
  };

  const register = async (name, email, password) => {
    try {
      // API'ye gerçek register isteği
      const response = await api.post('/api/auth/register', { name, email, password });
      
      const { access_token, user: userData } = response.data;
      
      // Token ve kullanıcı bilgilerini kaydet
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Register error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Kayıt başarısız. Lütfen tekrar deneyin.' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
    api // API instance'ı diğer componentlerde kullanmak için
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Export api for use in other components
export { api };

