import React, { useState, useEffect } from 'react';
import { Settings, User, Lock, Save, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const SettingsPage = ({ geminiKey, onGeminiKeyChange }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [localGeminiKey, setLocalGeminiKey] = useState(geminiKey || '');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    checkServerStatus();
    loadCredentials();
    setLocalGeminiKey(geminiKey || '');
  }, [geminiKey]);

  const checkServerStatus = async () => {
    try {
      await axios.get('/api/health');
      setServerStatus('connected');
    } catch (error) {
      setServerStatus('disconnected');
    }
  };

  const loadCredentials = async () => {
    try {
      const response = await axios.get('/api/get_credentials');
      if (response.data.username) {
        setCredentials({
          username: response.data.username,
          password: '••••••••' // Masked password
        });
      }
    } catch (error) {
      console.log('Could not load credentials:', error.message);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveCredentials = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post('/api/update_credentials', {
        username: credentials.username,
        password: credentials.password
      });
      
      setMessage('Credentials saved successfully!');
      setMessageType('success');
      
      // Mask the password after saving
      setCredentials(prev => ({
        ...prev,
        password: '••••••••'
      }));
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to save credentials');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleTestLogin = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post('/api/test_login');
      setMessage('Login test successful!');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Login test failed');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleGeminiKeyInput = (e) => {
    setLocalGeminiKey(e.target.value);
  };

  const handleSave = (e) => {
    e.preventDefault();
    localStorage.setItem('gemini_api_key', localGeminiKey);
    if (onGeminiKeyChange) onGeminiKeyChange(localGeminiKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">
          Manage your LinkedIn credentials and system settings
        </p>
      </div>

      {/* LinkedIn Credentials */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <User className="w-5 h-5 mr-2" />
          LinkedIn Credentials
        </h2>
        
        <form onSubmit={handleSaveCredentials} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Email/Username
            </label>
            <input
              type="email"
              name="username"
              value={credentials.username}
              onChange={handleInputChange}
              placeholder="your.email@example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={credentials.password}
                onChange={handleInputChange}
                placeholder="Enter your password"
                className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Your password is encrypted and stored locally
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading || !credentials.username || !credentials.password}
              className="flex items-center space-x-2 px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>{loading ? 'Saving...' : 'Save Credentials'}</span>
            </button>

            <button
              type="button"
              onClick={handleTestLogin}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Test Login</span>
            </button>
          </div>
        </form>

        {message && (
          <div className={`mt-4 p-3 rounded-lg ${
            messageType === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            <div className="flex items-center space-x-2">
              {messageType === 'success' ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <AlertCircle className="w-4 h-4" />
              )}
              <span>{message}</span>
            </div>
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          System Status
        </h2>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">API Bridge Status</span>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                serverStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className={`text-sm font-medium ${
                serverStatus === 'connected' ? 'text-green-600' : 'text-red-600'
              }`}>
                {serverStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">LinkedIn Login</span>
            <span className="text-sm text-gray-500">
              {credentials.username ? 'Configured' : 'Not configured'}
            </span>
          </div>
        </div>
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Security Information</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Your credentials are encrypted and stored locally</li>
          <li>• No data is sent to external servers</li>
          <li>• Sessions are automatically managed and secured</li>
          <li>• Keep your credentials safe and don't share them</li>
        </ul>
      </div>

      {/* Gemini API Key */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Gemini API Key
        </h2>
        
        <form onSubmit={handleSave} className="space-y-4">
          <input
            type="text"
            value={localGeminiKey}
            onChange={handleGeminiKeyInput}
            placeholder="Paste your Gemini API key here..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
          <button
            type="submit"
            className="flex items-center space-x-2 px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save Gemini Key</span>
          </button>
          {saved && <span className="text-green-600 text-sm">Gemini key saved!</span>}
        </form>
      </div>

      {/* AI Features Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <User className="w-5 h-5 mr-2" />
          AI Features Status
        </h2>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Gemini API Key</span>
            <span className="text-sm text-gray-500">
              {localGeminiKey ? <span className="text-green-600">Set</span> : <span className="text-red-600">Not Set</span>}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Resume Optimization</span>
            <span className="text-sm text-gray-500">
              <span className="text-green-600">Enabled</span>
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Easy Apply Assistant</span>
            <span className="text-sm text-gray-500">
              <span className="text-green-600">Enabled</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 