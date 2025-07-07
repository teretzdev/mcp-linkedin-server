import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';
import { 
  Search, 
  Briefcase, 
  FileText, 
  TrendingUp, 
  Settings, 
  User,
  CheckCircle,
  Clock,
  Star,
  Activity,
  Zap,
  Target,
  Play,
  Pause,
  RotateCcw,
  XCircle,
  CheckSquare,
  Square,
  AlertCircle,
  Info,
  ExternalLink,
  ChevronDown
} from 'lucide-react';

function Dashboard({ isLoggedIn, serverStatus }) {
  const [stats, setStats] = useState({
    jobsViewed: 0,
    jobsApplied: 0,
    jobsSaved: 0,
    successRate: 0
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [quickActions, setQuickActions] = useState([
    {
      title: 'Start Job Search',
      description: 'Find new opportunities',
      icon: Search,
      href: '/job-search',
      color: 'blue'
    },
    {
      title: 'View Applications',
      description: 'Track your progress',
      icon: Briefcase,
      href: '/applications',
      color: 'green'
    },
    {
      title: 'Saved Jobs',
      description: 'Review your favorites',
      icon: FileText,
      href: '/saved-jobs',
      color: 'purple'
    },
    {
      title: 'AI Automation',
      description: 'Let AI help you',
      icon: Zap,
      href: '/ai-automation',
      color: 'orange'
    }
  ]);

  const [profile, setProfile] = useState(null);
  const [aiSuggestions, setAiSuggestions] = useState([]);

  // Automation state
  const [automationStatus, setAutomationStatus] = useState('idle');
  const [automationStats, setAutomationStats] = useState({
    jobsFound: 0,
    jobsApplied: 0,
    jobsSaved: 0,
    connectionsMade: 0,
    messagesSent: 0,
    interviewsScheduled: 0,
    lastRun: null
  });

  // Setup checklist state
  const [setupChecklist, setSetupChecklist] = useState([
    {
      id: 'linkedin-login',
      title: 'LinkedIn Account Setup',
      description: 'Ensure you\'re logged into LinkedIn',
      completed: false,
      required: true,
      priority: 'critical',
      action: 'Go to LinkedIn and verify login',
      link: 'https://linkedin.com'
    },
    {
      id: 'profile-complete',
      title: 'Complete LinkedIn Profile',
      description: 'Fill out all profile sections (experience, skills, education)',
      completed: false,
      required: true,
      priority: 'critical',
      action: 'Update your LinkedIn profile',
      link: 'https://linkedin.com/in/me'
    },
    {
      id: 'resume-upload',
      title: 'Upload Resume',
      description: 'Add your resume to the system for AI optimization',
      completed: false,
      required: true,
      priority: 'high',
      action: 'Upload resume in Resume Manager',
      link: '/resume-manager'
    },
    {
      id: 'job-preferences',
      title: 'Set Job Preferences',
      description: 'Configure your job search criteria and preferences',
      completed: false,
      required: true,
      priority: 'high',
      action: 'Configure job preferences',
      link: '/job-search'
    },
    {
      id: 'automation-settings',
      title: 'Configure Automation Settings',
      description: 'Set up automation parameters and safety limits',
      completed: false,
      required: true,
      priority: 'high',
      action: 'Configure automation settings',
      link: '/job-search'
    },
    {
      id: 'message-templates',
      title: 'Create Message Templates',
      description: 'Set up connection and follow-up message templates',
      completed: false,
      required: false,
      priority: 'medium',
      action: 'Create message templates',
      link: '/job-search'
    },
    {
      id: 'target-companies',
      title: 'Define Target Companies',
      description: 'List companies you want to work for',
      completed: false,
      required: false,
      priority: 'medium',
      action: 'Add target companies',
      link: '/job-search'
    },
    {
      id: 'salary-expectations',
      title: 'Set Salary Expectations',
      description: 'Define your target salary range',
      completed: false,
      required: false,
      priority: 'medium',
      action: 'Set salary expectations',
      link: '/job-search'
    },
    {
      id: 'network-strategy',
      title: 'Plan Networking Strategy',
      description: 'Define your networking approach and targets',
      completed: false,
      required: false,
      priority: 'low',
      action: 'Plan networking strategy',
      link: '/job-search'
    },
    {
      id: 'interview-prep',
      title: 'Prepare for Interviews',
      description: 'Set up interview preparation materials',
      completed: false,
      required: false,
      priority: 'low',
      action: 'Prepare interview materials',
      link: '/job-search'
    }
  ]);

  useEffect(() => {
    fetchDashboardData();
    fetchAutomationStatus();
    checkSetupProgress();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch user profile
      const profileResponse = await axios.get('/api/user/profile');
      if (profileResponse.data) {
        setProfile(profileResponse.data);
      }

      // Fetch stats
      const statsResponse = await axios.get('/api/stats');
      if (statsResponse.data) {
        setStats(statsResponse.data);
      }

      // Fetch recent activity
      const activityResponse = await axios.get('/api/activity');
      if (activityResponse.data) {
        setRecentActivity(activityResponse.data.slice(0, 5));
      }

      // Fetch AI recommendations
      try {
        const recommendationsResponse = await axios.get('/api/ai/recommendations');
        if (recommendationsResponse.data) {
          setAiSuggestions(recommendationsResponse.data.slice(0, 3));
        }
      } catch (error) {
        console.log('AI recommendations not available');
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchAutomationStatus = async () => {
    try {
      const response = await axios.get('/api/automation/status');
      if (response.data) {
        setAutomationStatus(response.data.status);
        setAutomationStats(response.data.stats || automationStats);
      }
    } catch (error) {
      console.log('Automation status not available');
    }
  };

  const checkSetupProgress = async () => {
    try {
      // Check if user is logged into LinkedIn
      const linkedinStatus = await axios.get('/api/linkedin/status');
      if (linkedinStatus.data.loggedIn) {
        updateChecklistItem('linkedin-login', true);
      }

      // Check if profile is complete
      const profileStatus = await axios.get('/api/linkedin/profile-status');
      if (profileStatus.data.complete) {
        updateChecklistItem('profile-complete', true);
      }

      // Check if resume is uploaded
      const resumeStatus = await axios.get('/api/resume/status');
      if (resumeStatus.data.uploaded) {
        updateChecklistItem('resume-upload', true);
      }

      // Check if job preferences are set
      const preferencesStatus = await axios.get('/api/preferences/status');
      if (preferencesStatus.data.configured) {
        updateChecklistItem('job-preferences', true);
        updateChecklistItem('automation-settings', true);
      }

      // Check if message templates are created
      const templatesStatus = await axios.get('/api/templates/status');
      if (templatesStatus.data.created) {
        updateChecklistItem('message-templates', true);
      }

      // Check if target companies are set
      const companiesStatus = await axios.get('/api/companies/status');
      if (companiesStatus.data.set) {
        updateChecklistItem('target-companies', true);
      }

      // Check if salary expectations are set
      const salaryStatus = await axios.get('/api/salary/status');
      if (salaryStatus.data.set) {
        updateChecklistItem('salary-expectations', true);
      }

    } catch (error) {
      console.log('Setup progress check not available');
    }
  };

  const updateChecklistItem = (id, completed) => {
    setSetupChecklist(prev => prev.map(item => 
      item.id === id ? { ...item, completed } : item
    ));
  };

  const toggleChecklistItem = (id) => {
    setSetupChecklist(prev => prev.map(item => 
      item.id === id ? { ...item, completed: !item.completed } : item
    ));
  };

  const getSetupProgress = () => {
    const completed = setupChecklist.filter(item => item.completed).length;
    const total = setupChecklist.length;
    return Math.round((completed / total) * 100);
  };

  const getCriticalItems = () => {
    return setupChecklist.filter(item => item.priority === 'critical' && !item.completed);
  };

  const getNextSteps = () => {
    return setupChecklist.filter(item => !item.completed).slice(0, 3);
  };

  const handleStartAutomation = async () => {
    try {
      setAutomationStatus('running');
      await axios.post('/api/automation/start');
      setAutomationStats(prev => ({
        ...prev,
        lastRun: new Date().toISOString()
      }));
    } catch (error) {
      console.error('Failed to start automation:', error);
      setAutomationStatus('error');
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

  const handlePauseAutomation = async () => {
    try {
      await axios.post('/api/automation/pause');
      setAutomationStatus('paused');
    } catch (error) {
      console.error('Failed to pause automation:', error);
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

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical': return <AlertCircle className="w-4 h-4" />;
      case 'high': return <AlertCircle className="w-4 h-4" />;
      case 'medium': return <Info className="w-4 h-4" />;
      case 'low': return <Info className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className="container container-xl">
      <div className="dashboard-container">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">
              {profile?.name ? `Welcome back, ${profile.name}!` : 'Welcome to LinkedIn Job Hunter'}
            </h1>
            <p className="dashboard-subtitle">
              {profile?.current_position ? `Currently: ${profile.current_position}` : 'Ready to find your next opportunity?'}
            </p>
          </div>
          <div className="dashboard-header-actions">
            <div className={`status status-${serverStatus}`}>
              <div className="status-indicator"></div>
              <span>{serverStatus === 'connected' ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
        </div>

        {/* Setup Progress Checklist */}
        <div className="dashboard-setup-checklist">
          <div className="setup-checklist-header">
            <h2 className="setup-checklist-title">
              <CheckSquare className="w-5 h-5 text-blue-600" />
              Getting Started Checklist
            </h2>
            <div className="setup-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${getSetupProgress()}%` }}
                ></div>
              </div>
              <span className="progress-text">{getSetupProgress()}% Complete</span>
            </div>
          </div>

          {/* Critical Items Warning */}
          {getCriticalItems().length > 0 && (
            <div className="critical-items-warning">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <h3 className="warning-title">Critical Setup Required</h3>
                <p className="warning-text">
                  {getCriticalItems().length} critical item{getCriticalItems().length !== 1 ? 's' : ''} must be completed before automation can start.
                </p>
              </div>
            </div>
          )}

          {/* Next Steps */}
          <div className="next-steps-section">
            <h3 className="next-steps-title">Next Steps to Get Started</h3>
            <div className="next-steps-list">
              {getNextSteps().map((item, index) => (
                <div key={item.id} className={`checklist-item ${item.completed ? 'completed' : ''}`}>
                  <button
                    onClick={() => toggleChecklistItem(item.id)}
                    className="checklist-checkbox"
                  >
                    {item.completed ? (
                      <CheckSquare className="w-5 h-5 text-green-600" />
                    ) : (
                      <Square className="w-5 h-5 text-gray-400" />
                    )}
                  </button>
                  <div className="checklist-content">
                    <div className="checklist-header">
                      <h4 className="checklist-item-title">{item.title}</h4>
                      <span className={`priority-badge ${getPriorityColor(item.priority)}`}>
                        {getPriorityIcon(item.priority)}
                        {item.priority}
                      </span>
                    </div>
                    <p className="checklist-description">{item.description}</p>
                    <div className="checklist-actions">
                      <Link to={item.link} className="checklist-action-btn">
                        <ExternalLink className="w-4 h-4" />
                        {item.action}
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Full Checklist Toggle */}
          <div className="full-checklist-toggle">
            <button className="toggle-btn">
              <span>View Full Checklist</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Profile Card */}
        {profile && (
          <div className="dashboard-profile-card">
            <div className="profile-info">
              <div className="profile-avatar">
                {profile.avatar ? (
                  <img src={profile.avatar} alt="Profile" />
                ) : (
                  <User className="w-8 h-8" />
                )}
              </div>
              <div className="profile-details">
                <h3 className="profile-name">{profile.name}</h3>
                <p className="profile-position">{profile.current_position}</p>
                <p className="profile-location">{profile.location}</p>
              </div>
            </div>
            <div className="profile-actions">
              <Link to="/settings" className="btn btn-secondary">
                <Settings className="w-4 h-4" />
                Edit Profile
              </Link>
            </div>
          </div>
        )}

        {/* Automation Status Card */}
        <div className="dashboard-automation-card">
          <div className="automation-header">
            <h2 className="automation-title">
              <Zap className="w-5 h-5 text-blue-600" />
              AI Automation Status
            </h2>
            <div className="automation-status-indicator">
              <div className={`status-dot ${automationStatus}`}></div>
              <span className="status-text capitalize">{automationStatus}</span>
            </div>
          </div>
          
          <div className="automation-stats">
            <div className="automation-stat">
              <span className="stat-label">Jobs Found:</span>
              <span className="stat-value">{automationStats.jobsFound}</span>
            </div>
            <div className="automation-stat">
              <span className="stat-label">Jobs Applied:</span>
              <span className="stat-value">{automationStats.jobsApplied}</span>
            </div>
            <div className="automation-stat">
              <span className="stat-label">Jobs Saved:</span>
              <span className="stat-value">{automationStats.jobsSaved}</span>
            </div>
            <div className="automation-stat">
              <span className="stat-label">Connections:</span>
              <span className="stat-value">{automationStats.connectionsMade}</span>
            </div>
            <div className="automation-stat">
              <span className="stat-label">Messages:</span>
              <span className="stat-value">{automationStats.messagesSent}</span>
            </div>
            <div className="automation-stat">
              <span className="stat-label">Interviews:</span>
              <span className="stat-value">{automationStats.interviewsScheduled}</span>
            </div>
            <div className="automation-stat">
              <span className="stat-label">Last Run:</span>
              <span className="stat-value">
                {automationStats.lastRun ? 
                  new Date(automationStats.lastRun).toLocaleTimeString() : 
                  'Never'
                }
              </span>
            </div>
          </div>

          <div className="automation-controls">
            <button
              onClick={handleStartAutomation}
              disabled={automationStatus === 'running' || getCriticalItems().length > 0}
              className="btn btn-primary btn-sm"
            >
              <Play className="w-4 h-4" />
              Start
            </button>
            
            <button
              onClick={handlePauseAutomation}
              disabled={automationStatus !== 'running'}
              className="btn btn-warning btn-sm"
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
            
            <button
              onClick={handleStopAutomation}
              disabled={automationStatus === 'idle'}
              className="btn btn-danger btn-sm"
            >
              <XCircle className="w-4 h-4" />
              Stop
            </button>
            
            <button
              onClick={handleResetAutomation}
              className="btn btn-secondary btn-sm"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            
            <Link to="/job-search" className="btn btn-outline btn-sm">
              <Settings className="w-4 h-4" />
              Configure
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="dashboard-stats-grid">
          <div className="stat-card">
            <div className="stat-icon jobs-viewed">
              <Activity className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <h3 className="stat-value">{stats.jobsViewed}</h3>
              <p className="stat-label">Jobs Viewed</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon jobs-applied">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <h3 className="stat-value">{stats.jobsApplied}</h3>
              <p className="stat-label">Jobs Applied</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon jobs-saved">
              <Star className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <h3 className="stat-value">{stats.jobsSaved}</h3>
              <p className="stat-label">Jobs Saved</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon success-rate">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <h3 className="stat-value">{stats.successRate}%</h3>
              <p className="stat-label">Success Rate</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard-section">
          <h2 className="section-title">Quick Actions</h2>
          <div className="quick-actions-grid">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Link key={index} to={action.href} className="quick-action-card">
                  <div className={`quick-action-icon ${action.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="quick-action-content">
                    <h3 className="quick-action-title">{action.title}</h3>
                    <p className="quick-action-description">{action.description}</p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Recent Activity */}
        {recentActivity.length > 0 && (
          <div className="dashboard-activity-card">
            <h2 className="dashboard-activity-title">Recent Activity</h2>
            <div className="dashboard-activity-list">
              {recentActivity.map((activity, index) => (
                <div key={index} className="dashboard-activity-item">
                  <div className={`dashboard-activity-status ${activity.status}`}></div>
                  <div className="dashboard-activity-content">
                    <p className="dashboard-activity-text">{activity.description}</p>
                    <p className="dashboard-activity-time">{activity.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Suggestions */}
        {aiSuggestions.length > 0 && (
          <div className="dashboard-ai-section">
            <h2 className="dashboard-ai-title">AI-Powered Insights</h2>
            <p className="dashboard-ai-desc">
              Get personalized job recommendations and application tips based on your profile and activity.
            </p>
            <div className="dashboard-ai-actions">
              <Link to="/ai-automation" className="dashboard-ai-btn">
                <Target className="w-4 h-4 mr-2" />
                View Recommendations
              </Link>
              <Link to="/job-search" className="dashboard-ai-btn">
                <Search className="w-4 h-4 mr-2" />
                Start Smart Search
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
