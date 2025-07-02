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
  Clock
} from 'lucide-react';

const Sidebar = ({ isLoggedIn, serverStatus, onLogin, onLogout }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Job Search', href: '/jobs', icon: Search },
    { name: 'Applications', href: '/applications', icon: CheckCircle },
    { name: 'Saved Jobs', href: '/saved', icon: Clock },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const filteredNavigation = navigation.filter(item => 
    !item.requiresAuth || (item.requiresAuth && isLoggedIn)
  );

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Linkedin className="w-8 h-8 text-linkedin-600" />
          <span className="text-xl font-bold text-gray-900">MCP</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {filteredNavigation.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-linkedin-100 text-linkedin-700 border border-linkedin-200'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
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