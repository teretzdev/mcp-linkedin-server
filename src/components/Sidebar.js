import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Search, 
  Briefcase, 
  FileText, 
  Settings, 
  User,
  LogOut,
  Activity,
  Zap,
  Target,
  BookOpen,
  TrendingUp,
  MessageSquare,
  Bell,
  BarChart3
} from 'lucide-react';

function Sidebar({ isLoggedIn, serverStatus, onLogin, onLogout, currentUser }) {
  const location = useLocation();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('/api/user/profile');
        if (response.ok) {
          setProfile(await response.json());
        }
      } catch (e) {
        setProfile(null);
      }
    };
    fetchProfile();
  }, []);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Job Search', href: '/job-search', icon: Search },
    { name: 'Applications', href: '/applications', icon: Briefcase },
    { name: 'Saved Jobs', href: '/saved-jobs', icon: FileText },
    { name: 'Automation', href: '/automation', icon: Activity },
    { name: 'AI Automation', href: '/ai-automation', icon: Zap },
    { name: 'Resume Manager', href: '/resume-manager', icon: FileText },
    { name: 'Easy Apply', href: '/easy-apply', icon: Target },
    { name: 'Knowledge Base', href: '/applicant-knowledge', icon: BookOpen },
    { name: 'Follow-ups', href: '/follow-ups', icon: Bell },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="sidebar">
      <div className="p-6">
        {/* Logo */}
        <div className="flex items-center space-x-3 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">L</span>
          </div>
          <h1 className="text-xl font-bold">Job Hunter</h1>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`sidebar-item ${isActive(item.href) ? 'active' : ''}`}
              >
                <Icon className="sidebar-icon" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Server Status */}
        <div className="mt-8 p-3 card">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${serverStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs">
              {serverStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* User Profile */}
        {(profile || currentUser) && (
          <div className="mt-6 p-3 card">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                {profile?.avatar ? (
                  <img src={profile.avatar} alt="avatar" className="w-8 h-8 rounded-full object-cover" />
                ) : (
                  <span className="text-white text-sm font-medium">
                    {(profile?.name || currentUser?.name || 'U').charAt(0)}
                  </span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {profile?.name || currentUser?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {profile?.email || currentUser?.email || 'user@example.com'}
                </p>
                {profile?.skills && (
                  <p className="text-xs text-blue-600 truncate">Skills: {Array.isArray(profile.skills) ? profile.skills.join(', ') : profile.skills}</p>
                )}
                {profile?.target_roles && (
                  <p className="text-xs text-purple-600 truncate">Roles: {Array.isArray(profile.target_roles) ? profile.target_roles.join(', ') : profile.target_roles}</p>
                )}
              </div>
            </div>
            <Link
              to="/settings"
              className="block mt-2 text-xs text-blue-600 hover:underline text-center"
            >
              Edit Profile / Settings
            </Link>
            <button
              onClick={onLogout}
              className="mt-3 w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
