import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Edit3, Download, MessageCircle, Plus, Trash2, Sparkles, Settings, MessageSquare } from 'lucide-react';
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
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [showChat, setShowChat] = useState(false);

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
    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await axios.post('/api/upload_resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.success) {
        setResumes(prev => [...prev, response.data.resume]);
        setSelectedResume(response.data.resume);
      }
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
      <div className="container container-lg">
        <div className="p-xl">
          <div className="card">
            <div className="card-body text-center py-xl">
              <h2 className="text-2xl font-bold text-primary mb-sm">AI Resume Optimization</h2>
              <p className="text-secondary mb-lg text-center max-w-md mx-auto">
                To use AI-powered resume optimization and chat, please connect your <b>Gemini API key</b>.
              </p>
              <button 
                onClick={() => window.location.href = '/settings'}
                className="btn btn-primary"
              >
                <Settings className="w-4 h-4 mr-sm" />
                Go to Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container container-lg">
      <div className="p-xl">
        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-primary flex items-center gap-sm">
              <FileText className="w-5 h-5" />
              Resume Manager
            </h1>
          </div>
          
          <div className="card-body">
            {/* Profile Info */}
            {profile && (
              <div className="card mb-lg">
                <div className="card-body">
                  <div className="flex items-center gap-md">
                    <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-white font-bold">
                      {profile.name?.charAt(0) || 'U'}
                    </div>
                    <div>
                      <p className="font-semibold text-primary">{profile.name}</p>
                      <p className="text-xs text-tertiary">{profile.email}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Upload Section */}
            <div className="card mb-lg">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-primary">Upload Resume</h2>
              </div>
              <div className="card-body">
                <div className="border-2 border-dashed border-border-primary rounded-lg p-xl text-center">
                  <Upload className="w-12 h-12 mx-auto mb-md text-tertiary" />
                  <p className="text-secondary mb-md">
                    Drag and drop your resume here, or click to browse
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="resume-upload"
                    disabled={isUploading}
                  />
                  <label htmlFor="resume-upload" className="btn btn-primary cursor-pointer">
                    {isUploading ? 'Uploading...' : 'Choose File'}
                  </label>
                </div>
              </div>
            </div>

            {/* Resumes List */}
            <div className="card mb-lg">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-primary">Your Resumes</h2>
              </div>
              <div className="card-body">
                {resumes.length === 0 ? (
                  <div className="text-center py-xl text-tertiary">
                    <Upload className="w-12 h-12 mx-auto mb-md text-tertiary" />
                    <p className="text-secondary">No resumes uploaded yet.</p>
                  </div>
                ) : (
                  <div className="space-y-md">
                    {resumes.map(resume => (
                      <div key={resume.id} className="card">
                        <div className="card-body">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-md">
                              <FileText className="w-5 h-5 text-primary" />
                              <div>
                                <p className="font-medium text-primary">{resume.name}</p>
                                <p className="text-sm text-tertiary">
                                  {resume.size} • Uploaded {resume.uploadDate}
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-sm">
                              <button
                                onClick={() => optimizeResume(resume.id)}
                                disabled={isOptimizing}
                                className="btn btn-primary btn-sm"
                              >
                                {isOptimizing ? 'Optimizing...' : 'Optimize'}
                              </button>
                              <button
                                onClick={() => setSelectedResume(resume)}
                                className="btn btn-secondary btn-sm"
                              >
                                View
                              </button>
                              <button
                                onClick={() => deleteResume(resume.id)}
                                className="btn btn-error btn-sm"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Analysis Results */}
            {analysis && selectedResume && (
              <div className="card mb-lg">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-primary">Analysis Results</h2>
                </div>
                <div className="card-body">
                  <div className="form-group">
                    <label className="form-label">Target Job</label>
                    <input
                      type="text"
                      value={analysis.targetJob || ''}
                      className="form-input"
                      readOnly
                    />
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Target Company / Skill</label>
                    <input
                      type="text"
                      value={analysis.targetCompany || ''}
                      className="form-input"
                      readOnly
                    />
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Optimized Resume</label>
                    <pre className="text-sm text-primary whitespace-pre-wrap bg-bg-secondary p-md rounded border">
                      {analysis.optimizedResume}
                    </pre>
                  </div>
                  
                  <div className="flex gap-sm">
                    <button className="btn btn-primary">
                      <Download className="w-4 h-4 mr-sm" />
                      Download Optimized
                    </button>
                    <button 
                      onClick={() => setShowChat(true)}
                      className="btn btn-secondary"
                    >
                      <MessageSquare className="w-4 h-4 mr-sm" />
                      Chat with AI
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Chat Interface */}
            {showChat && selectedResume && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-primary">AI Chat Assistant</h2>
                </div>
                <div className="card-body">
                  <div className="h-64 overflow-y-auto mb-md bg-bg-secondary p-md rounded border">
                    {chatHistory.map((msg, index) => (
                      <div key={index} className={`mb-sm ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
                        <div className={`inline-block p-sm rounded ${
                          msg.type === 'user' 
                            ? 'bg-primary text-white' 
                            : 'bg-bg-primary text-primary border'
                        }`}>
                          {msg.message}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex gap-sm">
                    <input
                      type="text"
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !isChatting && handleChatClick()}
                      placeholder="Ask about your resume..."
                      className="form-input flex-1"
                    />
                    <button onClick={handleChatClick} className="btn btn-primary">
                      Send
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeManager; 