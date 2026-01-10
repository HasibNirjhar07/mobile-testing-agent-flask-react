import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { Smartphone, Globe, Home, Menu } from 'lucide-react';

const SidebarLayout = () => {
  
  return (
    <div className="min-h-screen bg-gray-50 flex font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 fixed inset-y-0 left-0 z-10 hidden md:flex flex-col">
        <div className="p-6 border-b border-gray-100 flex items-center gap-2">
           <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">T</div>
           <span className="font-bold text-gray-900 text-lg">TestingPlatform</span>
        </div>
        
        <nav className="p-4 space-y-1 flex-1">
          <NavLink 
            to="/" 
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-colors mb-4"
          >
            <Home size={18} /> Home
          </NavLink>
          
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-4 mb-2 mt-6">Agents</div>
          
          <NavLink 
            to="/dashboard/mobile" 
            className={({ isActive }) => 
              `flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                isActive 
                ? 'bg-indigo-50 text-indigo-700 border-r-2 border-indigo-600' 
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Smartphone size={18} /> Mobile Testing
          </NavLink>
          
          <NavLink 
            to="/dashboard/web" 
            className={({ isActive }) => 
              `flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                isActive 
                ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600' 
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Globe size={18} /> Web Testing
          </NavLink>
        </nav>
        
        <div className="p-4 border-t border-gray-100">
           <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-xs">U</div>
              <div className="text-sm">
                 <p className="font-medium text-gray-900">User Workspace</p>
                 <p className="text-xs text-gray-500">Local Environment</p>
              </div>
           </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 md:ml-64">
        {/* Mobile Header */}
        <div className="md:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between sticky top-0 z-20">
           <span className="font-bold text-gray-900">TestingPlatform</span>
           <button className="p-2 text-gray-600"><Menu size={24} /></button>
        </div>
        
        <main className="p-4 md:p-8 max-w-7xl mx-auto">
           <Outlet />
        </main>
      </div>
    </div>
  );
};

export default SidebarLayout;
