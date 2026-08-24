import axios from 'axios';

// Configuração base do Axios para consumir a nossa API FastAPI
export const api = axios.create({
  baseURL: 'http://localhost:8000', // Em produção, usaríamos uma variável de ambiente (ex: import.meta.env.VITE_API_URL)
});

// Interceptor para injetar o Token JWT automaticamente em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('barix_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
