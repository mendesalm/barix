import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Package, ClipboardList, DollarSign, LogOut, Settings } from 'lucide-react';

export function Layout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('barix_token');
    navigate('/login');
  };

  const menuItems = [
    { to: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/produtos', icon: <Package size={20} />, label: 'Produtos e Estoque' },
    { to: '/comandas', icon: <ClipboardList size={20} />, label: 'Comandas' },
    { to: '/financeiro', icon: <DollarSign size={20} />, label: 'Financeiro' },
  ];

  return (
    <div className="flex h-screen bg-gray-50 font-sans text-gray-900">
      {/* Sidebar Lateral */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        <div className="h-16 flex items-center justify-center border-b border-gray-100">
          <h1 className="text-2xl font-bold text-blue-600 tracking-tight">Barix</h1>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {menuItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
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

        <div className="p-4 border-t border-gray-100">
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

      {/* Conteúdo Principal dinâmico injetado pelo Router (Outlet) */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
