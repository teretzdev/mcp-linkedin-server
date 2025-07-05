import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Building, 
  MapPin, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Star,
  MessageSquare,
  Download,
  Filter,
  RefreshCw
} from 'lucide-react';
import axios from 'axios';

const ApplicationAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30');
  const [selectedMetric, setSelectedMetric] = useState('status');

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [analyticsResponse, applicationsResponse] = await Promise.all([
        axios.get('/api/application_analytics'),
        axios.get('/api/list_applied_jobs')
      ]);
      
      setAnalytics(analyticsResponse.data.analytics);
      setApplications(applicationsResponse.data.applied_jobs || []);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'applied': return 'bg-blue-500';
      case 'under_review': return 'bg-yellow-500';
      case 'interview': return 'bg-purple-500';
      case 'offer': return 'bg-green-500';
      case 'rejected': return 'bg-red-500';
      case 'withdrawn': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'applied': return 'Applied';
      case 'under_review': return 'Under Review';
      case 'interview': return 'Interview';
      case 'offer': return 'Offer';
      case 'rejected': return 'Rejected';
      case 'withdrawn': return 'Withdrawn';
      default: return status;
    }
  };

  const calculateMetrics = () => {
    if (!applications.length) return {};

    const filteredApplications = applications.filter(app => {
      if (timeRange === 'all') return true;
      const appDate = new Date(app.date_applied);
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - parseInt(timeRange));
      return appDate >= cutoffDate;
    });

    const total = filteredApplications.length;
    const statusCounts = {};
    const companyCounts = {};
    const locationCounts = {};
    const monthlyData = {};

    filteredApplications.forEach(app => {
      // Status counts
      const status = app.status || 'applied';
      statusCounts[status] = (statusCounts[status] || 0) + 1;

      // Company counts
      const company = app.company || 'Unknown';
      companyCounts[company] = (companyCounts[company] || 0) + 1;

      // Location counts
      const location = app.location || 'Unknown';
      locationCounts[location] = (locationCounts[location] || 0) + 1;

      // Monthly data
      if (app.date_applied) {
        const date = new Date(app.date_applied);
        const monthKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
        monthlyData[monthKey] = (monthlyData[monthKey] || 0) + 1;
      }
    });

    // Calculate success rate
    const successStatuses = ['interview', 'offer'];
    const successful = filteredApplications.filter(app => 
      successStatuses.includes(app.status || 'applied')
    ).length;
    const successRate = total > 0 ? (successful / total * 100) : 0;

    // Calculate response rate (any status change from applied)
    const responded = filteredApplications.filter(app => 
      app.status && app.status !== 'applied'
    ).length;
    const responseRate = total > 0 ? (responded / total * 100) : 0;

    return {
      total,
      statusCounts,
      companyCounts,
      locationCounts,
      monthlyData,
      successRate: Math.round(successRate * 10) / 10,
      responseRate: Math.round(responseRate * 10) / 10,
      averageApplicationsPerDay: total / Math.max(parseInt(timeRange), 1)
    };
  };

  const metrics = calculateMetrics();

  const exportAnalytics = () => {
    const csvContent = [
      ['Metric', 'Value'],
      ['Total Applications', metrics.total],
      ['Success Rate (%)', metrics.successRate],
      ['Response Rate (%)', metrics.responseRate],
      ['Average Applications/Day', (metrics.averageApplicationsPerDay || 0).toFixed(2)],
      ['', ''],
      ['Status Breakdown', ''],
      ...Object.entries(metrics.statusCounts || {}).map(([status, count]) => [
        getStatusLabel(status),
        count
      ]),
      ['', ''],
      ['Top Companies', ''],
      ...Object.entries(metrics.companyCounts || {})
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10)
        .map(([company, count]) => [company, count])
    ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `application-analytics-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center space-x-2 p-6">
        <RefreshCw className="w-6 h-6 animate-spin text-linkedin-600" />
        <span className="text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Application Analytics</h1>
            <p className="text-gray-600">Track your job search performance and insights</p>
          </div>
          <div className="flex items-center space-x-2">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="all">All time</option>
            </select>
            <button
              onClick={exportAnalytics}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Applications</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.successRate}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <MessageSquare className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Response Rate</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.responseRate}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Daily Average</p>
              <p className="text-2xl font-bold text-gray-900">{(metrics.averageApplicationsPerDay || 0).toFixed(1)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Status Breakdown</h2>
        <div className="space-y-3">
          {Object.entries(metrics.statusCounts || {})
            .sort(([,a], [,b]) => b - a)
            .map(([status, count]) => {
              const percentage = metrics.total > 0 ? (count / metrics.total * 100) : 0;
              return (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full ${getStatusColor(status)}`}></div>
                    <span className="font-medium text-gray-900">{getStatusLabel(status)}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 w-32">
                      <div 
                        className={`h-2 rounded-full ${getStatusColor(status)}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-16 text-right">
                      {count} ({(percentage || 0).toFixed(1)}%)
                    </span>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Top Companies */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Companies Applied To</h2>
        <div className="space-y-3">
          {Object.entries(metrics.companyCounts || {})
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10)
            .map(([company, count]) => (
              <div key={company} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Building className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-gray-900">{company}</span>
                </div>
                <span className="text-sm text-gray-600">{count} applications</span>
              </div>
            ))}
        </div>
      </div>

      {/* Monthly Trend */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Monthly Application Trend</h2>
        <div className="space-y-3">
          {Object.entries(metrics.monthlyData || {})
            .sort(([a], [b]) => new Date(a) - new Date(b))
            .map(([month, count]) => (
              <div key={month} className="flex items-center justify-between">
                <span className="font-medium text-gray-900">{month}</span>
                <div className="flex items-center space-x-4">
                  <div className="flex-1 bg-gray-200 rounded-full h-2 w-32">
                    <div 
                      className="h-2 rounded-full bg-linkedin-600"
                      style={{ 
                        width: `${Math.min((count / Math.max(...Object.values(metrics.monthlyData || {}))) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-16 text-right">{count}</span>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Insights */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Insights & Recommendations</h2>
        <div className="space-y-4">
          {metrics.successRate < 10 && (
            <div className="flex items-start space-x-3 p-4 bg-yellow-50 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-medium text-yellow-900">Low Success Rate</p>
                <p className="text-sm text-yellow-800">
                  Your success rate is below 10%. Consider improving your resume, 
                  tailoring applications, or expanding your search criteria.
                </p>
              </div>
            </div>
          )}

          {metrics.responseRate < 20 && (
            <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
              <MessageSquare className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium text-blue-900">Low Response Rate</p>
                <p className="text-sm text-blue-800">
                  Less than 20% of applications are getting responses. 
                  Focus on networking, improving your cover letters, and following up.
                </p>
              </div>
            </div>
          )}

          {metrics.averageApplicationsPerDay > 5 && (
            <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
              <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">High Application Volume</p>
                <p className="text-sm text-green-800">
                  You're applying to many jobs daily. Consider focusing on quality 
                  over quantity for better results.
                </p>
              </div>
            </div>
          )}

          {Object.keys(metrics.statusCounts || {}).includes('interview') && (metrics.statusCounts || {}).interview > 0 && (
            <div className="flex items-start space-x-3 p-4 bg-purple-50 rounded-lg">
              <Star className="w-5 h-5 text-purple-600 mt-0.5" />
              <div>
                <p className="font-medium text-purple-900">Interview Success</p>
                <p className="text-sm text-purple-800">
                  Great! You have {(metrics.statusCounts || {}).interview} interview(s). 
                  Focus on preparation and follow-up to convert these opportunities.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicationAnalytics; 