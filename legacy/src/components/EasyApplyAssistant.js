import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Brain, FileText, CheckCircle, AlertCircle, Sparkles, ExternalLink, Loader2 } from 'lucide-react';
import axios from 'axios';

const EasyApplyAssistant = ({ onRequestGeminiKey }) => {
  const [currentJob, setCurrentJob] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [jobContext, setJobContext] = useState(null);
  const [applicantProfile, setApplicantProfile] = useState({
    name: 'John Doe',
    email: 'john.doe@email.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    experience_years: 5,
    skills: ['JavaScript', 'React', 'Node.js', 'Python', 'AWS'],
    education: 'Bachelor of Science in Computer Science',
    languages: ['English', 'Spanish'],
    work_authorization: 'US Citizen',
    salary_expectation: '$120,000 - $140,000',
    availability: '2 weeks notice',
    current_position: 'Senior Frontend Developer',
    target_roles: ['Software Engineer', 'Full Stack Developer'],
    achievements: ['Led team of 5 developers', 'Improved app performance by 60%']
  });
  const [fitAnalysis, setFitAnalysis] = useState(null);
  const [applicationStatus, setApplicationStatus] = useState('not_started');
  const geminiKey = localStorage.getItem('gemini_api_key') || '';

  // Get job URL from query parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('jobId');
    const jobUrl = urlParams.get('jobUrl');
    
    if (jobUrl) {
      startEasyApply(jobUrl);
    } else if (jobId) {
      // Convert job ID to URL if needed
      const jobUrl = `https://linkedin.com/jobs/view/${jobId}`;
      startEasyApply(jobUrl);
    }
  }, []);

  const startEasyApply = async (jobUrl) => {
    setIsProcessing(true);
    try {
      const response = await axios.post('/api/easy_apply/start', {
        job_url: jobUrl,
        gemini_api_key: geminiKey
      });
      
      if (response.data.status === 'success') {
        setCurrentJob(response.data.job_details);
        setQuestions(response.data.questions);
        setJobContext(response.data.job_details);
        setApplicationStatus('started');
        
        // Analyze job fit
        await analyzeJobFit(response.data.job_details);
      }
    } catch (error) {
      console.error('Failed to start Easy Apply:', error);
      // Fallback to sample data for demo
      setCurrentJob({
        title: 'Senior React Developer',
        company: 'TechCorp Inc.',
        location: 'San Francisco, CA',
        salary_range: '$120,000 - $150,000',
        description: 'We are looking for a Senior React Developer...',
        requirements: ['React', 'JavaScript', 'TypeScript', '5+ years experience'],
        responsibilities: ['Build scalable applications', 'Lead development team'],
        job_type: 'Full-time',
        remote: true
      });
      setJobContext({
        title: 'Senior React Developer',
        company: 'TechCorp Inc.',
        location: 'San Francisco, CA',
        salary_range: '$120,000 - $150,000',
        description: 'We are looking for a Senior React Developer...',
        requirements: ['React', 'JavaScript', 'TypeScript', '5+ years experience'],
        responsibilities: ['Build scalable applications', 'Lead development team'],
        job_type: 'Full-time',
        remote: true
      });
      setQuestions([
        {
          id: 1,
          question: 'How many years of experience do you have with React?',
          type: 'text',
          required: true,
          category: 'experience'
        },
        {
          id: 2,
          question: 'What is your work authorization status?',
          type: 'select',
          options: ['US Citizen', 'Green Card', 'H1B Visa', 'Other'],
          required: true,
          category: 'authorization'
        },
        {
          id: 3,
          question: 'What is your expected salary range?',
          type: 'text',
          required: true,
          category: 'compensation'
        },
        {
          id: 4,
          question: 'Describe a challenging project you worked on and how you overcame obstacles.',
          type: 'textarea',
          required: true,
          category: 'experience'
        },
        {
          id: 5,
          question: 'When can you start?',
          type: 'select',
          options: ['Immediately', '2 weeks notice', '1 month notice', '3 months notice'],
          required: true,
          category: 'availability'
        }
      ]);
      setApplicationStatus('started');
    } finally {
      setIsProcessing(false);
    }
  };

  const analyzeJobFit = async (jobDetails) => {
    if (!geminiKey) return;
    
    try {
      const response = await axios.post('/api/easy_apply/analyze_fit', {
        job_context: jobDetails,
        applicant_profile: applicantProfile,
        gemini_api_key: geminiKey,
        question_id: 'fit_analysis',
        question: 'Job fit analysis',
        question_type: 'text',
        question_category: 'analysis',
        required: false
      });
      
      if (response.data.success) {
        setFitAnalysis(response.data);
      }
    } catch (error) {
      console.error('Failed to analyze job fit:', error);
    }
  };

  const generateAnswer = async (questionId, question) => {
    if (!geminiKey) {
      if (onRequestGeminiKey) onRequestGeminiKey();
      return;
    }
    
    setIsProcessing(true);
    try {
      const response = await axios.post('/api/easy_apply/generate_answer', {
        question_id: questionId,
        question: question.question,
        question_type: question.type,
        question_category: question.category,
        required: question.required,
        options: question.options,
        max_length: question.max_length,
        job_context: jobContext,
        applicant_profile: applicantProfile,
        previous_answers: answers,
        gemini_api_key: geminiKey
      });
      
      if (response.data.success) {
        setAnswers(prev => ({
          ...prev,
          [questionId]: response.data.answer
        }));
        
        // Add suggestions
        if (response.data.suggestions) {
          setSuggestions(prev => [
            ...prev,
            ...response.data.suggestions.map(s => ({ ...s, questionId }))
          ]);
        }
      } else {
        // Use fallback answer
        setAnswers(prev => ({
          ...prev,
          [questionId]: response.data.fallback_answer
        }));
      }
    } catch (error) {
      console.error('Error generating answer:', error);
      // Generate fallback answer
      const fallbackAnswer = generateFallbackAnswer(question);
      setAnswers(prev => ({
        ...prev,
        [questionId]: fallbackAnswer
      }));
    } finally {
      setIsProcessing(false);
    }
  };

  const generateFallbackAnswer = (question) => {
    switch (question.category) {
      case 'experience':
        if (question.question.includes('React')) {
          return `${applicantProfile.experience_years} years`;
        } else if (question.question.includes('challenging project')) {
          return 'I led the development of a real-time dashboard that processed 1M+ data points daily. The main challenge was optimizing performance - I implemented virtual scrolling and lazy loading, reducing load times by 60%.';
        }
        return `${applicantProfile.experience_years} years of experience`;
      case 'authorization':
        return applicantProfile.work_authorization;
      case 'compensation':
        return applicantProfile.salary_expectation;
      case 'availability':
        return applicantProfile.availability;
      default:
        return 'I am excited about this opportunity and believe my skills and experience make me a great fit for this role.';
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const submitApplication = async () => {
    if (!geminiKey) {
      if (onRequestGeminiKey) onRequestGeminiKey();
      return;
    }
    
    setIsProcessing(true);
    try {
      const response = await axios.post('/api/easy_apply/submit', {
        job_url: currentJob?.job_url || window.location.href,
        answers: answers,
        applicant_profile: applicantProfile,
        job_context: jobContext
      });
      
      if (response.data.status === 'success') {
        setApplicationStatus('submitted');
        alert('Application submitted successfully!');
      } else {
        throw new Error(response.data.message || 'Submission failed');
      }
    } catch (error) {
      console.error('Submission failed:', error);
      alert(`Submission failed: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // If Gemini key is missing, show a prompt
  if (!geminiKey) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-lg flex flex-col items-center justify-center min-h-[60vh]">
        <Sparkles className="w-12 h-12 text-blue-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">AI Easy Apply Assistant</h2>
        <p className="text-gray-600 mb-4 text-center max-w-md">To use AI-powered application form completion and answer suggestions, please connect your <b>Gemini API key</b>.</p>
        <button
          onClick={onRequestGeminiKey}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          Connect Gemini
        </button>
      </div>
    );
  }

  const renderQuestion = (question) => {
    const answer = answers[question.id] || '';
    return (
      <div key={question.id} className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-medium text-gray-800 mb-2">
              {question.question}
              {question.required && <span className="text-red-500 ml-1">*</span>}
            </h3>
            {question.type === 'text' && (
              <input
                type="text"
                value={answer}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your answer..."
              />
            )}
            {question.type === 'select' && (
              <select
                value={answer}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select an option...</option>
                {question.options?.map((option, index) => (
                  <option key={index} value={option}>{option}</option>
                ))}
              </select>
            )}
            {question.type === 'textarea' && (
              <textarea
                value={answer}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your detailed answer..."
              />
            )}
          </div>
          <button
            onClick={() => generateAnswer(question.id, question)}
            disabled={isProcessing}
            className="ml-4 flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Brain className="w-4 h-4 mr-2" />
            )}
            AI Help
          </button>
        </div>
        {/* Suggestions for this question */}
        {suggestions.filter(s => s.questionId === question.id).map((suggestion, index) => (
          <div key={index} className={`flex items-start p-3 rounded-lg mt-3 ${
            suggestion.type === 'improvement' ? 'bg-yellow-50 border border-yellow-200' : 'bg-green-50 border border-green-200'
          }`}>
            {suggestion.type === 'improvement' ? (
              <AlertCircle className="w-4 h-4 text-yellow-600 mr-2 mt-0.5" />
            ) : (
              <CheckCircle className="w-4 h-4 text-green-600 mr-2 mt-0.5" />
            )}
            <p className="text-sm text-gray-700">{suggestion.message}</p>
          </div>
        ))}
      </div>
    );
  };

  if (isProcessing && !currentJob) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Loading Easy Apply...</h2>
          <p className="text-sm text-gray-500 mt-2">Preparing your application form</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Easy Apply Assistant</h1>
            <p className="text-gray-600">AI-powered application form completion</p>
            {currentJob && (
              <div className="mt-2 text-sm text-gray-500">
                <span className="font-medium">{currentJob.title}</span> at <span className="font-medium">{currentJob.company}</span>
              </div>
            )}
          </div>
          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded flex items-center">
            <Sparkles className="w-4 h-4 mr-1" /> AI Powered
          </span>
        </div>

        {/* Job Fit Analysis */}
        {fitAnalysis && (
          <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
            <h3 className="text-lg font-medium text-gray-800 mb-4">Job Fit Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(fitAnalysis.fit_score * 100)}%
                </div>
                <div className="text-sm text-gray-600">Match Score</div>
              </div>
              <div>
                <h4 className="font-medium text-gray-800 mb-2">Strengths</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {fitAnalysis.strengths?.slice(0, 3).map((strength, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircle className="w-3 h-3 text-green-500 mr-2" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-800 mb-2">Recommendations</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {fitAnalysis.recommendations?.slice(0, 3).map((rec, index) => (
                    <li key={index} className="flex items-center">
                      <AlertCircle className="w-3 h-3 text-yellow-500 mr-2" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Progress */}
        <div className="bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(Object.keys(answers).length / questions.length) * 100}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          {Object.keys(answers).length} of {questions.length} questions completed
        </p>

        {/* Questions */}
        <div className="space-y-6 mt-6">
          {questions.map(renderQuestion)}
        </div>

        {/* Submit Button */}
        <div className="bg-white p-6 rounded-lg shadow-lg mt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-800">Ready to Submit?</h3>
              <p className="text-sm text-gray-600">
                Review your answers before submitting your application
              </p>
            </div>
            <button
              onClick={submitApplication}
              disabled={isProcessing || Object.keys(answers).length < questions.length}
              className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              {isProcessing ? 'Submitting...' : 'Submit Application'}
            </button>
          </div>
        </div>

        {/* Applicant Profile Summary */}
        <div className="bg-white p-6 rounded-lg shadow-lg mt-6">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Your Profile Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="font-medium">{applicantProfile.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Experience</p>
              <p className="font-medium">{applicantProfile.experience_years} years</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Location</p>
              <p className="font-medium">{applicantProfile.location}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Authorization</p>
              <p className="font-medium">{applicantProfile.work_authorization}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EasyApplyAssistant; 