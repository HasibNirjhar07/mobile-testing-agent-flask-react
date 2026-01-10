import React, { useState, useEffect } from 'react';
import {
  Upload,
  Play,
  Settings,
  Brain,
  Download,
  AlertCircle,
  CheckCircle,
  Loader,
  RefreshCw,
} from 'lucide-react';
import clsx from 'clsx';

const API_BASE_URL = 'http://localhost:5000';

const MobileTest = () => {
  const [step, setStep] = useState(1);
  const [apkFile, setApkFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [apkFilepath, setApkFilepath] = useState(null);
  const [testMode, setTestMode] = useState('auto');
  const [credentials, setCredentials] = useState({ hasLogin: false, username: '', password: '', email: '' });
  const [testContext, setTestContext] = useState('');
  const [aiInstructions, setAiInstructions] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [testProgress, setTestProgress] = useState(0);
  const [testMessage, setTestMessage] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    if (testing && sessionId) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/test/status/${sessionId}`);
          const data = await response.json();

          setTestProgress(data.progress || 0);
          setTestMessage(data.message || 'Testing...');

          if (data.status === 'completed') {
            setTestResults(data.results);
            setTesting(false);
            setStep(4);
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

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.apk')) {
      setError('Please upload a valid APK file');
      return;
    }

    setError(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setApkFile(file);
          setSessionId(response.session_id);
          setApkFilepath(response.filepath);
          setStep(2);
          setUploadProgress(0);
        } else {
          setError('Upload failed. Please try again.');
          setUploadProgress(0);
        }
      });

      xhr.addListener && xhr.addEventListener('error', () => { // Fixed typo listener -> addEventListener
        setError('Upload failed. Please check your connection.');
        setUploadProgress(0);
      });

      xhr.open('POST', `${API_BASE_URL}/api/upload`);
      xhr.send(formData);
    } catch (err) {
      setError('Failed to upload APK: ' + err.message);
      setUploadProgress(0);
    }
  };

  const startTesting = async () => {
    if (!sessionId) {
      setError('No APK uploaded');
      return;
    }

    setError(null);
    setTesting(true);
    setTestProgress(0);
    setTestMessage('Initializing AI core...');

    try {
      const testData = {
        session_id: sessionId,
        test_mode: testMode,
        credentials,
        test_context: testContext,
        ai_instructions: aiInstructions,
      };

      if (apkFilepath) testData.apk_filepath = apkFilepath;

      const response = await fetch(`${API_BASE_URL}/api/mobile/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData),
      });

      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to start testing');
      }
    } catch (err) {
      setError('Failed to start testing: ' + err.message);
      setTesting(false);
    }
  };

  const downloadReport = () => { if (sessionId) window.open(`${API_BASE_URL}/api/report/${sessionId}`, '_blank'); };
  const viewReport = () => { if (sessionId) window.open(`${API_BASE_URL}/api/report/view/${sessionId}`, '_blank'); };
  
  const resetTest = () => {
    setStep(1); setApkFile(null); setSessionId(null); setApkFilepath(null);
    setTestResults(null); setTestMode('auto'); setCredentials({ hasLogin: false, username: '', password: '', email: '' });
    setTestContext(''); setAiInstructions(''); setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between pb-6 border-b border-white/5">
         <div>
            <h2 className="text-2xl font-serif text-white mb-2">Android Autonomous Agent</h2>
            <p className="font-mono text-zinc-500 text-xs uppercase tracking-wider">Powered by Gemini 1.5 Pro</p>
         </div>
         {/* Steps Indicator */}
         <div className="flex items-center gap-2">
            {[1, 2, 3, 4].map(s => (
               <div key={s} className={clsx("w-2 h-2 rounded-full transition-colors", step >= s ? "bg-electric-purple" : "bg-zinc-800")} />
            ))}
         </div>
      </div>
      
      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-4 animate-in fade-in slide-in-from-top-2">
          <AlertCircle className="text-red-500 mt-1 shrink-0" size={20} />
          <div>
            <p className="font-mono text-red-300 font-bold mb-1">[SYSTEM ERROR]</p>
            <p className="text-sm text-zinc-400">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="ml-auto text-zinc-500 hover:text-white">✕</button>
        </div>
      )}

       <main className="glass-panel rounded-2xl p-8 relative overflow-hidden min-h-[400px]">
          {/* Step 1: Upload APK */}
          {step === 1 && (
            <div className="flex flex-col items-center justify-center h-full py-12">
              <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-6 animate-pulse-fast">
                 <Upload className="text-electric-purple" size={32} />
              </div>
              <h2 className="text-2xl font-serif text-white mb-2">Initialize Payload</h2>
              <p className="text-zinc-500 mb-8 max-w-sm text-center">Drag and drop your .apk file to begin the analysis sequence.</p>
              
              <label className="cursor-pointer group">
                <div className={clsx(
                   "w-[400px] border-2 border-dashed rounded-xl p-10 transition-all duration-300 text-center relative",
                   uploadProgress > 0 ? "border-electric-purple bg-electric-purple/5" : "border-white/10 hover:border-electric-purple hover:bg-white/5"
                )}>
                  {uploadProgress > 0 ? (
                    <div>
                      <Loader className="mx-auto mb-4 text-electric-purple animate-spin" size={32} />
                      <div className="font-mono text-electric-purple text-lg">{uploadProgress}%</div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-zinc-300 font-medium group-hover:text-white transition-colors">
                         {apkFile ? apkFile.name : 'Select APK File'}
                      </p>
                    </div>
                  )}
                </div>
                <input type="file" accept=".apk" onChange={handleFileUpload} className="hidden" disabled={uploadProgress > 0} />
              </label>
            </div>
          )}

          {/* Step 2: Configuration */}
          {step === 2 && (
            <div className="animate-in fade-in slide-in-from-right-4">
              <h2 className="text-xl font-serif text-white mb-6">Mission Configuration</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                {[
                  { id: 'auto', title: 'Auto-Pilot', desc: 'Full autonomy', icon: Brain },
                  { id: 'guided', title: 'Guided', desc: 'Context aware', icon: Settings },
                  { id: 'custom', title: 'Manual Override', desc: 'Specific prompts', icon: AlertCircle },
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setTestMode(mode.id)}
                    className={clsx(
                      "p-4 text-left border rounded-xl transition-all duration-300 relative overflow-hidden group",
                      testMode === mode.id ? "border-electric-purple bg-electric-purple/10" : "border-white/10 hover:bg-white/5"
                    )}
                  >
                    <div className="relative z-10 flex flex-col h-full">
                       <mode.icon className={clsx("mb-3", testMode === mode.id ? "text-electric-purple" : "text-zinc-500")} size={24} />
                       <h3 className="font-mono font-bold text-white text-sm mb-1">{mode.title}</h3>
                       <p className="text-xs text-zinc-500">{mode.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
              
              <div className="flex gap-4 pt-4 border-t border-white/5">
                <button onClick={() => setStep(1)} className="px-6 py-3 text-zinc-400 hover:text-white transition-colors">BACK</button>
                <div className="flex-1"></div>
                <button onClick={() => setStep(3)} className="px-8 py-3 bg-white text-black font-bold rounded-lg hover:bg-zinc-200 transition-colors">CONTINUE</button>
              </div>
            </div>
          )}

          {/* Step 3: Confirmation */}
          {step === 3 && !testing && (
            <div className="max-w-md mx-auto py-12 text-center animate-in zoom-in-95">
              <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                 <CheckCircle className="text-emerald-500" size={32} />
              </div>
              <h2 className="text-2xl font-serif text-white mb-2">Ready for Launch</h2>
              <div className="font-mono text-zinc-500 text-sm mb-8">Target: {apkFile?.name}</div>
              
              <div className="flex gap-4 justify-center">
                <button onClick={() => setStep(2)} className="px-6 py-3 text-zinc-400 hover:text-white">Back</button>
                <button 
                  onClick={startTesting} 
                  className="px-8 py-3 bg-electric-purple text-white font-bold rounded-lg hover:shadow-[0_0_20px_rgba(189,0,255,0.4)] transition-all flex items-center gap-2"
                >
                  <Play size={18} fill="currentColor" /> ENABLE AGENT
                </button>
              </div>
            </div>
          )}

          {/* Testing Progress */}
          {testing && (
            <div className="text-center py-20">
              <div className="relative w-24 h-24 mx-auto mb-8">
                 <div className="absolute inset-0 border-4 border-zinc-800 rounded-full"></div>
                 <div className="absolute inset-0 border-4 border-electric-purple border-t-transparent rounded-full animate-spin"></div>
                 <Brain className="absolute inset-0 m-auto text-white animate-pulse" size={32} />
              </div>
              <h2 className="text-xl font-mono text-white mb-2 uppercase tracking-widest">{testMessage}</h2>
              <p className="text-zinc-500 font-mono text-xs">Analyzing application logic...</p>
            </div>
          )}

          {/* Step 4: Results */}
          {step === 4 && testResults && (
            <div className="animate-in slide-in-from-bottom-8">
              <div className="flex items-center gap-4 mb-8">
                 <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                    <CheckCircle className="text-emerald-500" size={24} />
                 </div>
                 <div>
                    <h2 className="text-xl font-serif text-white">Analysis Complete</h2>
                    <p className="text-zinc-500 text-sm">Session ID: {sessionId?.slice(0,8)}</p>
                 </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mb-8">
                <div className="p-4 bg-white/5 rounded-xl text-center border border-white/5"><div className="text-2xl font-mono text-white mb-1">{testResults.total_tests}</div><div className="text-[10px] text-zinc-500 uppercase tracking-widest">Total Tests</div></div>
                <div className="p-4 bg-white/5 rounded-xl text-center border border-emerald-500/20"><div className="text-2xl font-mono text-emerald-400 mb-1">{testResults.passed}</div><div className="text-[10px] text-zinc-500 uppercase tracking-widest">Passed</div></div>
                <div className="p-4 bg-white/5 rounded-xl text-center border border-red-500/20"><div className="text-2xl font-mono text-red-400 mb-1">{testResults.failed}</div><div className="text-[10px] text-zinc-500 uppercase tracking-widest">Failed</div></div>
                <div className="p-4 bg-white/5 rounded-xl text-center border border-white/5"><div className="text-2xl font-mono text-electric-purple mb-1">{testResults.screens_explored}</div><div className="text-[10px] text-zinc-500 uppercase tracking-widest">Screens</div></div>
              </div>

               {testResults.ai_insights && (
                  <div className="mb-8 p-6 bg-electric-purple/5 border border-electric-purple/20 rounded-xl">
                    <h3 className="font-mono text-electric-purple mb-4 flex items-center gap-2 text-xs uppercase tracking-widest">
                       <Brain size={14} /> Agent Intelligence Report
                    </h3>
                    <p className="text-zinc-300 leading-relaxed font-light">
                      {testResults.ai_insights}
                    </p>
                  </div>
                )}

              <div className="flex gap-4">
                <button onClick={resetTest} className="px-6 py-3 bg-white/5 text-white rounded-lg hover:bg-white/10 flex items-center gap-2"><RefreshCw size={16}/> NEW SESSION</button>
                <div className="flex-1"></div>
                <button onClick={viewReport} className="px-6 py-3 bg-white text-black font-bold rounded-lg hover:bg-zinc-200">VIEW FULL REPORT</button>
                <button onClick={downloadReport} className="p-3 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700"><Download size={20}/></button>
              </div>
            </div>
          )}
       </main>
    </div>
  );
};

export default MobileTest;
