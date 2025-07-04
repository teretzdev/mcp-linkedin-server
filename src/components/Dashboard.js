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
      href: '/job-search',
      color: 'bg-blue-500',
      requiresAuth: true,
      action: () => {
        // Pre-fill search with software keywords
        localStorage.setItem('quickSearch', JSON.stringify({
          query: 'software engineer developer',
          location: '',
          count: 10
        }));
        window.location.href = '/job-search';
      }
    },
    {
      title: 'Search Remote Jobs',
      description: 'Find remote and work-from-home opportunities',
      icon: Search,
      href: '/job-search',
      color: 'bg-green-500',
      requiresAuth: true,
      action: () => {
        localStorage.setItem('quickSearch', JSON.stringify({
          query: 'remote',
          location: 'Remote',
          count: 10
        }));
        window.location.href = '/job-search';
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
      href: '/saved-jobs',
      color: 'bg-orange-500',
      requiresAuth: true
    },
    {
      title: 'Saved Jobs',
      description: 'Review jobs you\'ve saved for later',
      icon: Clock,
      href: '/saved-jobs',
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
          {filteredActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <div
                key={index}
                className={`${action.color} rounded-lg p-4 text-white cursor-pointer hover:opacity-90 transition-opacity`}
                onClick={action.action || (() => window.location.href = action.href)}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-6 h-6" />
                  <div>
                    <h3 className="font-semibold">{action.title}</h3>
                    <p className="text-sm opacity-90">{action.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">API Bridge</span>
            <span className={`px-2 py-1 rounded text-sm font-medium ${
              serverStatus === 'connected' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {serverStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">LinkedIn Credentials</span>
            <span className={`px-2 py-1 rounded text-sm font-medium ${
              credentialsConfigured 
                ? 'bg-green-100 text-green-800' 
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {credentialsConfigured ? 'Configured' : 'Not Configured'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 