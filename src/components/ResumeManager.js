import React, { useState, useRef } from 'react';
import { Upload, FileText, Edit3, Download, MessageCircle, Plus, Trash2, Sparkles } from 'lucide-react';

const ResumeManager = ({ onRequestGeminiKey }) => {
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const fileInputRef = useRef();
  const geminiKey = localStorage.getItem('gemini_api_key') || '';

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    try {
      // Simulate file upload
      const newResume = {
        id: Date.now(),
        name: file.name,
        size: file.size,
        type: file.type,
        uploadDate: new Date().toISOString(),
        content: await file.text(),
        optimized: false
      };

      setResumes([...resumes, newResume]);
      setSelectedResume(newResume);
    } catch (error) {
      console.error('Upload failed:', error);
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
      // Simulate AI optimization
      await new Promise(resolve => setTimeout(resolve, 2000));
      const optimizedResume = {
        ...selectedResume,
        optimized: true,
        optimizationDate: new Date().toISOString()
      };
      setResumes(resumes.map(r => r.id === selectedResume.id ? optimizedResume : r));
      setSelectedResume(optimizedResume);
      setChatHistory([
        ...chatHistory,
        {
          type: 'ai',
          message: 'I\'ve analyzed your resume and made the following improvements:\n\n• Enhanced action verbs for better impact\n• Improved formatting and structure\n• Added relevant keywords for ATS systems\n• Strengthened achievement descriptions\n\nWould you like me to explain any specific changes?'
        }
      ]);
    } catch (error) {
      console.error('Optimization failed:', error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return;
    if (!geminiKey) {
      if (onRequestGeminiKey) onRequestGeminiKey();
      return;
    }
    const userMessage = { type: 'user', message: chatMessage };
    setChatHistory([...chatHistory, userMessage]);
    setChatMessage('');
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        type: 'ai',
        message: `I can help you with that! Here are some suggestions for improving your resume:\n\n• Consider adding more quantifiable achievements\n• Use industry-specific keywords\n• Highlight relevant skills for the target role\n\nWould you like me to help you rewrite any specific section?`
      };
      setChatHistory(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const deleteResume = (id) => {
    setResumes(resumes.filter(r => r.id !== id));
    if (selectedResume?.id === id) {
      setSelectedResume(null);
    }
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
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Resume Manager</h2>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload Resume
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
                        {(resume.size / 1024).toFixed(1)} KB
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
                    onClick={optimizeResume}
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

              {/* Resume Content */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Resume Content</h4>
                <div className="bg-white p-4 rounded border max-h-64 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {selectedResume.content}
                  </pre>
                </div>
              </div>

              {/* AI Chat */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center mb-3">
                  <MessageCircle className="w-5 h-5 text-blue-600 mr-2" />
                  <h4 className="font-semibold">AI Resume Assistant</h4>
                  <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded flex items-center"><Sparkles className="w-4 h-4 mr-1" /> Need help? Ask Gemini!</span>
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
                    onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                    placeholder="Ask about resume improvements, job applications..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={sendChatMessage}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Send
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