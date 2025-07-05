import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Search, 
  User, 
  MessageCircle, 
  Settings,
  Activity,
  LogIn,
  LogOut,
  Linkedin,
  CheckCircle,
  Clock,
  Bot,
  Briefcase,
  Bookmark,
  FileText,
  MessageSquare,
  Zap,
  Brain,
  Bell,
  BarChart3
} from 'lucide-react';

const Sidebar = ({ isLoggedIn, serverStatus, onLogin, onLogout, currentUser }) => {
  const location = useLocation();

  const navigationItems = [
    // Core
    { section: 'Core' },
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/job-search', icon: Search, label: 'Job Search' },
    { path: '/applications', icon: Briefcase, label: 'Applications' },
    { path: '/saved-jobs', icon: Bookmark, label: 'Saved Jobs' },
    // AI & Automation
    { section: 'AI & Automation' },
    { path: '/easy-apply', icon: MessageSquare, label: 'Easy Apply Assistant' },
    { path: '/resume-manager', icon: FileText, label: 'Resume Manager' },
    { path: '/ai-automation', icon: Bot, label: 'AI Automation' },
    { path: '/automation', icon: Zap, label: 'Automation' },
    // Insights
    { section: 'Insights' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/applicant-knowledge', icon: Brain, label: 'Knowledge Base' },
    { path: '/follow-ups', icon: Bell, label: 'Follow-ups' },
    // Settings
    { section: 'Settings' },
    { path: '/settings', icon: Settings, label: 'Settings' }
  ];

  // Only filter items with a path (skip section dividers)
  const filteredNavigation = navigationItems.filter(item => !item.path || !item.requiresAuth || (item.requiresAuth && isLoggedIn));

  const isActive = (path) => location.pathname === path;

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Linkedin className="w-8 h-8 text-linkedin-600" />
          <span className="text-xl font-bold text-gray-900">MCP</span>
        </div>
      </div>

      {/* User Profile */}
      {currentUser && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <img 
              src={currentUser.avatar} 
              alt={currentUser.name}
              className="w-10 h-10 rounded-full"
            />
            <div>
              <p className="font-medium text-gray-800">{currentUser.name}</p>
              <p className="text-sm text-gray-600">{currentUser.email}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {filteredNavigation.map((item, idx) => {
          if (item.section) {
            return (
              <div key={item.section + idx} className="mt-4 mb-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                {item.section}
              </div>
            );
          }
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.path)
                  ? 'bg-linkedin-100 text-linkedin-700 border border-linkedin-200'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Status and Actions */}
      <div className="p-4 border-t border-gray-200">
        <div className="mb-4">
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${
            serverStatus === 'connected' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              serverStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span>Server {serverStatus}</span>
          </div>
        </div>

        {isLoggedIn && (
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default Sidebar; 