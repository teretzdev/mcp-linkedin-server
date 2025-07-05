import React, { useState, useEffect } from 'react';
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
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    const savedUser = localStorage.getItem('currentUser');
    return !!savedUser;
  });
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [loading, setLoading] = useState(true);
  const [apiPort, setApiPort] = useState(8001);
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem('currentUser');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [showGeminiModal, setShowGeminiModal] = useState(false);
  const [geminiKey, setGeminiKey] = useState(localStorage.getItem('gemini_api_key') || '');
  const [pendingGeminiKey, setPendingGeminiKey] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(() => !localStorage.getItem('onboarded_v1'));

  useEffect(() => {
    detectApiPort();
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
            name: 'John Doe',
            email: 'john.doe@email.com',
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
    localStorage.setItem('currentUser', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
  };

  // Handler to open Gemini modal from child components
  const openGeminiModal = () => setShowGeminiModal(true);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 to-linkedin-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-linkedin-600 animate-spin mx-auto mb-4" />
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
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 to-linkedin-100">
        <div className="flex">
          <Sidebar 
            isLoggedIn={isLoggedIn} 
            serverStatus={serverStatus} 
            onLogin={() => setIsLoggedIn(true)}
            onLogout={() => setIsLoggedIn(false)}
            currentUser={currentUser}
          />
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard isLoggedIn={isLoggedIn} serverStatus={serverStatus} />} />
              <Route path="/job-search" element={<JobSearch />} />
              <Route path="/applications" element={<Applications />} />
              <Route path="/saved-jobs" element={<SavedJobs />} />
              <Route path="/automation" element={<AutomationDashboard />} />
              <Route path="/ai-automation" element={<AIAutomationDashboard />} />
              <Route path="/settings" element={<SettingsPage onGeminiKeyChange={setGeminiKey} geminiKey={geminiKey} />} />
              <Route path="/resume-manager" element={<ResumeManager onRequestGeminiKey={openGeminiModal} />} />
              <Route path="/easy-apply" element={<EasyApplyAssistant onRequestGeminiKey={openGeminiModal} />} />
              <Route path="/applicant-knowledge" element={<ApplicantKnowledgeBase />} />
              <Route path="/follow-ups" element={<ApplicationFollowUps />} />
              <Route path="/analytics" element={<ApplicationAnalytics />} />
            </Routes>
          </main>
        </div>
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
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-blue-800 text-sm">
                <b>Tip:</b> The AI will proactively guide you and offer help as you use the app. Look for the <span role="img" aria-label="robot">🤖</span> icon!
              </div>
              <button onClick={handleOnboardingClose} className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-semibold">Get Started</button>
            </div>
          </div>
        )}
        {/* Gemini API Key Modal */}
        {showGeminiModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Enter Gemini API Key</h2>
              <p className="mb-4 text-gray-600">To enable AI-powered features, please enter your <span className='font-semibold'>Google Gemini API key</span>. You can get one from <a href='https://aistudio.google.com/app/apikey' target='_blank' rel='noopener noreferrer' className='text-blue-600 underline'>Google AI Studio</a>.</p>
              <form onSubmit={handleGeminiKeySubmit}>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
                  placeholder="Paste your Gemini API key here..."
                  value={pendingGeminiKey}
                  onChange={e => setPendingGeminiKey(e.target.value)}
                  autoFocus
                />
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-semibold"
                >
                  Save API Key
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App; 