import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Brain, FileText, CheckCircle, AlertCircle, Sparkles, ExternalLink, Loader2 } from 'lucide-react';
import axios from 'axios';
import EasyApplyQuestionForm from './EasyApplyQuestionForm';
import EasyApplyJobSummary from './EasyApplyJobSummary';
import EasyApplyProfileSummary from './EasyApplyProfileSummary';
import EasyApplySuggestions from './EasyApplySuggestions';
import { analyzeJobFit, generateAnswer } from './EasyApplyUtils';

const EasyApplyAssistant = ({ onRequestGeminiKey }) => {
  const [currentJob, setCurrentJob] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [jobContext, setJobContext] = useState(null);
  const [applicantProfile, setApplicantProfile] = useState(null);
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

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleGenerateAnswer = (questionId, question) => {
    // ...stub: use generateAnswer utility...
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

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <EasyApplyJobSummary jobContext={jobContext} />
        <EasyApplyProfileSummary applicantProfile={applicantProfile} />
        <EasyApplyQuestionForm
          questions={questions}
          answers={answers}
          onAnswerChange={handleAnswerChange}
          onGenerateAnswer={handleGenerateAnswer}
          isProcessing={isProcessing}
        />
        <EasyApplySuggestions suggestions={suggestions} />
      </div>
    </div>
  );
};

export default EasyApplyAssistant; 