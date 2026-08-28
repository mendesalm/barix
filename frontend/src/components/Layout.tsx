import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Package, ClipboardList, DollarSign, LogOut, Settings, Menu, X, Wine, ShieldCheck } from 'lucide-react';

export function Layout() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('barix_token');
    navigate('/login');
  };

  const menuItems = [
    { to: '/app', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/app/produtos', icon: <Package size={20} />, label: 'Produtos e Estoque' },
    { to: '/app/comandas', icon: <ClipboardList size={20} />, label: 'Comandas' },
    { to: '/app/financeiro', icon: <DollarSign size={20} />, label: 'Financeiro' },
    { to: '/app/auditoria', icon: <ShieldCheck size={20} />, label: 'Auditoria' },
  ];

  return (
    <div className="flex h-screen bg-gray-50 font-sans text-gray-900 overflow-hidden">
      
      {/* Mobile Topbar */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50 flex items-center justify-between px-4 shadow-sm">
        <div className="flex items-center gap-2 text-blue-600 font-bold text-xl">
          <Wine /> Barix
        </div>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-gray-600">
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar Lateral */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 flex flex-col shadow-lg lg:shadow-sm
        transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="h-16 flex items-center justify-center border-b border-gray-100 shrink-0 mt-16 lg:mt-0">
          <h1 className="text-2xl font-bold text-blue-600 tracking-tight hidden lg:flex items-center gap-2">
            <Wine /> Barix
          </h1>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {menuItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/app'}
              onClick={() => setIsMobileMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors font-medium ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-100 shrink-0">
          <button className="flex items-center space-x-3 px-4 py-3 w-full text-left rounded-lg text-gray-600 hover:bg-gray-100 transition-colors font-medium mb-1">
            <Settings size={20} />
            <span>Configurações</span>
          </button>
          <button 
            onClick={handleLogout}
            className="flex items-center space-x-3 px-4 py-3 w-full text-left rounded-lg text-red-600 hover:bg-red-50 transition-colors font-medium"
          >
            <LogOut size={20} />
            <span>Sair do Sistema</span>
          </button>
        </div>
      </aside>

      {/* Overlay Background no Mobile */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-30 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Conteúdo Principal dinâmico injetado pelo Router (Outlet) */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden pt-16 lg:pt-0">
        <div className="p-4 md:p-8 w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
