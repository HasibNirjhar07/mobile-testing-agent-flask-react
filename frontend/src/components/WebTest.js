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
  XCircle,
  Clock
} from 'lucide-react';

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
    <div className="p-6">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Globe className="text-blue-600" /> Web Site Testing
        </h1>
        <p className="text-gray-600">Automated smoke testing & issue detection</p>
      </header>
      
      {/* Input Section */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 mb-8">
        <form onSubmit={startTest} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3.5 text-gray-400" size={20} />
            <input 
              type="url" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter website URL (e.g. https://example.com)"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              required
              disabled={testing}
            />
          </div>
          <button 
            type="submit" 
            disabled={testing}
            className={`px-6 py-3 rounded-lg font-semibold text-white flex items-center gap-2 transition-colors ${
              testing ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {testing ? <Loader className="animate-spin" size={20} /> : <Play size={20} />}
            {testing ? 'Scanning...' : 'Start Scan'}
          </button>
        </form>
        {testing && (
          <div className="mt-6">
             <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>{testMessage}</span>
                <span>{testProgress}%</span>
             </div>
             <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: `${testProgress}%` }}></div>
             </div>
          </div>
        )}
        {error && (
           <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-2">
             <AlertCircle size={20} /> {error}
           </div>
        )}
      </div>

      {/* Results Section */}
      {results && results.pages && (
        <div className="space-y-8">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 text-center">
                <div className="text-2xl font-bold text-gray-900">{results.summary.total_pages}</div>
                <div className="text-xs text-gray-500 uppercase font-semibold">Pages Explored</div>
             </div>
             <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 text-center">
                <div className="text-2xl font-bold text-red-600">{results.summary.total_issues}</div>
                <div className="text-xs text-gray-500 uppercase font-semibold">Issues Found</div>
             </div>
             <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 text-center">
                <div className="text-2xl font-bold text-blue-600">{results.duration?.toFixed(1)}s</div>
                <div className="text-xs text-gray-500 uppercase font-semibold">Total Duration</div>
             </div>
             <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 text-center">
                <div className="text-2xl font-bold text-green-600">Completed</div>
                <div className="text-xs text-gray-500 uppercase font-semibold">Status</div>
             </div>
          </div>

          <h3 className="text-xl font-bold text-gray-900 border-l-4 border-blue-600 pl-3">Detailed Page Analysis</h3>

          {/* Page Cards */}
          <div className="grid gap-8">
            {results.pages.map((page, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                
                {/* Card Header */}
                <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900 truncate max-w-md" title={page.title || page.url}>
                      {page.title || 'Untitled Page'}
                    </h4>
                    <a href={page.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline flex items-center gap-1 mt-1">
                      {page.url} <ExternalLink size={10} />
                    </a>
                  </div>
                  <div className="flex gap-2">
                    {page.issues.length > 0 ? (
                      <span className="bg-red-100 text-red-700 text-xs px-3 py-1 rounded-full font-medium">
                        {page.issues.length} Issues
                      </span>
                    ) : (
                      <span className="bg-green-100 text-green-700 text-xs px-3 py-1 rounded-full font-medium flex items-center gap-1">
                        <CheckCircle size={12} /> Clean
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex flex-col lg:flex-row">
                  {/* Screenshot Column */}
                  {page.screenshot && (
                    <div className="lg:w-1/2 border-b lg:border-b-0 lg:border-r border-gray-200 bg-gray-100 relative group">
                      <img 
                        src={`${API_BASE_URL}/screenshots/${page.screenshot}`} 
                        alt={`Screenshot of ${page.url}`} 
                        className="w-full h-auto object-cover block"
                      />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer" 
                           onClick={() => window.open(`${API_BASE_URL}/screenshots/${page.screenshot}`, '_blank')}>
                         <span className="bg-white/90 px-3 py-1 rounded-full text-xs font-semibold shadow-sm">View Fullsize</span>
                      </div>
                    </div>
                  )}

                  {/* Issues Column */}
                  <div className="lg:w-1/2 p-6 max-h-[400px] overflow-y-auto">
                    {page.issues.length > 0 ? (
                      <div className="space-y-3">
                        {page.issues.map((issue, i) => (
                          <div key={i} className="flex gap-3 p-3 bg-red-50/50 rounded-lg border border-red-100 text-sm">
                            <AlertTriangle className="text-red-500 shrink-0 mt-0.5" size={16} />
                            <div className="overflow-hidden">
                              <div className="font-bold text-red-800 text-xs uppercase mb-0.5">{issue.type}</div>
                              <div className="text-gray-800 break-words">{issue.text || issue.message || issue.error || `Status: ${issue.status}`}</div>
                              {issue.url && <div className="text-gray-500 text-xs mt-1 truncate">{issue.url}</div>}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center text-gray-400 py-10">
                        <CheckCircle size={40} className="mb-3 text-gray-200" />
                        <p className="text-sm">No console errors or broken links detected.</p>
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
