import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [loading, setLoading] = useState(true);
  const [apiPort, setApiPort] = useState(8001);

  useEffect(() => {
    detectApiPort();
  }, []);

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

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 to-linkedin-100">
        <div className="flex">
          <Sidebar 
            isLoggedIn={isLoggedIn} 
            serverStatus={serverStatus} 
            onLogin={() => setIsLoggedIn(true)}
            onLogout={() => setIsLoggedIn(false)}
          />
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard isLoggedIn={isLoggedIn} serverStatus={serverStatus} />} />
              <Route path="/jobs" element={<JobSearch />} />
              <Route path="/applications" element={<Applications />} />
              <Route path="/saved" element={<SavedJobs />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App; 