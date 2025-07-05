import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { 
  Linkedin, 
  Home, 
  Search, 
  User, 
  MessageCircle, 
  Settings,
  Activity,
  LogIn,
  LogOut,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import axios from 'axios';
import './index.css';

// Components
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import ProfileSearch from './components/ProfileSearch';
import FeedBrowser from './components/FeedBrowser';
import PostInteraction from './components/PostInteraction';
import SettingsPage from './components/SettingsPage';
import JobSearch from './components/JobSearch';
import Applications from './components/Applications';
import SavedJobs from './components/SavedJobs';
import AutomationDashboard from './components/AutomationDashboard';
import ResumeManager from './components/ResumeManager';
import EasyApplyAssistant from './components/EasyApplyAssistant';
import ApplicantKnowledgeBase from './components/ApplicantKnowledgeBase';
import ApplicationFollowUps from './components/ApplicationFollowUps';
import ApplicationAnalytics from './components/ApplicationAnalytics';
import AIAutomationDashboard from './components/AIAutomationDashboard';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [loading, setLoading] = useState(true);
  const [apiPort, setApiPort] = useState(8001);
  const [currentUser, setCurrentUser] = useState(null);
  const [showGeminiModal, setShowGeminiModal] = useState(false);
  const [geminiKey, setGeminiKey] = useState(localStorage.getItem('gemini_api_key') || '');
  const [pendingGeminiKey, setPendingGeminiKey] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(() => !localStorage.getItem('onboarded_v1'));
  const [sessionId, setSessionId] = useState(null);
  const [sessionStats, setSessionStats] = useState({ jobs_viewed: 0, jobs_applied: 0, jobs_saved: 0, errors: 0 });
  const sessionActive = useRef(false);

  useEffect(() => {
    detectApiPort();
    // Start or resume session on app load
    startOrResumeSession();
    // End session on unload
    window.addEventListener('beforeunload', handleSessionEnd);
    return () => {
      window.removeEventListener('beforeunload', handleSessionEnd);
      handleSessionEnd();
    };
  }, []);

  useEffect(() => {
    // Show Gemini modal if key is missing
    if (!geminiKey) {
      setShowGeminiModal(true);
    }
  }, [geminiKey]);

  const detectApiPort = async () => {
    // Try ports 8001-8010 to find the API bridge
    for (let port = 8001; port <= 8010; port++) {
      try {
        const response = await axios.get(`http://localhost:${port}/api/health`, { timeout: 1000 });
        if (response.status === 200) {
          setApiPort(port);
          // Update axios default base URL
          axios.defaults.baseURL = `http://localhost:${port}`;
          console.log(`API Bridge found on port ${port}`);
          break;
        }
      } catch (error) {
        continue;
      }
    }
    
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 5000);
    return () => clearInterval(interval);
  };

  const checkServerStatus = async () => {
    try {
      const response = await axios.get('/api/health');
      setServerStatus('connected');
      
      // Check if credentials are configured
      try {
        const credentialsResponse = await axios.get('/api/get_credentials');
        if (credentialsResponse.data.configured) {
          setIsLoggedIn(true);
          setCurrentUser({
            name: credentialsResponse.data.name || credentialsResponse.data.username || 'User',
            email: credentialsResponse.data.username || 'user@example.com',
            avatar: 'https://via.placeholder.com/40'
          });
        }
      } catch (error) {
        console.log('Could not check credentials:', error.message);
      }
      
      setLoading(false);
    } catch (error) {
      setServerStatus('disconnected');
      setLoading(false);
    }
  };

  const handleGeminiKeySubmit = (e) => {
    e.preventDefault();
    if (pendingGeminiKey.trim()) {
      localStorage.setItem('gemini_api_key', pendingGeminiKey.trim());
      setGeminiKey(pendingGeminiKey.trim());
      setShowGeminiModal(false);
    }
  };

  const handleOnboardingClose = () => {
    setShowOnboarding(false);
    localStorage.setItem('onboarded_v1', 'true');
  };

  const handleLogin = (userData) => {
    setIsLoggedIn(true);
    setCurrentUser(userData);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
    handleSessionEnd();
  };

  // Handler to open Gemini modal from child components
  const openGeminiModal = () => setShowGeminiModal(true);

  const startOrResumeSession = async () => {
    try {
      // Try to resume from localStorage, else start new
      let sid = localStorage.getItem('session_id');
      if (!sid) {
        sid = `session_${Date.now()}`;
        localStorage.setItem('session_id', sid);
      }
      setSessionId(sid);
      // Start or update session in backend
      await axios.post('/api/session/start', { session_id: sid, automation_mode: 'manual' });
      sessionActive.current = true;
    } catch (error) {
      // ignore for now
    }
  };

  const updateSessionStats = async (updates) => {
    if (!sessionId) return;
    const newStats = { ...sessionStats, ...updates };
    setSessionStats(newStats);
    try {
      await axios.post('/api/session/update', { ...newStats }, { params: { session_id: sessionId } });
    } catch (error) {
      // ignore for now
    }
  };

  const handleSessionEnd = async () => {
    if (!sessionId || !sessionActive.current) return;
    sessionActive.current = false;
    try {
      await axios.post('/api/session/end', null, { params: { session_id: sessionId } });
      localStorage.removeItem('session_id');
    } catch (error) {
      // ignore for now
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Connecting to LinkedIn Job Hunter...</h2>
          <p className="text-sm text-gray-500 mt-2">Detecting API Bridge on ports 8001-8010</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
        <div className="flex">
          <Sidebar 
            isLoggedIn={isLoggedIn} 
            serverStatus={serverStatus} 
            onLogin={() => setIsLoggedIn(true)}
            onLogout={handleLogout}
            currentUser={currentUser}
          />
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard isLoggedIn={isLoggedIn} serverStatus={serverStatus} sessionStats={sessionStats} />} />
              <Route path="/job-search" element={<JobSearch updateSessionStats={updateSessionStats} sessionStats={sessionStats} />} />
              <Route path="/applications" element={<Applications updateSessionStats={updateSessionStats} sessionStats={sessionStats} />} />
              <Route path="/saved-jobs" element={<SavedJobs updateSessionStats={updateSessionStats} sessionStats={sessionStats} />} />
              <Route path="/automation" element={<AutomationDashboard updateSessionStats={updateSessionStats} sessionStats={sessionStats} />} />
              <Route path="/ai-automation" element={<AIAutomationDashboard updateSessionStats={updateSessionStats} sessionStats={sessionStats} />} />
              <Route path="/settings" element={<SettingsPage onGeminiKeyChange={setGeminiKey} geminiKey={geminiKey} />} />
              <Route path="/resume-manager" element={<ResumeManager onRequestGeminiKey={openGeminiModal} />} />
              <Route path="/easy-apply" element={<EasyApplyAssistant onRequestGeminiKey={openGeminiModal} updateSessionStats={updateSessionStats} sessionStats={sessionStats} />} />
              <Route path="/applicant-knowledge" element={<ApplicantKnowledgeBase />} />
              <Route path="/follow-ups" element={<ApplicationFollowUps />} />
              <Route path="/analytics" element={<ApplicationAnalytics sessionStats={sessionStats} />} />
            </Routes>
          </main>
        </div>
        
        {/* Gemini API Key Modal */}
        {showGeminiModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
              <div className="flex items-center mb-4">
                <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png" alt="AI" className="w-12 h-12 mr-4" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-1">AI Assistant Setup</h2>
                  <p className="text-gray-600">Enter your Gemini API key to enable AI features</p>
                </div>
              </div>
              <form onSubmit={handleGeminiKeySubmit} className="space-y-4">
                <div>
                  <label htmlFor="gemini-key" className="block text-sm font-medium text-gray-700 mb-2">
                    Gemini API Key
                  </label>
                  <input
                    type="password"
                    id="gemini-key"
                    value={pendingGeminiKey}
                    onChange={(e) => setPendingGeminiKey(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your Gemini API key"
                    required
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Save Key
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Onboarding Modal */}
        {showOnboarding && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-lg w-full relative">
              <button onClick={handleOnboardingClose} className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-2xl">×</button>
              <div className="flex items-center mb-4">
                <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png" alt="AI" className="w-12 h-12 mr-4" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-1">Welcome to LinkedIn Job Hunter!</h2>
                  <p className="text-gray-600">Your AI assistant will guide you through every step of your job search journey.</p>
                </div>
              </div>
              <ol className="list-decimal pl-6 text-gray-700 space-y-2 mb-4">
                <li>Set up your <span className="font-semibold">Gemini API key</span> for AI-powered features (you'll be prompted if it's missing).</li>
                <li>Use the <span className="font-semibold">Resume Manager</span> to upload and optimize your resume with AI.</li>
                <li>Let the <span className="font-semibold">Easy Apply Assistant</span> help you answer job application questions.</li>
                <li>Manage your <span className="font-semibold">Knowledge Base</span> for personalized job matching.</li>
                <li>Check <span className="font-semibold">Settings</span> to update your Gemini key or preferences at any time.</li>
              </ol>
              <button
                onClick={handleOnboardingClose}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Get Started
              </button>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
