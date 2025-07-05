import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Edit3, Download, MessageCircle, Plus, Trash2, Sparkles } from 'lucide-react';
import axios from 'axios';

const ResumeManager = ({ onRequestGeminiKey }) => {
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [targetJob, setTargetJob] = useState('');
  const [targetCompany, setTargetCompany] = useState('');
  const fileInputRef = useRef();
  const geminiKey = localStorage.getItem('gemini_api_key') || '';
  const [profile, setProfile] = useState(null);
  const [missingFields, setMissingFields] = useState([]);
  const [missingFieldValues, setMissingFieldValues] = useState({});
  const [savingMissing, setSavingMissing] = useState(false);

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('/api/user/profile');
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        // Pre-fill targetJob and targetCompany if not set
        if (!targetJob && data.target_roles && data.target_roles.length > 0) {
          setTargetJob(Array.isArray(data.target_roles) ? data.target_roles[0] : data.target_roles);
        }
        if (!targetCompany && data.skills && data.skills.length > 0) {
          setTargetCompany(Array.isArray(data.skills) ? data.skills[0] : data.skills);
        }
      }
    } catch (e) {
      setProfile(null);
    }
  };

  // Detect missing required fields for resume optimization/chat
  useEffect(() => {
    // Example: require skills and target_roles for optimization
    const requiredFields = ['skills', 'target_roles'];
    const missing = requiredFields.filter(field => !profile || !profile[field] || profile[field].length === 0);
    setMissingFields(missing);
  }, [profile]);

  const handleMissingFieldChange = (field, value) => {
    setMissingFieldValues(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveMissingFields = async (e) => {
    e.preventDefault();
    setSavingMissing(true);
    try {
      // Update profile in backend
      const updatedProfile = { ...profile, ...missingFieldValues };
      await fetch('/api/user/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedProfile)
      });
      setProfile(updatedProfile);
      setMissingFields([]);
      setMissingFieldValues({});
      // Auto-continue: re-trigger optimization/chat if needed
      if (isOptimizing && selectedResume) {
        optimizeResume();
      }
      if (isChatting && selectedResume) {
        sendChatMessage();
      }
    } catch (e) {
      // Optionally show error
    } finally {
      setSavingMissing(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Content = e.target.result.split(',')[1]; // Remove data URL prefix
        
        const response = await axios.post('/api/resume/upload', {
          filename: file.name,
          content: base64Content
        });

        if (response.data.success) {
          const newResume = {
            id: response.data.resume_id,
            name: response.data.filename,
            size: file.size,
            type: file.type,
            uploadDate: response.data.upload_date,
            content: response.data.content,
            wordCount: response.data.word_count,
            optimized: false
          };

          setResumes([...resumes, newResume]);
          setSelectedResume(newResume);
        }
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Upload failed:', error);
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const optimizeResume = async () => {
    if (!selectedResume) return;
    if (!geminiKey) {
      if (onRequestGeminiKey) onRequestGeminiKey();
      return;
    }
    
    setIsOptimizing(true);
    try {
      const response = await axios.post('/api/resume/optimize', {
        resume_id: selectedResume.id,
        resume_content: selectedResume.content,
        target_job: targetJob,
        target_company: targetCompany
      });

      if (response.data.success) {
        const optimizedResume = {
          ...selectedResume,
          optimized: true,
          optimizationDate: new Date().toISOString(),
          optimizedContent: response.data.optimized_content,
          suggestions: response.data.suggestions
        };
        
        setResumes(resumes.map(r => r.id === selectedResume.id ? optimizedResume : r));
        setSelectedResume(optimizedResume);
        
        setChatHistory([
          ...chatHistory,
          {
            type: 'ai',
            message: `✅ Resume optimized successfully using ${response.data.provider}!\n\n${response.data.optimized_content}`
          }
        ]);
      } else {
        setChatHistory([
          ...chatHistory,
          {
            type: 'ai',
            message: `⚠️ Optimization failed: ${response.data.error}\n\nFallback suggestions:\n${response.data.fallback_suggestions?.join('\n') || 'Please try again later.'}`
          }
        ]);
      }
    } catch (error) {
      console.error('Optimization failed:', error);
      setChatHistory([
        ...chatHistory,
        {
          type: 'ai',
          message: `❌ Optimization failed: ${error.response?.data?.detail || error.message}`
        }
      ]);
    } finally {
      setIsOptimizing(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatMessage.trim() || !selectedResume) return;
    if (!geminiKey) {
      if (onRequestGeminiKey) onRequestGeminiKey();
      return;
    }
    
    const userMessage = { type: 'user', message: chatMessage };
    setChatHistory([...chatHistory, userMessage]);
    const currentMessage = chatMessage;
    setChatMessage('');
    setIsChatting(true);
    
    try {
      const response = await axios.post('/api/resume/chat', {
        resume_content: selectedResume.content,
        message: currentMessage,
        chat_history: chatHistory.map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.message
        }))
      });

      if (response.data.success) {
        const aiResponse = {
          type: 'ai',
          message: response.data.response
        };
        setChatHistory(prev => [...prev, aiResponse]);
      } else {
        const aiResponse = {
          type: 'ai',
          message: response.data.fallback_response || 'Sorry, I encountered an error. Please try again.'
        };
        setChatHistory(prev => [...prev, aiResponse]);
      }
    } catch (error) {
      console.error('Chat failed:', error);
      const aiResponse = {
        type: 'ai',
        message: `Sorry, I'm having trouble right now: ${error.response?.data?.detail || error.message}`
      };
      setChatHistory(prev => [...prev, aiResponse]);
    } finally {
      setIsChatting(false);
    }
  };

  const deleteResume = (id) => {
    setResumes(resumes.filter(r => r.id !== id));
    if (selectedResume?.id === id) {
      setSelectedResume(null);
    }
  };

  // Before optimization/chat, check for missing fields
  const handleOptimizeClick = () => {
    if (missingFields.length > 0) return; // Will prompt user
    optimizeResume();
  };
  const handleChatClick = () => {
    if (missingFields.length > 0) return; // Will prompt user
    sendChatMessage();
  };

  // If Gemini key is missing, show a prompt
  if (!geminiKey) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-lg flex flex-col items-center justify-center min-h-[60vh]">
        <Sparkles className="w-12 h-12 text-blue-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">AI Resume Optimization</h2>
        <p className="text-gray-600 mb-4 text-center max-w-md">To use AI-powered resume optimization and chat, please connect your <b>Gemini API key</b>.</p>
        <button
          onClick={onRequestGeminiKey}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          Connect Gemini
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      {/* Profile Summary */}
      {profile && (
        <div className="mb-6 flex items-center space-x-4 bg-blue-50 p-4 rounded-lg">
          {profile.avatar ? (
            <img src={profile.avatar} alt="avatar" className="w-12 h-12 rounded-full object-cover" />
          ) : (
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-xl font-bold">{profile.name?.charAt(0) || 'U'}</span>
            </div>
          )}
          <div>
            <p className="font-semibold text-gray-900">{profile.name}</p>
            <p className="text-xs text-gray-500">{profile.email}</p>
            {profile.skills && (
              <p className="text-xs text-blue-600">Skills: {Array.isArray(profile.skills) ? profile.skills.join(', ') : profile.skills}</p>
            )}
            {profile.target_roles && (
              <p className="text-xs text-purple-600">Target Roles: {Array.isArray(profile.target_roles) ? profile.target_roles.join(', ') : profile.target_roles}</p>
            )}
          </div>
        </div>
      )}
      {/* Prompt for missing fields if any */}
      {missingFields.length > 0 && (
        <form onSubmit={handleSaveMissingFields} className="mb-6 bg-yellow-50 p-4 rounded-lg">
          <h3 className="font-semibold text-yellow-800 mb-2">We need a bit more info to optimize your resume or chat:</h3>
          {missingFields.map(field => (
            <div key={field} className="mb-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </label>
              <input
                type="text"
                value={missingFieldValues[field] || ''}
                onChange={e => handleMissingFieldChange(field, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          ))}
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" disabled={savingMissing}>
            Save & Continue
          </button>
        </form>
      )}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Resume Manager</h2>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <Upload className="w-4 h-4 mr-2" />
          {isUploading ? 'Uploading...' : 'Upload Resume'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Resume List */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold mb-4">Your Resumes</h3>
          <div className="space-y-3">
            {resumes.map((resume) => (
              <div
                key={resume.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedResume?.id === resume.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedResume(resume)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-gray-600 mr-3" />
                    <div>
                      <p className="font-medium text-gray-800">{resume.name}</p>
                      <p className="text-sm text-gray-500">
                        {resume.wordCount || Math.round(resume.size / 1024)} {resume.wordCount ? 'words' : 'KB'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteResume(resume.id);
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                {resume.optimized && (
                  <div className="mt-2 flex items-center text-green-600 text-sm">
                    <Edit3 className="w-4 h-4 mr-1" />
                    Optimized
                  </div>
                )}
              </div>
            ))}
            {resumes.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Upload className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No resumes uploaded yet</p>
                <p className="text-sm">Upload your first resume to get started</p>
              </div>
            )}
          </div>
        </div>

        {/* Resume Details & Chat */}
        <div className="lg:col-span-2">
          {selectedResume ? (
            <div className="space-y-6">
              {/* Resume Actions */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h3 className="text-lg font-semibold">{selectedResume.name}</h3>
                  <p className="text-sm text-gray-600">
                    Uploaded {new Date(selectedResume.uploadDate).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleOptimizeClick}
                    disabled={isOptimizing}
                    className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    <Edit3 className="w-4 h-4 mr-2" />
                    {isOptimizing ? 'Optimizing...' : 'Optimize with AI'}
                  </button>
                  <button className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </button>
                </div>
              </div>

              {/* Optimization Settings */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Optimization Settings</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Target Job</label>
                    <input
                      type="text"
                      value={targetJob}
                      onChange={e => setTargetJob(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={profile?.target_roles ? `e.g. ${Array.isArray(profile.target_roles) ? profile.target_roles[0] : profile.target_roles}` : 'Target job title'}
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Target Company / Skill</label>
                    <input
                      type="text"
                      value={targetCompany}
                      onChange={e => setTargetCompany(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={profile?.skills ? `e.g. ${Array.isArray(profile.skills) ? profile.skills[0] : profile.skills}` : 'Target company or skill'}
                    />
                  </div>
                </div>
              </div>

              {/* Resume Content */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Resume Content</h4>
                <div className="bg-white p-4 rounded border max-h-64 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {selectedResume.optimizedContent || selectedResume.content}
                  </pre>
                </div>
              </div>

              {/* AI Chat */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center mb-3">
                  <MessageCircle className="w-5 h-5 text-blue-600 mr-2" />
                  <h4 className="font-semibold">AI Resume Assistant</h4>
                  <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded flex items-center">
                    <Sparkles className="w-4 h-4 mr-1" /> Powered by Gemini
                  </span>
                </div>
                {/* Chat History */}
                <div className="bg-white p-4 rounded border max-h-64 overflow-y-auto mb-4">
                  {chatHistory.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                      Ask me anything about your resume or job applications!
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {chatHistory.map((msg, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-lg ${
                            msg.type === 'user'
                              ? 'bg-blue-100 ml-8'
                              : 'bg-gray-100 mr-8'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Chat Input */}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !isChatting && handleChatClick()}
                    placeholder="Ask about resume improvements, job applications..."
                    disabled={isChatting}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  />
                  <button
                    onClick={handleChatClick}
                    disabled={isChatting || !chatMessage.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isChatting ? 'Sending...' : 'Send'}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">Select a resume to view details</p>
              <p className="text-sm">Upload a resume to get started with AI optimization</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumeManager; 