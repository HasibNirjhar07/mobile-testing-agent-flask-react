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

const API_BASE_URL = 'http://localhost:5000';

const MobileTestingUI = () => {
  const [step, setStep] = useState(1);
  const [apkFile, setApkFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [apkFilepath, setApkFilepath] = useState(null); // Store the filepath from backend
  const [testMode, setTestMode] = useState('auto');
  const [credentials, setCredentials] = useState({
    hasLogin: false,
    username: '',
    password: '',
    email: '',
  });
  const [testContext, setTestContext] = useState('');
  const [aiInstructions, setAiInstructions] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [testProgress, setTestProgress] = useState(0);
  const [testMessage, setTestMessage] = useState('');
  const [error, setError] = useState(null);

  // Poll test status
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

    return () => {
      if (interval) clearInterval(interval);
    };
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
          console.log('Upload response:', response); // Debug log
          setApkFile(file);
          setSessionId(response.session_id);
          setApkFilepath(response.filepath); // Store the filepath from backend
          setStep(2);
          setUploadProgress(0);
        } else {
          setError('Upload failed. Please try again.');
          setUploadProgress(0);
        }
      });

      xhr.addEventListener('error', () => {
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
    setTestMessage('Initializing...');

    try {
      const testData = {
        session_id: sessionId,
        test_mode: testMode,
        credentials,
        test_context: testContext,
        ai_instructions: aiInstructions,
      };

      // Only include apk_filepath if we have it (backend can find it automatically if not provided)
      if (apkFilepath) {
        testData.apk_filepath = apkFilepath;
      }

      console.log('Starting test with data:', testData); // Debug log

      const response = await fetch(`${API_BASE_URL}/api/test/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData),
      });

      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to start testing');
      }
      
      console.log('Test started successfully:', data); // Debug log
    } catch (err) {
      console.error('Start testing error:', err); // Debug log
      setError('Failed to start testing: ' + err.message);
      setTesting(false);
    }
  };

  const downloadReport = () => {
    if (sessionId) window.open(`${API_BASE_URL}/api/report/${sessionId}`, '_blank');
  };

  const viewReport = () => {
    if (sessionId) window.open(`${API_BASE_URL}/api/report/view/${sessionId}`, '_blank');
  };

  const resetTest = () => {
    setStep(1);
    setApkFile(null);
    setSessionId(null);
    setApkFilepath(null);
    setTestResults(null);
    setTestMode('auto');
    setCredentials({ hasLogin: false, username: '', password: '', email: '' });
    setTestContext('');
    setAiInstructions('');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-10 text-center">
          <div className="inline-flex items-center gap-2.5 bg-gray-100 px-4 py-2 rounded-lg mb-3">
            <Brain className="text-indigo-600" size={22} />
            <h1 className="text-xl font-semibold text-gray-900">AI Mobile Testing Agent</h1>
          </div>
          <p className="text-gray-600 text-sm">
            Automated mobile app testing powered by generative AI
          </p>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="text-red-500 mt-0.5 mr-3 flex-shrink-0" size={20} />
            <div className="flex-1">
              <p className="font-medium text-red-800">Error</p>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="text-gray-500 hover:text-gray-700">
              ✕
            </button>
          </div>
        )}

        {/* Progress Steps */}
        <div className="flex justify-center mb-10">
          <div className="flex items-center gap-3">
            {[1, 2, 3, 4].map((s) => (
              <React.Fragment key={s}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step >= s
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {s}
                </div>
                {s < 4 && <div className={`w-8 h-0.5 ${step > s ? 'bg-indigo-600' : 'bg-gray-200'}`} />}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Main Card */}
        <main className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-6 md:p-8">
            {/* Step 1: Upload APK */}
            {step === 1 && (
              <div className="text-center">
                <Upload className="mx-auto mb-4 text-gray-500" size={48} />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload APK File</h2>
                <p className="text-gray-600 mb-6 text-sm">
                  Select an Android APK to begin automated testing
                </p>

                <label className="cursor-pointer block">
                  <div
                    className={`border-2 border-dashed rounded-lg p-10 transition-colors ${
                      uploadProgress > 0
                        ? 'border-indigo-300 bg-indigo-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {uploadProgress > 0 ? (
                      <div>
                        <Loader className="mx-auto mb-3 text-indigo-600 animate-spin" size={32} />
                        <p className="font-medium text-gray-800 mb-2">Uploading... {uploadProgress}%</p>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                          <div
                            className="bg-indigo-600 h-2 rounded-full"
                            style={{ width: `${uploadProgress}%` }}
                          />
                        </div>
                      </div>
                    ) : (
                      <div>
                        <Upload className="mx-auto mb-2 text-gray-400" size={32} />
                        <p className="text-gray-700 font-medium">
                          {apkFile ? apkFile.name : 'Click to upload APK'}
                        </p>
                        <p className="text-gray-500 text-sm mt-1">Supported: .apk files only</p>
                      </div>
                    )}
                  </div>
                  <input
                    type="file"
                    accept=".apk"
                    onChange={handleFileUpload}
                    className="hidden"
                    disabled={uploadProgress > 0}
                  />
                </label>
              </div>
            )}

            {/* Step 2: Configuration */}
            {step === 2 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Test Configuration</h2>

                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-3">Testing Mode</label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { id: 'auto', title: 'Fully Automated', desc: 'AI handles all decisions', icon: Brain },
                      { id: 'guided', title: 'Guided Testing', desc: 'Provide context', icon: Settings },
                      { id: 'custom', title: 'Custom Instructions', desc: 'Detailed AI prompts', icon: AlertCircle },
                    ].map((mode) => (
                      <button
                        key={mode.id}
                        type="button"
                        onClick={() => setTestMode(mode.id)}
                        className={`p-4 text-left border rounded-lg transition-colors ${
                          testMode === mode.id
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <mode.icon
                            className={`mt-0.5 flex-shrink-0 ${
                              testMode === mode.id ? 'text-indigo-600' : 'text-gray-500'
                            }`}
                            size={20}
                          />
                          <div>
                            <h3 className="font-medium text-gray-900">{mode.title}</h3>
                            <p className="text-sm text-gray-600 mt-1">{mode.desc}</p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {testMode !== 'auto' && (
                  <div className="mb-6 p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <input
                        type="checkbox"
                        id="hasLogin"
                        checked={credentials.hasLogin}
                        onChange={(e) => setCredentials({ ...credentials, hasLogin: e.target.checked })}
                        className="rounded text-indigo-600 focus:ring-indigo-500"
                      />
                      <label htmlFor="hasLogin" className="text-sm font-medium text-gray-700">
                        App requires login?
                      </label>
                    </div>

                    {credentials.hasLogin && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                        <input
                          type="text"
                          placeholder="Username"
                          value={credentials.username}
                          onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                        <input
                          type="email"
                          placeholder="Email (optional)"
                          value={credentials.email}
                          onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                        <input
                          type="password"
                          placeholder="Password"
                          value={credentials.password}
                          onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 md:col-span-2"
                        />
                      </div>
                    )}
                  </div>
                )}

                {testMode === 'guided' && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Testing Context (Optional)
                    </label>
                    <textarea
                      value={testContext}
                      onChange={(e) => setTestContext(e.target.value)}
                      placeholder="e.g., This is a banking app. Test login, balance check, and fund transfer."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                      rows={3}
                    />
                  </div>
                )}

                {testMode === 'custom' && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Custom AI Instructions
                    </label>
                    <textarea
                      value={aiInstructions}
                      onChange={(e) => setAiInstructions(e.target.value)}
                      placeholder="e.g., Test checkout with invalid card. Verify error messages. Capture screenshots at each step."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                      rows={4}
                    />
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md text-sm font-medium hover:bg-gray-200"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={() => setStep(3)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 flex-1"
                  >
                    Continue
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Confirmation or Testing */}
            {step === 3 && !testing && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Confirm & Start Testing</h2>

                <div className="space-y-4 mb-6">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">APK File</p>
                    <p className="text-gray-900">{apkFile?.name}</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Mode</p>
                    <p className="text-gray-900 capitalize">{testMode.replace('-', ' ')}</p>
                  </div>

                  {credentials.hasLogin && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Credentials</p>
                      <p className="text-gray-900">Username: {credentials.username}</p>
                    </div>
                  )}

                  {testContext && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Context</p>
                      <p className="text-gray-900">{testContext}</p>
                    </div>
                  )}
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                  <div className="flex gap-2">
                    <AlertCircle className="text-yellow-600 mt-0.5 flex-shrink-0" size={18} />
                    <p className="text-sm text-yellow-800">
                      Ensure an Android emulator is running or a physical device is connected via ADB.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setStep(2)}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md text-sm font-medium hover:bg-gray-200"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={startTesting}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 flex items-center justify-center gap-2 flex-1"
                  >
                    <Play size={16} /> Start AI Testing
                  </button>
                </div>
              </div>
            )}

            {testing && (
              <div className="text-center py-8">
                <Loader className="mx-auto mb-4 text-indigo-600 animate-spin" size={40} />
                <h2 className="text-lg font-semibold text-gray-900 mb-2">AI Testing in Progress</h2>
                <p className="text-gray-600 text-sm mb-6">{testMessage}</p>

                <div className="max-w-md mx-auto">
                  <div className="flex justify-between text-xs text-gray-600 mb-2">
                    <span>Progress</span>
                    <span>{testProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${testProgress}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Results */}
            {step === 4 && testResults && (
              <div>
                <div className="text-center mb-6">
                  <CheckCircle className="mx-auto mb-3 text-green-600" size={48} />
                  <h2 className="text-xl font-semibold text-gray-900 mb-1">Testing Complete</h2>
                  <p className="text-gray-600 text-sm">AI analysis finished successfully</p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  {[
                    { label: 'Tests', value: testResults.total_tests },
                    { label: 'Passed', value: testResults.passed, color: 'text-green-600' },
                    { label: 'Failed', value: testResults.failed, color: 'text-red-600' },
                    { label: 'Screens', value: testResults.screens_explored },
                  ].map((stat) => (
                    <div key={stat.label} className="p-4 bg-gray-50 rounded-lg text-center border border-gray-200">
                      <p className={`text-lg font-semibold ${stat.color || 'text-gray-900'}`}>
                        {stat.value}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">{stat.label}</p>
                    </div>
                  ))}
                </div>

                {testResults.ai_insights && (
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-1.5">
                      <Brain size={16} className="text-indigo-600" /> AI Insights
                    </h3>
                    <p className="text-sm text-gray-700 whitespace-pre-line">
                      {testResults.ai_insights.length > 400
                        ? testResults.ai_insights.substring(0, 400) + '…'
                        : testResults.ai_insights}
                    </p>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    type="button"
                    onClick={resetTest}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md text-sm font-medium hover:bg-gray-200 flex items-center justify-center gap-1.5"
                  >
                    <RefreshCw size={16} /> Test Another APK
                  </button>
                  <button
                    type="button"
                    onClick={viewReport}
                    className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-black flex-1"
                  >
                    View Full Report
                  </button>
                  <button
                    type="button"
                    onClick={downloadReport}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 flex items-center justify-center gap-1.5"
                  >
                    <Download size={16} /> Download Report
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>

        <footer className="mt-10 text-center text-gray-500 text-xs">
          <p>Powered by Google Gemini • Python • Appium • ADB</p>
        </footer>
      </div>
    </div>
  );
};

export default MobileTestingUI;