import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Smartphone, Globe, Home, Command, Terminal as TerminalIcon, Settings, LogOut, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const SidebarItem = ({ to, icon: Icon, label, isActive }) => (
  <NavLink to={to} className="block mb-2">
    <div className={clsx(
      "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group",
      isActive 
        ? "bg-white/10 text-white border border-white/10 shadow-lg backdrop-blur-sm" 
        : "text-zinc-500 hover:text-white hover:bg-white/5"
    )}>
      <Icon size={18} className={clsx("transition-colors", isActive ? "text-electric-blue" : "group-hover:text-white")} />
      <span className="font-medium text-sm">{label}</span>
      {isActive && (
        <motion.div 
          layoutId="sidebar-active"
          className="ml-auto w-1.5 h-1.5 rounded-full bg-electric-blue shadow-[0_0_8px_rgba(41,84,255,0.8)]"
        />
      )}
    </div>
  </NavLink>
);



const DashboardLayout = () => {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-noir-900 text-white overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-white/5 bg-noir-800/20 backdrop-blur-xl p-4 z-20">
        <div className="flex items-center gap-3 px-4 py-6 mb-8">
            <div className="w-8 h-8 bg-gradient-to-br from-electric-blue to-electric-purple rounded-lg flex items-center justify-center shadow-lg">
                <Cpu size={16} className="text-white" />
            </div>
          <span className="font-serif font-bold text-lg tracking-tight">Agent_Zero</span>
        </div>

        <nav className="flex-1">
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-widest px-4 mb-4 mt-2">Platform</div>
          <SidebarItem to="/" icon={Home} label="Overview" isActive={location.pathname === '/'} />
          
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-widest px-4 mb-4 mt-6">Agents</div>
          <SidebarItem 
            to="/dashboard/mobile" 
            icon={Smartphone} 
            label="Mobile Agent" 
            isActive={location.pathname.includes('mobile')} 
          />
          <SidebarItem 
            to="/dashboard/web" 
            icon={Globe} 
            label="Web Agent" 
            isActive={location.pathname.includes('web')} 
          />
        </nav>

        <div className="mt-auto pt-6 border-t border-white/5">
          <button className="flex items-center gap-3 px-4 py-3 text-zinc-500 hover:text-white transition-colors w-full rounded-xl hover:bg-white/5">
            <Settings size={18} />
            <span className="text-sm">Settings</span>
          </button>
          <div className="flex items-center gap-3 mt-4 px-4">
             <div className="w-8 h-8 rounded-full bg-zinc-800 border border-white/10 flex items-center justify-center text-xs font-bold font-mono">
                 HN
             </div>
             <div className="flex-1 min-w-0">
                 <div className="text-sm font-medium truncate">Hasib Nirjhar</div>
                 <div className="text-xs text-zinc-500 truncate">Pro Plan</div>
             </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {/* Top Header / Breadcrumb area could go here */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-noir-900/50 backdrop-blur-md z-10">
            <div className="flex items-center gap-2 text-sm font-mono text-zinc-500">
                <span>DASHBOARD</span>
                <span>/</span>
                <span className="text-white">{location.pathname.split('/').pop().toUpperCase()}</span>
            </div>
            <div className="flex items-center gap-4">
                 <button className="p-2 text-zinc-500 hover:text-white transition-colors bg-white/5 rounded-lg">
                    <Command size={16} />
                 </button>
            </div>
        </header>

        <div className="flex-1 relative overflow-y-auto overflow-x-hidden p-8 scroll-smooth">
           {/* Page Transition Wrapper */}
           <AnimatePresence mode='wait'>
             <motion.div
               key={location.pathname}
               initial={{ opacity: 0, y: 10, filter: 'blur(10px)' }}
               animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
               exit={{ opacity: 0, y: -10, filter: 'blur(10px)' }}
               transition={{ duration: 0.3 }}
               className="h-full"
             >
                <Outlet />
             </motion.div>
           </AnimatePresence>
        </div>
      </main>

      {/* Right Side Terminal Removed */}
    </div>
  );
};

export default DashboardLayout;
