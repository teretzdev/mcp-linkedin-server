import React, { useState, useEffect } from 'react';
import { Settings, Key, User, Save } from 'lucide-react';
import axios from 'axios';

function SettingsPage() {
  const [settings, setSettings] = useState({
    preferredProvider: 'gemini',
    geminiApiKey: '',
    openaiApiKey: '',
    name: '',
    email: '',
    skills: '',
    targetRoles: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Load settings from localStorage or API
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = async () => {
    setIsLoading(true);
    setMessage('');

    try {
      // Save to localStorage
      localStorage.setItem('userSettings', JSON.stringify(settings));
      
      // Optionally save to backend
      await axios.post('/api/save_settings', settings);
      
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Failed to save settings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="container container-lg">
      <div className="p-xl">
        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-primary">Settings</h1>
            <p className="text-secondary">Configure your application settings</p>
          </div>
          
          <div className="card-body">
            {/* API Configuration */}
            <div className="card mb-lg">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-primary flex items-center gap-sm">
                  <Key className="w-5 h-5" />
                  API Configuration
                </h2>
              </div>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">Preferred Provider</label>
                  <select
                    value={settings.preferredProvider}
                    onChange={(e) => handleChange('preferredProvider', e.target.value)}
                    className="form-input"
                  >
                    <option value="gemini">Google Gemini</option>
                    <option value="openai">OpenAI</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Gemini API Key</label>
                  <input
                    type="password"
                    value={settings.geminiApiKey}
                    onChange={(e) => handleChange('geminiApiKey', e.target.value)}
                    className="form-input"
                    placeholder="Enter your Gemini API key"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">OpenAI API Key</label>
                  <input
                    type="password"
                    value={settings.openaiApiKey}
                    onChange={(e) => handleChange('openaiApiKey', e.target.value)}
                    className="form-input"
                    placeholder="Enter your OpenAI API key"
                  />
                </div>
              </div>
            </div>

            {/* Profile Settings */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-primary flex items-center gap-sm">
                  <User className="w-5 h-5" />
                  Profile Settings
                </h2>
              </div>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">Name</label>
                  <input
                    type="text"
                    value={settings.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    className="form-input"
                    placeholder="Enter your full name"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    value={settings.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    className="form-input"
                    placeholder="Enter your email"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Skills (comma separated)</label>
                  <input
                    type="text"
                    value={settings.skills}
                    onChange={(e) => handleChange('skills', e.target.value)}
                    className="form-input"
                    placeholder="e.g., React, JavaScript, Python"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Target Roles (comma separated)</label>
                  <input
                    type="text"
                    value={settings.targetRoles}
                    onChange={(e) => handleChange('targetRoles', e.target.value)}
                    className="form-input"
                    placeholder="e.g., Frontend Developer, Software Engineer"
                  />
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end mt-lg">
              <button
                onClick={handleSave}
                disabled={isLoading}
                className="btn btn-primary flex items-center gap-sm"
              >
                <Save className="w-4 h-4" />
                {isLoading ? 'Saving...' : 'Save Settings'}
              </button>
            </div>

            {message && (
              <div className={`mt-md text-center text-sm ${
                message.includes('successfully') ? 'text-success' : 'text-error'
              }`}>
                {message}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage; 