import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Layout } from './components/Layout';
import { Produtos } from './pages/Produtos';
import { Comandas } from './pages/Comandas';
import { Dashboard } from './pages/Dashboard';
import { Landing } from './pages/Landing';

// Rota protegida básica
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem('barix_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        
        {/* Rota Protegida com Layout */}
        <Route 
          path="/app" 
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          } 
        >
          {/* Rotas Filhas injetadas no <Outlet /> do Layout */}
          <Route index element={<Dashboard />} />
          <Route path="produtos" element={<Produtos />} />
          <Route path="comandas" element={<Comandas />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}


