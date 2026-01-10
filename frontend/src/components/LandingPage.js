import React from 'react';
import { motion } from 'framer-motion';
import { Smartphone, Globe, ArrowRight, Zap, Shield, Cpu, Brain } from 'lucide-react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-black text-white selection:bg-indigo-500 selection:text-white">
      {/* Navbar */}
      <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
            <Cpu size={20} className="text-white" />
          </div>
          Testing<span className="text-indigo-400">Agent</span>
        </div>
        <div className="flex gap-6 text-sm font-medium text-gray-300">
          <button className="hover:text-white transition-colors">Documentation</button>
          <button className="hover:text-white transition-colors">GitHub</button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20 lg:py-32 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold tracking-wide uppercase mb-6">
            New: Web Agent Support
          </span>
        </motion.div>
        
        <motion.h1 
          className="text-5xl lg:text-7xl font-bold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-indigo-400"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          The All-in-One<br />AI Testing Workspace
        </motion.h1>
        
        <motion.p 
          className="text-lg lg:text-xl text-gray-400 max-w-2xl mb-12 leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Deploy autonomous agents to stress-test your mobile apps and websites using the power of Computer Vision and LLMs.
        </motion.p>
      </div>

      {/* Card Grid */}
      <div className="max-w-5xl mx-auto px-6 pb-32">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Mobile Card */}
          <Link to="/dashboard/mobile" className="group">
            <motion.div 
              className="bg-gray-800/50 border border-gray-700 hover:border-indigo-500/50 p-8 rounded-2xl transition-all duration-300 hover:shadow-2xl hover:shadow-indigo-500/10 h-full relative overflow-hidden"
              whileHover={{ y: -5 }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                <Smartphone size={120} />
              </div>
              <div className="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-400 mb-6 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                <Smartphone size={24} />
              </div>
              <h3 className="text-2xl font-bold mb-3 text-white">Mobile App Testing</h3>
              <p className="text-gray-400 mb-6 text-sm leading-relaxed">
                Upload APKs and let AI explore your Android app. Detect crashes, UI issues, and validate flows using Appium & Adb.
              </p>
              <div className="flex items-center text-indigo-400 font-medium text-sm group-hover:translate-x-1 transition-transform">
                Launch Agent <ArrowRight size={16} className="ml-2" />
              </div>
            </motion.div>
          </Link>

          {/* Web Card */}
          <Link to="/dashboard/web" className="group">
            <motion.div 
              className="bg-gray-800/50 border border-gray-700 hover:border-blue-500/50 p-8 rounded-2xl transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 h-full relative overflow-hidden"
              whileHover={{ y: -5 }}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
               <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                <Globe size={120} />
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center text-blue-400 mb-6 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                <Globe size={24} />
              </div>
              <h3 className="text-2xl font-bold mb-3 text-white">Web Site Testing</h3>
              <p className="text-gray-400 mb-6 text-sm leading-relaxed">
                 Input any URL and trigger a headless browser agent. Detect broken links, console errors, and DOM anomalies using Playwright.
              </p>
              <div className="flex items-center text-blue-400 font-medium text-sm group-hover:translate-x-1 transition-transform">
                Launch Agent <ArrowRight size={16} className="ml-2" />
              </div>
            </motion.div>
          </Link>
        </div>
      </div>
      
      {/* Features */}
      <div className="border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm py-12">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8 text-center">
            <div className="flex flex-col items-center">
                <div className="p-3 bg-gray-800 rounded-full mb-4 text-indigo-400"><Zap size={20} /></div>
                <h4 className="font-semibold text-white mb-2">Fast Execution</h4>
                <p className="text-sm text-gray-400">Local execution means no queue times. Results in minutes.</p>
            </div>
            <div className="flex flex-col items-center">
                <div className="p-3 bg-gray-800 rounded-full mb-4 text-indigo-400"><Shield size={20} /></div>
                <h4 className="font-semibold text-white mb-2">Private & Secure</h4>
                <p className="text-sm text-gray-400">Everything runs on your machine. No data leaves your network unless using Cloud AI.</p>
            </div>
             <div className="flex flex-col items-center">
                <div className="p-3 bg-gray-800 rounded-full mb-4 text-indigo-400"><Brain size={20} /></div>
                <h4 className="font-semibold text-white mb-2">Smart Analysis</h4>
                <p className="text-sm text-gray-400">Agents understand context. They don't just click randomly.</p>
            </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
