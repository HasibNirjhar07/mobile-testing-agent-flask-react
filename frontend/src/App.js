import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import MobileTest from './components/MobileTest';
import WebTest from './components/WebTest';
import SidebarLayout from './components/SidebarLayout';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        
        <Route path="/dashboard" element={<SidebarLayout />}>
           <Route index element={<Navigate to="/dashboard/mobile" replace />} />
           <Route path="mobile" element={<MobileTest />} />
           <Route path="web" element={<WebTest />} />
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;