import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
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
  Target
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
      link: '/job-search',
      color: 'bg-blue-500'
    },
    {
      title: 'Resume Manager',
      description: 'Optimize your resume',
      icon: FileText,
      link: '/resume-manager',
      color: 'bg-green-500'
    },
    {
      title: 'Easy Apply Assistant',
      description: 'AI-powered applications',
      icon: Zap,
      link: '/easy-apply',
      color: 'bg-purple-500'
    },
    {
      title: 'Analytics',
      description: 'Track your progress',
      icon: TrendingUp,
      link: '/analytics',
      color: 'bg-orange-500'
    }
  ]);

  const [profile, setProfile] = useState(null);

  useEffect(() => {
    loadDashboardData();
    fetchUserProfile();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Fetch jobs applied, jobs saved, and analytics in parallel
      const [appliedRes, savedRes, analyticsRes] = await Promise.all([
        axios.get('/api/list_applied_jobs'),
        axios.get('/api/list_saved_jobs'),
        axios.get('/api/application_analytics')
      ]);
      const appliedJobs = appliedRes.data.applied_jobs || [];
      const savedJobs = savedRes.data.saved_jobs || [];
      const analytics = analyticsRes.data.analytics || {};

      // Aggregate stats
      setStats({
        jobsViewed: analytics.jobs_viewed || appliedJobs.length + savedJobs.length, // fallback if not available
        jobsApplied: appliedJobs.length,
        jobsSaved: savedJobs.length,
        successRate: analytics.success_rate || 0
      });

      // Build recent activity from applied and saved jobs
      const activity = [];
      appliedJobs.slice(0, 5).forEach(job => {
        activity.push({
          id: `applied-${job.id}`,
          type: 'application',
          title: `Applied to ${job.title} at ${job.company}`,
          time: job.date_applied ? new Date(job.date_applied).toLocaleString() : '',
          status: job.status || 'applied'
        });
      });
      savedJobs.slice(0, 5).forEach(job => {
        activity.push({
          id: `saved-${job.id}`,
          type: 'saved',
          title: `Saved ${job.title} at ${job.company}`,
          time: job.date_saved ? new Date(job.date_saved).toLocaleString() : '',
          status: 'saved'
        });
      });
      // Sort by most recent
      activity.sort((a, b) => new Date(b.time) - new Date(a.time));
      setRecentActivity(activity.slice(0, 8));
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // fallback to zeros if error
      setStats({ jobsViewed: 0, jobsApplied: 0, jobsSaved: 0, successRate: 0 });
      setRecentActivity([]);
    }
  };

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('/api/user/profile');
      if (response.ok) {
        setProfile(await response.json());
      }
    } catch (e) {
      setProfile(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-green-600';
      case 'disconnected':
        return 'text-red-600';
      default:
        return 'text-yellow-600';
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'application':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'saved':
        return <Star className="w-4 h-4 text-yellow-500" />;
      case 'viewed':
        return <Clock className="w-4 h-4 text-blue-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {profile?.name ? `Welcome, ${profile.name}!` : 'Dashboard'}
          </h1>
          <p className="text-gray-600">
            {profile?.target_roles ? `Target Roles: ${Array.isArray(profile.target_roles) ? profile.target_roles.join(', ') : profile.target_roles}` : "Here's your job search overview."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {profile?.avatar ? (
            <img src={profile.avatar} alt="avatar" className="w-10 h-10 rounded-full object-cover" />
          ) : (
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-lg font-medium">{profile?.name?.charAt(0) || 'U'}</span>
            </div>
          )}
          <div className={`w-3 h-3 rounded-full ${serverStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className={`text-sm font-medium ${getStatusColor(serverStatus)}`}>{serverStatus === 'connected' ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Profile Summary Card */}
      {profile && (
        <div className="bg-white rounded-lg shadow-sm p-6 flex items-center space-x-6">
          {profile.avatar ? (
            <img src={profile.avatar} alt="avatar" className="w-16 h-16 rounded-full object-cover" />
          ) : (
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-bold">{profile.name?.charAt(0) || 'U'}</span>
            </div>
          )}
          <div>
            <p className="text-lg font-semibold text-gray-900">{profile.name}</p>
            <p className="text-sm text-gray-500">{profile.email}</p>
            {profile.skills && (
              <p className="text-xs text-blue-600">Skills: {Array.isArray(profile.skills) ? profile.skills.join(', ') : profile.skills}</p>
            )}
            {profile.target_roles && (
              <p className="text-xs text-purple-600">Target Roles: {Array.isArray(profile.target_roles) ? profile.target_roles.join(', ') : profile.target_roles}</p>
            )}
            <Link to="/settings" className="text-xs text-blue-600 hover:underline">Edit Profile</Link>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Search className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Jobs Viewed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.jobsViewed}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
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

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Star className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Jobs Saved</p>
              <p className="text-2xl font-bold text-gray-900">{stats.jobsSaved}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats.successRate}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <Link
              key={index}
              to={action.link}
              className="group p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${action.color} text-white`}>
                  <action.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 group-hover:text-blue-600">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {recentActivity.length === 0 ? (
            <div className="text-gray-500">No recent activity found.</div>
          ) : (
            recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                {getActivityIcon(activity.type)}
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  activity.status === 'saved' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {activity.status}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* AI Assistant Section */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold mb-2">AI Assistant Ready</h2>
            <p className="text-blue-100">Your AI assistant is ready to help with job applications, resume optimization, and interview preparation.</p>
          </div>
          <div className="flex space-x-3">
            <Link
              to="/easy-apply"
              className="px-4 py-2 bg-white text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
            >
              Easy Apply
            </Link>
            <Link
              to="/resume-manager"
              className="px-4 py-2 bg-blue-700 text-white rounded-md hover:bg-blue-800 transition-colors"
            >
              Resume Manager
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
