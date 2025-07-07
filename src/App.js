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
  Loader2,
  Moon,
  Sun,
  Briefcase,
  FileText,
  TrendingUp
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
  const [apiPort, setApiPort] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [showGeminiModal, setShowGeminiModal] = useState(false);
  const [geminiKey, setGeminiKey] = useState(localStorage.getItem('gemini_api_key') || '');
  const [pendingGeminiKey, setPendingGeminiKey] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(() => !localStorage.getItem('onboarded_v1'));
  const [sessionId, setSessionId] = useState(null);
  const [sessionStats, setSessionStats] = useState({ jobs_viewed: 0, jobs_applied: 0, jobs_saved: 0, errors: 0 });
  const [darkMode, setDarkMode] = useState(false);
  const sessionActive = useRef(false);

  useEffect(() => {
    // Load dark mode preference
    const stored = localStorage.getItem('appDarkMode');
    if (stored === 'true') {
      setDarkMode(true);
      document.body.classList.add('dark-mode');
    } else {
      setDarkMode(false);
      document.body.classList.remove('dark-mode');
    }
    
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
    if (darkMode) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('appDarkMode', 'true');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('appDarkMode', 'false');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode((d) => !d);

  useEffect(() => {
    // Show Gemini modal if key is missing
    if (!geminiKey) {
      setShowGeminiModal(true);
    }
  }, [geminiKey]);

  const detectApiPort = async () => {
    // Try port 8002 first, then 8001-8010
    const ports = [8002, ...Array.from({length: 10}, (_, i) => 8001 + i).filter(p => p !== 8002)];
    let found = false;
    for (let port of ports) {
      console.log(`[API DETECT] Trying http://localhost:${port}/api/health`);
      try {
        const response = await axios.get(`http://localhost:${port}/api/health`, { timeout: 1000 });
        if (response.status === 200) {
          setApiPort(port);
          axios.defaults.baseURL = `http://localhost:${port}`;
          console.log(`[API DETECT] API Bridge found on port ${port}`);
          found = true;
          break;
        }
      } catch (error) {
        // Log error for each port
        console.log(`[API DETECT] No API on port ${port}: ${error.message}`);
        continue;
      }
    }
    if (!found) {
      setServerStatus('disconnected');
      setLoading(false);
      setApiPort(null);
      console.error('[API DETECT] No API Bridge found on ports 8001-8010.');
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
      <div className="app">
        <div className="main-content flex items-center justify-center min-h-screen">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-md" />
            <h2 className="text-xl font-semibold text-primary">Connecting to LinkedIn Job Hunter...</h2>
            <p className="text-sm text-secondary mt-sm">Detecting API Bridge on ports 8001-8010</p>
            {apiPort === null && !loading && (
              <div className="text-red-500 mt-md">
                <b>Could not connect to backend API on any port (8001-8010).</b><br />
                Please ensure the backend is running and refresh this page.
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} serverStatus={serverStatus} />;
  }

  return (
    <Router>
      <div className="app">
        {/* Navigation Header */}
        <nav className="nav">
          <div className="flex items-center gap-lg">
            <a href="/dashboard" className="nav-brand">
              <Linkedin className="w-8 h-8 mr-sm" />
              LinkedIn Job Hunter
            </a>
            <div className={`status status-${serverStatus}`}>
              <div className="status-indicator"></div>
              <span className="text-sm">
                {serverStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <div className="nav-actions">
            <button 
              onClick={toggleDarkMode} 
              className="btn btn-secondary"
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            {currentUser && (
              <div className="flex items-center gap-sm">
                <span className="text-sm">{currentUser.name}</span>
                <button onClick={handleLogout} className="btn btn-secondary">
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </nav>

        {/* Main Content Area */}
        <div className="app-content">
          {/* Sidebar */}
          <aside className="sidebar">
            <a href="/dashboard" className="sidebar-item">
              <Activity className="sidebar-icon" />
              Dashboard
            </a>
            <a href="/job-search" className="sidebar-item">
              <Search className="sidebar-icon" />
              Job Search
            </a>
            <a href="/applications" className="sidebar-item">
              <Briefcase className="sidebar-icon" />
              Applications
            </a>
            <a href="/saved-jobs" className="sidebar-item">
              <FileText className="sidebar-icon" />
              Saved Jobs
            </a>
            <a href="/easy-apply" className="sidebar-item">
              <CheckCircle className="sidebar-icon" />
              Easy Apply
            </a>
            <a href="/ai-automation" className="sidebar-item">
              <TrendingUp className="sidebar-icon" />
              AI Automation
            </a>
            <a href="/applicant-knowledge" className="sidebar-item">
              <FileText className="sidebar-icon" />
              Knowledge Base
            </a>
            <a href="/analytics" className="sidebar-item">
              <TrendingUp className="sidebar-icon" />
              Analytics
            </a>
            <a href="/follow-ups" className="sidebar-item">
              <MessageCircle className="sidebar-icon" />
              Follow-ups
            </a>
            <a href="/feed-browser" className="sidebar-item">
              <Activity className="sidebar-icon" />
              Feed Browser
            </a>
            <a href="/post-interaction" className="sidebar-item">
              <MessageCircle className="sidebar-icon" />
              Post Interaction
            </a>
            <a href="/profile-search" className="sidebar-item">
              <User className="sidebar-icon" />
              Profile Search
            </a>
            <a href="/resume-manager" className="sidebar-item">
              <FileText className="sidebar-icon" />
              Resume Manager
            </a>
            <a href="/settings" className="sidebar-item">
              <Settings className="sidebar-icon" />
              Settings
            </a>
          </aside>

          {/* Main Content */}
          <main className="main-content">
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
          <div className="fixed inset-0 z-modal-backdrop flex items-center justify-center bg-black bg-opacity-40">
            <div className="card max-w-md w-full">
              <div className="flex items-center mb-md">
                <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png" alt="AI" className="w-12 h-12 mr-md" />
                <div>
                  <h2 className="text-2xl font-bold mb-xs">AI Assistant Setup</h2>
                  <p className="text-secondary">Enter your Gemini API key to enable AI features</p>
                </div>
              </div>
              <form onSubmit={handleGeminiKeySubmit} className="space-y-md">
                <div>
                  <label htmlFor="gemini-key" className="form-label">
                    Gemini API Key
                  </label>
                  <input
                    type="password"
                    id="gemini-key"
                    value={pendingGeminiKey}
                    onChange={(e) => setPendingGeminiKey(e.target.value)}
                    className="form-input"
                    placeholder="Enter your Gemini API key"
                    required
                  />
                </div>
                <div className="flex justify-end gap-sm">
                  <button
                    type="submit"
                    className="btn btn-primary"
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
          <div className="fixed inset-0 z-modal-backdrop flex items-center justify-center bg-black bg-opacity-40">
            <div className="card max-w-lg w-full relative">
              <button onClick={handleOnboardingClose} className="absolute top-sm right-sm text-tertiary hover:text-primary text-2xl">×</button>
              <div className="flex items-center mb-md">
                <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png" alt="AI" className="w-12 h-12 mr-md" />
                <div>
                  <h2 className="text-2xl font-bold mb-xs">Welcome to LinkedIn Job Hunter!</h2>
                  <p className="text-secondary">Your AI assistant will guide you through every step of your job search journey.</p>
                </div>
              </div>
              <ol className="list-decimal pl-lg space-y-sm mb-md">
                <li>Set up your <span className="font-semibold">Gemini API key</span> for AI-powered features (you'll be prompted if it's missing).</li>
                <li>Use the <span className="font-semibold">Resume Manager</span> to upload and optimize your resume with AI.</li>
                <li>Let the <span className="font-semibold">Easy Apply Assistant</span> help you answer job application questions.</li>
                <li>Manage your <span className="font-semibold">Knowledge Base</span> for personalized job matching.</li>
                <li>Check <span className="font-semibold">Settings</span> to update your Gemini key or preferences at any time.</li>
              </ol>
              <button
                onClick={handleOnboardingClose}
                className="btn btn-primary w-full"
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
