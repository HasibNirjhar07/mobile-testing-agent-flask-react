import React, { useState, useEffect } from 'react';
import {
  Globe,
  Play,
  Loader,
  AlertCircle,
  CheckCircle,
  ExternalLink,
  Search,
  AlertTriangle,
} from 'lucide-react';
import clsx from 'clsx';

const API_BASE_URL = 'http://localhost:5000';

const WebTest = () => {
  const [url, setUrl] = useState('https://');
  const [sessionId, setSessionId] = useState(null);
  const [testing, setTesting] = useState(false);
  const [testProgress, setTestProgress] = useState(0);
  const [testMessage, setTestMessage] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    if (testing && sessionId) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/test/status/${sessionId}`);
          
          if (response.status === 404) {
             setError('Session expired or server restarted. Please try again.');
             setTesting(false);
             clearInterval(interval);
             return;
          }

          const data = await response.json();

          setTestProgress(data.progress || 0);
          setTestMessage(data.message || 'Testing...');

          if (data.status === 'completed') {
            setResults(data.results);
            setTesting(false);
            clearInterval(interval);
          } else if (data.status === 'failed') {
            setError(data.message || 'Testing failed');
            setTesting(false);
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling status:', err);
        }
      }, 2000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [testing, sessionId]);

  const startTest = async (e) => {
    e.preventDefault();
    if (!url) return;

    setTesting(true);
    setResults(null);
    setError(null);
    setTestProgress(10);
    setTestMessage("Initializing web agent...");

    try {
      const response = await fetch(`${API_BASE_URL}/api/web/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      
      if (data.success) {
        setSessionId(data.session_id);
      } else {
        throw new Error(data.error || "Failed to start");
      }
    } catch (err) {
      setError(err.message);
      setTesting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header with Title */}
      <div className="flex items-center justify-between pb-6 border-b border-white/5">
         <div>
            <h2 className="text-2xl font-serif text-white mb-2">Web Application Scanner</h2>
            <p className="font-mono text-zinc-500 text-xs uppercase tracking-wider">Playwright // Headless Chromium</p>
         </div>
      </div>

      {/* Input Section */}
      <div className="glass-panel p-8 rounded-2xl relative overflow-hidden">
        {/* Glow effect behind */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-electric-blue/10 blur-[100px] rounded-full pointer-events-none"></div>

        <form onSubmit={startTest} className="flex gap-4 relative z-10">
          <div className="flex-1 relative group">
            <Search className="absolute left-4 top-4 text-zinc-500 group-focus-within:text-electric-blue transition-colors" size={20} />
            <input 
              type="url" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter target URL (e.g. https://example.com)"
              className="w-full pl-12 pr-4 py-4 bg-black/40 border border-white/10 rounded-xl text-white placeholder-zinc-600 focus:ring-1 focus:ring-electric-blue focus:border-electric-blue outline-none transition-all font-mono text-sm"
              required
              disabled={testing}
            />
          </div>
          <button 
            type="submit" 
            disabled={testing}
            className={clsx(
              "px-8 py-4 rounded-xl font-bold flex items-center gap-2 transition-all duration-300 shadow-lg",
              testing 
                ? "bg-zinc-800 text-zinc-500 cursor-not-allowed" 
                : "bg-electric-blue text-white hover:shadow-[0_0_20px_rgba(41,84,255,0.4)] hover:scale-[1.02]"
            )}
          >
            {testing ? <Loader className="animate-spin" size={20} /> : <Play size={20} fill="currentColor" />}
            {testing ? 'SCANNING...' : 'START SCAN'}
          </button>
        </form>

        {testing && (
          <div className="mt-8">
             <div className="flex justify-between text-xs font-mono text-zinc-400 mb-2 uppercase tracking-wide">
                <span className="flex items-center gap-2">
                   <div className="w-1.5 h-1.5 rounded-full bg-electric-blue animate-pulse"></div>
                   {testMessage}
                </span>
                <span>{testProgress}%</span>
             </div>
             <div className="w-full bg-black/40 rounded-full h-1 overflow-hidden border border-white/5">
                <div className="bg-electric-blue h-full rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(41,84,255,0.5)]" style={{ width: `${testProgress}%` }}></div>
             </div>
          </div>
        )}

        {error && (
           <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 text-red-200 rounded-xl flex items-center gap-3">
             <AlertCircle size={20} className="text-red-500" /> 
             <span className="font-mono text-sm">{error}</span>
           </div>
        )}
      </div>

      {/* Results Section */}
      {results && results.pages && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <div className="bg-noir-800/40 border border-white/5 p-5 rounded-xl text-center">
                <div className="text-3xl font-mono font-bold text-white mb-1">{results.summary.total_pages}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-widest">Pages Explored</div>
             </div>
             <div className="bg-noir-800/40 border border-white/5 p-5 rounded-xl text-center">
                <div className="text-3xl font-mono font-bold text-red-400 mb-1">{results.summary.total_issues}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-widest">Issues Detected</div>
             </div>
             <div className="bg-noir-800/40 border border-white/5 p-5 rounded-xl text-center">
                <div className="text-3xl font-mono font-bold text-electric-blue mb-1">{results.duration?.toFixed(1)}s</div>
                <div className="text-xs text-zinc-500 uppercase tracking-widest">Duration</div>
             </div>
             <div className="bg-noir-800/40 border border-white/5 p-5 rounded-xl text-center">
                <div className="text-3xl font-mono font-bold text-emerald-400 mb-1">OK</div>
                <div className="text-xs text-zinc-500 uppercase tracking-widest">System Status</div>
             </div>
          </div>

          <div className="font-mono text-xs text-zinc-500 uppercase tracking-widest border-l-2 border-electric-blue pl-4">
              Detailed Analysis Report
          </div>

          {/* Page Cards */}
          <div className="grid gap-6">
            {results.pages.map((page, index) => (
              <div key={index} className="glass-panel overflow-hidden rounded-xl hover:border-white/10 transition-colors group">
                
                {/* Card Header */}
                <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-white/5">
                  <div className="min-w-0">
                    <h4 className="font-medium text-white truncate text-lg font-serif" title={page.title || page.url}>
                      {page.title || 'Untitled Page'}
                    </h4>
                    <a href={page.url} target="_blank" rel="noopener noreferrer" className="text-xs font-mono text-electric-blue hover:underline flex items-center gap-1 mt-1 truncate">
                      {page.url} <ExternalLink size={10} />
                    </a>
                  </div>
                  <div className="flex shrink-0 ml-4">
                    {page.issues.length > 0 ? (
                      <span className="bg-red-500/20 border border-red-500/30 text-red-300 text-xs px-3 py-1 rounded-full font-mono uppercase tracking-wide">
                        {page.issues.length} Issues
                      </span>
                    ) : (
                      <span className="bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs px-3 py-1 rounded-full font-mono uppercase tracking-wide flex items-center gap-1">
                        <CheckCircle size={10} /> Clean
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex flex-col lg:flex-row">
                  {/* Screenshot Column */}
                  {page.screenshot && (
                    <div className="lg:w-1/2 border-b lg:border-b-0 lg:border-r border-white/5 relative group/img bg-black/50">
                      <img 
                        src={`${API_BASE_URL}/screenshots/${page.screenshot}`} 
                        alt={`Screenshot of ${page.url}`} 
                        className="w-full h-auto object-cover opacity-80 group-hover/img:opacity-100 transition-opacity"
                      />
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover/img:opacity-100 transition-opacity bg-black/60 backdrop-blur-sm cursor-pointer"
                           onClick={() => window.open(`${API_BASE_URL}/screenshots/${page.screenshot}`, '_blank')}>
                         <button className="px-4 py-2 bg-white text-black font-bold rounded-full text-xs uppercase tracking-wide hover:scale-105 transition-transform">
                             Enlarge Verification
                         </button>
                      </div>
                    </div>
                  )}

                  {/* Issues Column */}
                  <div className="lg:w-1/2 p-6 max-h-[300px] overflow-y-auto custom-scrollbar">
                    {page.issues.length > 0 ? (
                      <div className="space-y-3">
                        {page.issues.map((issue, i) => (
                          <div key={i} className="flex gap-3 p-3 bg-red-500/5 rounded-lg border border-red-500/10 text-sm hover:bg-red-500/10 transition-colors">
                            <AlertTriangle className="text-red-400 shrink-0 mt-0.5" size={14} />
                            <div className="overflow-hidden">
                              <div className="font-bold text-red-300 text-xs font-mono uppercase mb-1">{issue.type}</div>
                              <div className="text-zinc-300 text-xs break-words">{issue.text || issue.message || issue.error || `Status: ${issue.status}`}</div>
                              {issue.url && <div className="text-zinc-500 text-[10px] font-mono mt-1 truncate">{issue.url}</div>}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center text-zinc-600 py-10">
                        <CheckCircle size={32} className="mb-2 opacity-20" />
                        <p className="text-xs font-mono uppercase tracking-widest">No Integrity Violations</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WebTest;
