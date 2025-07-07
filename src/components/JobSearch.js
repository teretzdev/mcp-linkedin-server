import React, { useState, useMemo, useEffect } from 'react';
import { Search, Filter, XCircle, ArrowUpDown, LayoutList, LayoutGrid, Zap, Play, Pause, RotateCcw, Settings, User, FileText, TrendingUp } from 'lucide-react';
import axios from 'axios';

const EXPERIENCE_LEVELS = ['Entry Level', 'Mid Level', 'Senior Level'];
const JOB_TYPES = ['Full-time', 'Part-time', 'Contract'];
const SALARY_RANGES = ['$50k - $80k', '$80k - $120k', '$120k - $160k', '$120k+'];
const allSkills = ['React', 'JavaScript', 'Python', 'Django', 'Node.js'];
const SORT_OPTIONS = [
  { value: 'most_relevant', label: 'Most Relevant' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'date', label: 'Date' },
  { value: 'most_recent', label: 'Most Recent' },
  { value: 'highest_salary', label: 'Highest Salary' },
  { value: 'highest_rated', label: 'Highest Rated' },
];

function JobSearch({ updateSessionStats, sessionStats }) {
  // State for search and filters
  const [searchQuery, setSearchQuery] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [jobType, setJobType] = useState('');
  const [salaryRange, setSalaryRange] = useState('');
  const [skills, setSkills] = useState([]);
  const [sortBy, setSortBy] = useState('relevant');
  const [viewMode, setViewMode] = useState('list');
  const [jobs, setJobs] = useState([]);

  // Automation state
  const [automationStatus, setAutomationStatus] = useState('idle'); // idle, running, paused, error
  const [automationStats, setAutomationStats] = useState({
    jobsFound: 0,
    jobsApplied: 0,
    jobsSaved: 0,
    connectionsMade: 0,
    messagesSent: 0,
    interviewsScheduled: 0,
    lastRun: null
  });
  const [automationSettings, setAutomationSettings] = useState({
    // Job Search Settings
    autoApply: false,
    autoSave: true,
    maxJobsPerRun: 10,
    searchKeywords: '',
    targetCompanies: '',
    excludeCompanies: '',
    salaryRange: '',
    experienceLevel: '',
    jobType: '',
    location: '',
    remoteOnly: false,
    hybridAllowed: false,
    
    // Advanced Search Filters
    industry: '',
    companySize: '',
    fundingStage: '',
    benefits: [],
    skills: [],
    certifications: [],
    languages: [],
    
    // Networking Automation
    autoConnect: false,
    connectionMessage: '',
    targetRoles: [],
    targetIndustries: [],
    maxConnectionsPerDay: 5,
    
    // Messaging Automation
    autoMessage: false,
    messageTemplate: '',
    followUpDays: 3,
    maxMessagesPerDay: 10,
    
    // Profile Optimization
    autoOptimizeProfile: false,
    keywordOptimization: true,
    skillEndorsements: true,
    recommendations: true,
    
    // Company Research
    autoResearchCompanies: false,
    researchDepth: 'basic', // basic, detailed, comprehensive
    trackCompetitors: false,
    
    // Application Tracking
    trackApplications: true,
    followUpReminders: true,
    interviewPrep: false,
    
    // Salary & Negotiation
    salaryNegotiation: false,
    targetSalary: '',
    benefitsNegotiation: false,
    
    // Interview Preparation
    mockInterviews: false,
    questionBank: true,
    
    // Advanced Features
    aiResumeOptimization: false,
    coverLetterGeneration: false,
    jobMatchingScore: 0.7,
    duplicateDetection: true,
    
    // Timing & Scheduling
    preferredTimeSlots: [],
    timezone: '',
    workDays: [1, 2, 3, 4, 5], // Monday to Friday
    maxDailyHours: 8,
    
    // Safety & Limits
    rateLimit: true,
    maxActionsPerHour: 20,
    cooldownPeriod: 300, // 5 minutes
    safetyChecks: true
  });

  const toggleSkill = skill => {
    setSkills(skills => skills.includes(skill) ? skills.filter(s => s !== skill) : [...skills, skill]);
  };

  useEffect(() => {
    // Fetch jobs from backend
    const fetchJobs = async () => {
      try {
        const response = await axios.get('/api/job_search');
        setJobs(response.data.jobs || []);
      } catch (error) {
        setJobs([]);
      }
    };
    fetchJobs();
  }, []);

  const filteredJobs = useMemo(() => {
    let filtered = jobs;
    if (searchQuery) filtered = filtered.filter(j => j.title.toLowerCase().includes(searchQuery.toLowerCase()) || j.company.toLowerCase().includes(searchQuery.toLowerCase()));
    if (experienceLevel) filtered = filtered.filter(j => j.experienceLevel === experienceLevel);
    if (jobType) filtered = filtered.filter(j => j.jobType === jobType);
    if (salaryRange) filtered = filtered.filter(j => j.salaryRange === salaryRange);
    if (skills.length) filtered = filtered.filter(j => skills.every(skill => j.skills.includes(skill)));
    // Sorting
    if (sortBy === 'newest') filtered = [...filtered].sort((a, b) => new Date(b.datePosted) - new Date(a.datePosted));
    if (sortBy === 'salary') filtered = [...filtered].sort((a, b) => {
      const getSalary = s => parseInt(s.replace(/[^0-9]/g, ''));
      return getSalary(b.salaryRange) - getSalary(a.salaryRange);
    });
    return filtered;
  }, [jobs, searchQuery, experienceLevel, jobType, salaryRange, skills, sortBy]);

  const clearFilters = () => {
    setSearchQuery('');
    setExperienceLevel('');
    setJobType('');
    setSalaryRange('');
    setSkills([]);
    setSortBy('relevant');
  };

  const handleViewJob = (job) => {
    // Called when a job is viewed
    updateSessionStats({ jobs_viewed: (sessionStats.jobs_viewed || 0) + 1 });
    // Optionally, mark job as viewed in backend
  };

  const handleSaveJob = async (job) => {
    try {
      await axios.post('/api/save_job', { job_id: job.id });
      updateSessionStats({ jobs_saved: (sessionStats.jobs_saved || 0) + 1 });
    } catch (error) {}
  };

  const handleApplyJob = async (job) => {
    try {
      await axios.post('/api/apply_job', { job_id: job.id });
      updateSessionStats({ jobs_applied: (sessionStats.jobs_applied || 0) + 1 });
    } catch (error) {}
  };

  const handleStartAutomation = async () => {
    try {
      setAutomationStatus('running');
      const response = await axios.post('/api/automation/start', {
        searchQuery,
        experienceLevel,
        jobType,
        salaryRange,
        skills,
        settings: automationSettings
      });
      
      if (response.data.success) {
        setAutomationStats(prev => ({
          ...prev,
          lastRun: new Date().toISOString()
        }));
      }
    } catch (error) {
      console.error('Failed to start automation:', error);
      setAutomationStatus('error');
    }
  };

  const handlePauseAutomation = async () => {
    try {
      await axios.post('/api/automation/pause');
      setAutomationStatus('paused');
    } catch (error) {
      console.error('Failed to pause automation:', error);
    }
  };

  const handleStopAutomation = async () => {
    try {
      await axios.post('/api/automation/stop');
      setAutomationStatus('idle');
    } catch (error) {
      console.error('Failed to stop automation:', error);
    }
  };

  const handleResetAutomation = async () => {
    try {
      await axios.post('/api/automation/reset');
      setAutomationStats({
        jobsFound: 0,
        jobsApplied: 0,
        jobsSaved: 0,
        connectionsMade: 0,
        messagesSent: 0,
        interviewsScheduled: 0,
        lastRun: null
      });
      setAutomationStatus('idle');
    } catch (error) {
      console.error('Failed to reset automation:', error);
    }
  };

  const handleUpdateAutomationSettings = async () => {
    try {
      await axios.post('/api/automation/settings', automationSettings);
      // Show success message or update UI
    } catch (error) {
      console.error('Failed to update automation settings:', error);
    }
  };

  const handleOptimizeProfile = async () => {
    try {
      await axios.post('/api/automation/optimize-profile', {
        keywords: automationSettings.searchKeywords,
        targetRoles: automationSettings.targetRoles
      });
    } catch (error) {
      console.error('Failed to optimize profile:', error);
    }
  };

  const handleGenerateCoverLetter = async () => {
    try {
      await axios.post('/api/automation/generate-cover-letter', {
        jobTitle: searchQuery,
        company: automationSettings.targetCompanies
      });
    } catch (error) {
      console.error('Failed to generate cover letter:', error);
    }
  };

  const handleResearchCompanies = async () => {
    try {
      await axios.post('/api/automation/research-companies', {
        companies: automationSettings.targetCompanies,
        depth: automationSettings.researchDepth
      });
    } catch (error) {
      console.error('Failed to research companies:', error);
    }
  };

  const handleNetworkAutomation = async () => {
    try {
      await axios.post('/api/automation/network', {
        targetRoles: automationSettings.targetRoles,
        messageTemplate: automationSettings.messageTemplate,
        maxConnections: automationSettings.maxConnectionsPerDay
      });
    } catch (error) {
      console.error('Failed to start networking automation:', error);
    }
  };

  const handleInterviewPrep = async () => {
    try {
      await axios.post('/api/automation/interview-prep', {
        jobTitle: searchQuery,
        company: automationSettings.targetCompanies,
        mockInterviews: automationSettings.mockInterviews
      });
    } catch (error) {
      console.error('Failed to start interview prep:', error);
    }
  };

  const handleSalaryNegotiation = async () => {
    try {
      await axios.post('/api/automation/salary-negotiation', {
        targetSalary: automationSettings.targetSalary,
        benefits: automationSettings.benefitsNegotiation
      });
    } catch (error) {
      console.error('Failed to start salary negotiation:', error);
    }
  };

  return (
    <div className="container container-xl">
      <div className="p-xl">
        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-primary flex items-center gap-sm">
              <Filter className="w-5 h-5 text-primary" /> Job Search
            </h1>
          </div>
          
          <div className="card-body">
            {/* Search Bar */}
            <div className="flex flex-col md:flex-row md:items-end md:gap-lg mb-lg">
              <div className="flex-1 mb-sm md:mb-0">
                <div className="relative">
                  <Search className="absolute left-md top-1/2 transform -translate-y-1/2 w-5 h-5 text-tertiary" />
                  <input
                    type="text"
                    placeholder="Search for jobs, companies, skills"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="form-input pl-xl"
                    data-testid="search-input"
                  />
                </div>
              </div>
              <div className="flex gap-sm">
                <button onClick={clearFilters} className="btn btn-secondary">
                  <XCircle className="w-4 h-4" />
                  Clear Filters
                </button>
              </div>
            </div>

            {/* Comprehensive Automation Controls */}
            <div className="card mb-lg bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-blue-500">
              <div className="card-header bg-transparent">
                <h2 className="text-lg font-semibold text-primary flex items-center gap-sm">
                  <Zap className="w-5 h-5 text-blue-600" />
                  LinkedIn AI Automation Suite - Complete Edition
                </h2>
              </div>
              <div className="card-body">
                {/* Status and Stats */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md mb-md">
                  <div className="flex items-center gap-sm">
                    <div className={`w-3 h-3 rounded-full ${
                      automationStatus === 'running' ? 'bg-green-500 animate-pulse' :
                      automationStatus === 'paused' ? 'bg-yellow-500' :
                      automationStatus === 'error' ? 'bg-red-500' : 'bg-gray-400'
                    }`}></div>
                    <span className="text-sm font-medium capitalize">{automationStatus}</span>
                  </div>

                  <div className="text-sm">
                    <span className="font-medium">Jobs:</span> {automationStats.jobsFound} | 
                    <span className="font-medium"> Applied:</span> {automationStats.jobsApplied} | 
                    <span className="font-medium"> Saved:</span> {automationStats.jobsSaved}
                  </div>

                  <div className="text-sm">
                    <span className="font-medium">Connections:</span> {automationStats.connectionsMade} | 
                    <span className="font-medium"> Messages:</span> {automationStats.messagesSent}
                  </div>

                  <div className="text-sm text-tertiary">
                    {automationStats.lastRun ? 
                      `Last run: ${new Date(automationStats.lastRun).toLocaleTimeString()}` : 
                      'No runs yet'
                    }
                  </div>
                </div>

                {/* Main Control Buttons */}
                <div className="flex flex-wrap gap-sm mb-md">
                  <button
                    onClick={handleStartAutomation}
                    disabled={automationStatus === 'running'}
                    className="btn btn-primary flex items-center gap-sm"
                  >
                    <Play className="w-4 h-4" />
                    Start Full Automation
                  </button>
                  
                  <button
                    onClick={handlePauseAutomation}
                    disabled={automationStatus !== 'running'}
                    className="btn btn-warning flex items-center gap-sm"
                  >
                    <Pause className="w-4 h-4" />
                    Pause
                  </button>
                  
                  <button
                    onClick={handleStopAutomation}
                    disabled={automationStatus === 'idle'}
                    className="btn btn-danger flex items-center gap-sm"
                  >
                    <XCircle className="w-4 h-4" />
                    Stop
                  </button>
                  
                  <button
                    onClick={handleResetAutomation}
                    className="btn btn-secondary flex items-center gap-sm"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Reset Stats
                  </button>
                </div>

                {/* Specialized Automation Buttons */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-sm mb-md">
                  <button
                    onClick={handleOptimizeProfile}
                    className="btn btn-outline btn-sm flex items-center gap-sm"
                  >
                    <User className="w-4 h-4" />
                    Optimize Profile
                  </button>
                  
                  <button
                    onClick={handleGenerateCoverLetter}
                    className="btn btn-outline btn-sm flex items-center gap-sm"
                  >
                    <FileText className="w-4 h-4" />
                    Generate Cover Letter
                  </button>
                  
                  <button
                    onClick={handleResearchCompanies}
                    className="btn btn-outline btn-sm flex items-center gap-sm"
                  >
                    <Search className="w-4 h-4" />
                    Research Companies
                  </button>
                  
                  <button
                    onClick={handleNetworkAutomation}
                    className="btn btn-outline btn-sm flex items-center gap-sm"
                  >
                    <User className="w-4 h-4" />
                    Auto Network
                  </button>
                  
                  <button
                    onClick={handleInterviewPrep}
                    className="btn btn-outline btn-sm flex items-center gap-sm"
                  >
                    <TrendingUp className="w-4 h-4" />
                    Interview Prep
                  </button>
                  
                  <button
                    onClick={handleSalaryNegotiation}
                    className="btn btn-outline btn-sm flex items-center gap-sm"
                  >
                    <TrendingUp className="w-4 h-4" />
                    Salary Negotiation
                  </button>
                </div>

                {/* Advanced Settings Tabs */}
                <div className="mb-md">
                  <div className="flex flex-wrap gap-sm border-b border-gray-200">
                    <button className="px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600">
                      Job Search
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-blue-600">
                      Networking
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-blue-600">
                      Profile
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-blue-600">
                      Messaging
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-blue-600">
                      Research
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-blue-600">
                      Advanced
                    </button>
                  </div>
                </div>

                {/* Job Search Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md mb-md">
                  <div>
                    <label className="block text-sm font-medium mb-xs">Max Jobs Per Run</label>
                    <input
                      type="number"
                      value={automationSettings.maxJobsPerRun}
                      onChange={e => setAutomationSettings(prev => ({...prev, maxJobsPerRun: parseInt(e.target.value)}))}
                      className="form-input w-full"
                      min="1"
                      max="100"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Search Keywords</label>
                    <input
                      type="text"
                      value={automationSettings.searchKeywords}
                      onChange={e => setAutomationSettings(prev => ({...prev, searchKeywords: e.target.value}))}
                      placeholder="e.g., React, Python, Remote, Senior"
                      className="form-input w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Target Companies</label>
                    <input
                      type="text"
                      value={automationSettings.targetCompanies}
                      onChange={e => setAutomationSettings(prev => ({...prev, targetCompanies: e.target.value}))}
                      placeholder="e.g., Google, Microsoft, Apple"
                      className="form-input w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Exclude Companies</label>
                    <input
                      type="text"
                      value={automationSettings.excludeCompanies}
                      onChange={e => setAutomationSettings(prev => ({...prev, excludeCompanies: e.target.value}))}
                      placeholder="e.g., StartupX, CompanyY"
                      className="form-input w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Target Salary</label>
                    <input
                      type="text"
                      value={automationSettings.targetSalary}
                      onChange={e => setAutomationSettings(prev => ({...prev, targetSalary: e.target.value}))}
                      placeholder="e.g., $120,000 - $150,000"
                      className="form-input w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Location</label>
                    <input
                      type="text"
                      value={automationSettings.location}
                      onChange={e => setAutomationSettings(prev => ({...prev, location: e.target.value}))}
                      placeholder="e.g., San Francisco, CA"
                      className="form-input w-full"
                    />
                  </div>
                </div>

                {/* Advanced Filters */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md mb-md">
                  <div>
                    <label className="block text-sm font-medium mb-xs">Industry</label>
                    <select
                      value={automationSettings.industry}
                      onChange={e => setAutomationSettings(prev => ({...prev, industry: e.target.value}))}
                      className="form-input w-full"
                    >
                      <option value="">Any Industry</option>
                      <option value="technology">Technology</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="finance">Finance</option>
                      <option value="education">Education</option>
                      <option value="retail">Retail</option>
                      <option value="manufacturing">Manufacturing</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Company Size</label>
                    <select
                      value={automationSettings.companySize}
                      onChange={e => setAutomationSettings(prev => ({...prev, companySize: e.target.value}))}
                      className="form-input w-full"
                    >
                      <option value="">Any Size</option>
                      <option value="startup">Startup (1-50)</option>
                      <option value="small">Small (51-200)</option>
                      <option value="medium">Medium (201-1000)</option>
                      <option value="large">Large (1000+)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Funding Stage</label>
                    <select
                      value={automationSettings.fundingStage}
                      onChange={e => setAutomationSettings(prev => ({...prev, fundingStage: e.target.value}))}
                      className="form-input w-full"
                    >
                      <option value="">Any Stage</option>
                      <option value="seed">Seed</option>
                      <option value="series-a">Series A</option>
                      <option value="series-b">Series B</option>
                      <option value="series-c">Series C+</option>
                      <option value="public">Public</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Job Matching Score</label>
                    <input
                      type="range"
                      min="0.1"
                      max="1.0"
                      step="0.1"
                      value={automationSettings.jobMatchingScore}
                      onChange={e => setAutomationSettings(prev => ({...prev, jobMatchingScore: parseFloat(e.target.value)}))}
                      className="w-full"
                    />
                    <span className="text-xs text-gray-500">{Math.round(automationSettings.jobMatchingScore * 100)}%</span>
                  </div>
                </div>

                {/* Automation Toggles */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-md mb-md">
                  <label className="flex items-center gap-xs text-sm">
                    <input
                      type="checkbox"
                      checked={automationSettings.autoApply}
                      onChange={e => setAutomationSettings(prev => ({...prev, autoApply: e.target.checked}))}
                      className="form-checkbox"
                    />
                    Auto Apply
                  </label>
                  
                  <label className="flex items-center gap-xs text-sm">
                    <input
                      type="checkbox"
                      checked={automationSettings.autoSave}
                      onChange={e => setAutomationSettings(prev => ({...prev, autoSave: e.target.checked}))}
                      className="form-checkbox"
                    />
                    Auto Save
                  </label>
                  
                  <label className="flex items-center gap-xs text-sm">
                    <input
                      type="checkbox"
                      checked={automationSettings.autoConnect}
                      onChange={e => setAutomationSettings(prev => ({...prev, autoConnect: e.target.checked}))}
                      className="form-checkbox"
                    />
                    Auto Connect
                  </label>
                  
                  <label className="flex items-center gap-xs text-sm">
                    <input
                      type="checkbox"
                      checked={automationSettings.autoMessage}
                      onChange={e => setAutomationSettings(prev => ({...prev, autoMessage: e.target.checked}))}
                      className="form-checkbox"
                    />
                    Auto Message
                  </label>
                  
                  <label className="flex items-center gap-xs text-sm">
                    <input
                      type="checkbox"
                      checked={automationSettings.remoteOnly}
                      onChange={e => setAutomationSettings(prev => ({...prev, remoteOnly: e.target.checked}))}
                      className="form-checkbox"
                    />
                    Remote Only
                  </label>
                  
                  <label className="flex items-center gap-xs text-sm">
                    <input
                      type="checkbox"
                      checked={automationSettings.aiResumeOptimization}
                      onChange={e => setAutomationSettings(prev => ({...prev, aiResumeOptimization: e.target.checked}))}
                      className="form-checkbox"
                    />
                    AI Resume
                  </label>
                </div>

                {/* Message Templates */}
                <div className="mb-md">
                  <label className="block text-sm font-medium mb-xs">Connection Message Template</label>
                  <textarea
                    value={automationSettings.connectionMessage}
                    onChange={e => setAutomationSettings(prev => ({...prev, connectionMessage: e.target.value}))}
                    placeholder="Hi [Name], I noticed your work at [Company] and would love to connect..."
                    className="form-input w-full h-20"
                  />
                </div>

                <div className="mb-md">
                  <label className="block text-sm font-medium mb-xs">Follow-up Message Template</label>
                  <textarea
                    value={automationSettings.messageTemplate}
                    onChange={e => setAutomationSettings(prev => ({...prev, messageTemplate: e.target.value}))}
                    placeholder="Hi [Name], I applied for the [Position] role and wanted to follow up..."
                    className="form-input w-full h-20"
                  />
                </div>

                {/* Safety Settings */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-md mb-md">
                  <div>
                    <label className="block text-sm font-medium mb-xs">Max Actions Per Hour</label>
                    <input
                      type="number"
                      value={automationSettings.maxActionsPerHour}
                      onChange={e => setAutomationSettings(prev => ({...prev, maxActionsPerHour: parseInt(e.target.value)}))}
                      className="form-input w-full"
                      min="1"
                      max="100"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Cooldown Period (seconds)</label>
                    <input
                      type="number"
                      value={automationSettings.cooldownPeriod}
                      onChange={e => setAutomationSettings(prev => ({...prev, cooldownPeriod: parseInt(e.target.value)}))}
                      className="form-input w-full"
                      min="30"
                      max="3600"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-xs">Max Connections Per Day</label>
                    <input
                      type="number"
                      value={automationSettings.maxConnectionsPerDay}
                      onChange={e => setAutomationSettings(prev => ({...prev, maxConnectionsPerDay: parseInt(e.target.value)}))}
                      className="form-input w-full"
                      min="1"
                      max="50"
                    />
                  </div>
                </div>

                {/* Save Settings Button */}
                <div className="flex justify-end">
                  <button
                    onClick={handleUpdateAutomationSettings}
                    className="btn btn-primary flex items-center gap-sm"
                  >
                    <Settings className="w-4 h-4" />
                    Save All Settings
                  </button>
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-md mb-lg">
              <select 
                value={experienceLevel} 
                onChange={e => setExperienceLevel(e.target.value)} 
                className="form-input"
              >
                <option value="">Experience Level</option>
                {EXPERIENCE_LEVELS.map(level => <option key={level} value={level}>{level}</option>)}
              </select>
              
              <select 
                value={jobType} 
                onChange={e => setJobType(e.target.value)} 
                className="form-input"
              >
                <option value="">Job Type</option>
                {JOB_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
              </select>
              
              <select 
                value={salaryRange} 
                onChange={e => setSalaryRange(e.target.value)} 
                className="form-input"
              >
                <option value="">Salary Range</option>
                {SALARY_RANGES.map(range => <option key={range} value={range}>{range}</option>)}
              </select>
              
              <div className="col-span-2 flex flex-wrap items-center gap-sm">
                {allSkills.map(skill => (
                  <button
                    key={skill}
                    onClick={() => toggleSkill(skill)}
                    className={`btn btn-sm ${skills.includes(skill) ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    {skill}
                  </button>
                ))}
              </div>
              
              <select 
                value={sortBy} 
                onChange={e => setSortBy(e.target.value)} 
                className="form-input"
              >
                {SORT_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
              
              <div className="flex items-center gap-sm">
                <button 
                  onClick={() => setViewMode('list')} 
                  className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
                >
                  <LayoutList className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => setViewMode('grid')} 
                  className={`btn btn-sm ${viewMode === 'grid' ? 'btn-primary' : 'btn-secondary'}`}
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Results Count */}
            <div className="mb-md text-secondary text-sm">
              Results: {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
            </div>

            {/* Job List */}
            <div>
              {filteredJobs.length === 0 ? (
                <div className="text-center py-xl text-tertiary">No jobs found matching your criteria.</div>
              ) : (
                <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 gap-md' : 'space-y-md'}>
                  {filteredJobs.map(job => (
                    <div 
                      key={job.id} 
                      onClick={() => handleViewJob(job)} 
                      className={`card cursor-pointer transition-fast hover:shadow-md ${
                        viewMode === 'grid' ? 'p-md' : 'p-lg'
                      }`}
                    >
                      <div className={viewMode === 'grid' ? 'space-y-sm' : 'flex flex-col md:flex-row md:items-center md:justify-between'}>
                        <div className="flex-1">
                          <div className="font-semibold text-lg text-primary mb-xs">{job.title}</div>
                          <div className="text-secondary mb-xs">{job.company} • {job.location}</div>
                          <div className="text-tertiary text-sm mb-xs">
                            Experience: {job.experienceLevel} | Type: {job.jobType} | Salary: {job.salaryRange}
                          </div>
                          <div className="text-tertiary text-xs">Skills: {job.skills.join(', ')}</div>
                        </div>
                        
                        <div className={`flex flex-col gap-sm ${viewMode === 'grid' ? 'mt-sm' : 'md:ml-lg'}`}>
                          <div className="text-tertiary text-sm">Posted: {job.datePosted}</div>
                          <div className="flex gap-sm">
                            <button 
                              onClick={e => { e.stopPropagation(); handleSaveJob(job); }} 
                              className="btn btn-sm btn-secondary"
                            >
                              Save
                            </button>
                            <button 
                              onClick={e => { e.stopPropagation(); handleApplyJob(job); }} 
                              className="btn btn-sm btn-success"
                            >
                              Apply
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
        </div>
      </div>
    </div>
  );
}

export default JobSearch; 