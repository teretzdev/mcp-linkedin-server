import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Briefcase,
  MapPin,
  Building,
  Zap,
  Settings
} from 'lucide-react';
import axios from 'axios';

const Dashboard = ({ isLoggedIn, serverStatus }) => {
  const [stats, setStats] = useState({
    jobsApplied: 0,
    jobsSaved: 0,
    searchesPerformed: 0,
    lastActivity: null
  });
  const [credentialsConfigured, setCredentialsConfigured] = useState(false);

  const quickActions = [
    {
      title: 'Search Software Jobs',
      description: 'Find software engineering, development, and tech roles',
      icon: Search,
      href: '/jobs',
      color: 'bg-blue-500',
      requiresAuth: true,
      action: () => {
        // Pre-fill search with software keywords
        localStorage.setItem('quickSearch', JSON.stringify({
          query: 'software engineer developer',
          location: '',
          count: 10
        }));
        window.location.href = '/jobs';
      }
    },
    {
      title: 'Search Remote Jobs',
      description: 'Find remote and work-from-home opportunities',
      icon: Search,
      href: '/jobs',
      color: 'bg-green-500',
      requiresAuth: true,
      action: () => {
        localStorage.setItem('quickSearch', JSON.stringify({
          query: 'remote',
          location: 'Remote',
          count: 10
        }));
        window.location.href = '/jobs';
      }
    },
    {
      title: 'View Applications',
      description: 'Track jobs you\'ve applied to and their status',
      icon: CheckCircle,
      href: '/applications',
      color: 'bg-purple-500',
      requiresAuth: true
    },
    {
      title: 'Job Recommendations',
      description: 'Get personalized job suggestions from LinkedIn',
      icon: TrendingUp,
      href: '/saved',
      color: 'bg-orange-500',
      requiresAuth: true
    },
    {
      title: 'Saved Jobs',
      description: 'Review jobs you\'ve saved for later',
      icon: Clock,
      href: '/saved',
      color: 'bg-indigo-500',
      requiresAuth: true
    },
    {
      title: 'Update Credentials',
      description: 'Manage your LinkedIn login credentials',
      icon: Settings,
      href: '/settings',
      color: 'bg-gray-500',
      requiresAuth: false
    }
  ];

  const filteredActions = quickActions.filter(action => 
    !action.requiresAuth || (action.requiresAuth && isLoggedIn)
  );

  useEffect(() => {
    // Load credentials status (always check this)
    const loadCredentials = async () => {
      try {
        const credentialsResponse = await axios.get('/api/get_credentials');
        setCredentialsConfigured(credentialsResponse.data.configured || false);
      } catch (error) {
        console.log('Could not load credentials:', error.message);
      }
    };

    // Load job statistics (only if logged in)
    const loadStats = async () => {
      try {
        const [appliedResponse, savedResponse, recommendationsResponse] = await Promise.all([
          axios.get('/api/list_applied_jobs'),
          axios.get('/api/list_saved_jobs'),
          axios.get('/api/job_recommendations')
        ]);
        
        setStats({
          jobsApplied: appliedResponse.data.applied_jobs?.length || 0,
          jobsSaved: savedResponse.data.saved_jobs?.length || 0,
          searchesPerformed: 0, // Could track this in localStorage
          lastActivity: new Date().toLocaleDateString()
        });
      } catch (error) {
        console.log('Could not load stats:', error.message);
      }
    };

    // Always load credentials status
    loadCredentials();
    
    // Load stats only if logged in
    if (isLoggedIn) {
      loadStats();
    }
  }, [isLoggedIn]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">LinkedIn Job Hunter</h1>
        <p className="text-gray-600">
          Automate your job search on LinkedIn. Find, apply, and track jobs efficiently.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Jobs Applied</p>
              <p className="text-2xl font-bold text-gray-900">{stats.jobsApplied}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Jobs Saved</p>
              <p className="text-2xl font-bold text-gray-900">{stats.jobsSaved}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Search className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Searches</p>
              <p className="text-2xl font-bold text-gray-900">{stats.searchesPerformed}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Last Activity</p>
              <p className="text-sm font-bold text-gray-900">{stats.lastActivity || 'Never'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredActions.map((action, index) => (
            <div
              key={index}
              onClick={action.action || (() => window.location.href = action.href)}
              className="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 ${action.color} rounded-lg`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">API Bridge Status</span>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${serverStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {serverStatus === 'connected' ? 'LinkedIn MCP Server Connected' : 'LinkedIn MCP Server Disconnected'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">LinkedIn Credentials</span>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${credentialsConfigured ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={`text-sm ${credentialsConfigured ? 'text-green-600' : 'text-red-600'}`}>
                {credentialsConfigured ? 'Configured' : 'Not configured'}
              </span>
            </div>
          </div>
        </div>
        
        {!credentialsConfigured && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800 mb-2">
              LinkedIn credentials not configured. Please set up your credentials to start using the job search features.
            </p>
            <Link
              to="/settings"
              className="inline-flex items-center space-x-1 text-sm text-yellow-700 hover:text-yellow-800 font-medium"
            >
              <span>Go to Settings</span>
              <span>→</span>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 