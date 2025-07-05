import React, { useState, useEffect } from 'react';
import { Settings, User, Lock, Save, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const SettingsPage = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [saved, setSaved] = useState(false);
  const [llmProviders, setLlmProviders] = useState({ gemini: false, openai: false });
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [loadingSettings, setLoadingSettings] = useState(true);
  const [profile, setProfile] = useState({ name: '', email: '', skills: '', target_roles: '' });
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileMessage, setProfileMessage] = useState('');
  const [profileMessageType, setProfileMessageType] = useState('');

  useEffect(() => {
    checkServerStatus();
    loadCredentials();
    fetchAllSettings();
    fetchUserProfile();
  }, []);

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

  const fetchAllSettings = async () => {
    setLoadingSettings(true);
    try {
      const [geminiRes, openaiRes, providerRes] = await Promise.all([
        axios.get('/api/settings/GEMINI_API_KEY').catch(() => ({ data: { value: '' } })),
        axios.get('/api/settings/OPENAI_API_KEY').catch(() => ({ data: { value: '' } })),
        axios.get('/api/settings/LLM_PROVIDER').catch(() => ({ data: { value: 'gemini' } })),
      ]);
      setGeminiKey(geminiRes.data.value || '');
      setOpenaiKey(openaiRes.data.value || '');
      setSelectedProvider(providerRes.data.value || 'gemini');
      await fetchLlmProviders();
    } catch (error) {
      // ignore
    } finally {
      setLoadingSettings(false);
    }
  };

  const fetchLlmProviders = async () => {
    try {
      const response = await axios.get('/api/llm_providers');
      setLlmProviders(response.data);
    } catch (error) {
      // ignore
    }
  };

  const fetchUserProfile = async () => {
    setProfileLoading(true);
    try {
      const response = await axios.get('/api/user/profile');
      setProfile({
        name: response.data.name || '',
        email: response.data.email || '',
        skills: (response.data.skills || []).join(', '),
        target_roles: (response.data.target_roles || []).join(', ')
      });
    } catch (error) {
      // ignore
    } finally {
      setProfileLoading(false);
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

  const handleSaveGemini = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      await axios.post('/api/settings/GEMINI_API_KEY', { value: geminiKey, setting_type: 'string' });
      setSaved(true);
      setMessage('Gemini API key saved!');
      setMessageType('success');
      await fetchLlmProviders();
    } catch (error) {
      setMessage('Failed to save Gemini API key');
      setMessageType('error');
    } finally {
      setLoading(false);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  const handleSaveOpenai = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      await axios.post('/api/settings/OPENAI_API_KEY', { value: openaiKey, setting_type: 'string' });
      setSaved(true);
      setMessage('OpenAI API key saved!');
      setMessageType('success');
      await fetchLlmProviders();
    } catch (error) {
      setMessage('Failed to save OpenAI API key');
      setMessageType('error');
    } finally {
      setLoading(false);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  const handleProviderChange = async (e) => {
    const value = e.target.value;
    setSelectedProvider(value);
    setLoading(true);
    setMessage('');
    try {
      await axios.post('/api/settings/LLM_PROVIDER', { value, setting_type: 'string' });
      setMessage('Preferred provider updated!');
      setMessageType('success');
      await fetchLlmProviders();
    } catch (error) {
      setMessage('Failed to update provider');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setProfileLoading(true);
    setProfileMessage('');
    try {
      await axios.post('/api/user/profile', {
        name: profile.name,
        email: profile.email,
        skills: profile.skills.split(',').map(s => s.trim()).filter(Boolean),
        target_roles: profile.target_roles.split(',').map(r => r.trim()).filter(Boolean)
      });
      setProfileMessage('Profile saved!');
      setProfileMessageType('success');
    } catch (error) {
      setProfileMessage('Failed to save profile');
      setProfileMessageType('error');
    } finally {
      setProfileLoading(false);
      setTimeout(() => setProfileMessage(''), 2000);
    }
  };

  if (loadingSettings) {
    return <div className="p-6">Loading settings...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Settings</h1>
        <p className="text-gray-600">Configure your application settings</p>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <User className="w-5 h-5 mr-2" />
          AI Provider
        </h2>
        <div className="mb-4">
          <div className="flex items-center space-x-4">
            <span className={`font-semibold ${llmProviders.gemini ? 'text-green-600' : 'text-gray-400'}`}>Gemini {llmProviders.gemini ? '(Available)' : '(Not Set)'}</span>
            <span className={`font-semibold ${llmProviders.openai ? 'text-green-600' : 'text-gray-400'}`}>OpenAI {llmProviders.openai ? '(Available)' : '(Not Set)'}</span>
          </div>
        </div>
        {(llmProviders.gemini && llmProviders.openai) && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Provider</label>
            <select value={selectedProvider} onChange={handleProviderChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="gemini">Gemini (Recommended)</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>
        )}
        {(!llmProviders.gemini && !llmProviders.openai) && (
          <div className="text-red-600">No AI provider is configured. Please set up a Gemini or OpenAI API key.</div>
        )}
        {/* Gemini API Key Input */}
        <div className="mt-6 mb-4 border-t pt-6">
          <form onSubmit={handleSaveGemini} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Gemini API Key</label>
            <input
              type="password"
              value={geminiKey}
              onChange={e => setGeminiKey(e.target.value)}
              placeholder="Paste your Gemini API key here"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" disabled={loading}>Save Gemini Key</button>
            {saved && messageType === 'success' && <div className="text-green-600 font-medium mt-1">{message}</div>}
            {messageType === 'error' && <div className="text-red-600 font-medium mt-1">{message}</div>}
          </form>
        </div>
        {/* OpenAI API Key Input */}
        <div className="mb-4">
          <form onSubmit={handleSaveOpenai} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">OpenAI API Key</label>
            <input
              type="password"
              value={openaiKey}
              onChange={e => setOpenaiKey(e.target.value)}
              placeholder="Paste your OpenAI API key here"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" disabled={loading}>Save OpenAI Key</button>
            {saved && messageType === 'success' && <div className="text-green-600 font-medium mt-1">{message}</div>}
            {messageType === 'error' && <div className="text-red-600 font-medium mt-1">{message}</div>}
          </form>
        </div>
      </div>
      {/* User Profile Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <User className="w-5 h-5 mr-2" />
          User Profile
        </h2>
        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              name="name"
              value={profile.name}
              onChange={handleProfileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={profileLoading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={profile.email}
              onChange={handleProfileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={profileLoading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma separated)</label>
            <input
              type="text"
              name="skills"
              value={profile.skills}
              onChange={handleProfileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={profileLoading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Roles (comma separated)</label>
            <input
              type="text"
              name="target_roles"
              value={profile.target_roles}
              onChange={handleProfileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={profileLoading}
            />
          </div>
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" disabled={profileLoading}>Save Profile</button>
          {profileMessage && (
            <div className={profileMessageType === 'success' ? 'text-green-600 font-medium mt-1' : 'text-red-600 font-medium mt-1'}>{profileMessage}</div>
          )}
        </form>
      </div>
    </div>
  );
};

export default SettingsPage; 