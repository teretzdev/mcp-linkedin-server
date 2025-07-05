import React, { useEffect, useState } from 'react';
import { 
  Loader2, 
  Filter, 
  Search, 
  Calendar, 
  Building, 
  MapPin, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Eye, 
  Edit3, 
  Plus,
  Download,
  BarChart3,
  ChevronDown,
  ChevronUp,
  Star,
  MessageSquare,
  ExternalLink
} from 'lucide-react';
import axios from 'axios';

const Applications = ({ updateSessionStats, sessionStats }) => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date_applied');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showAddNote, setShowAddNote] = useState(false);
  const [newNote, setNewNote] = useState('');
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Application statuses with colors and icons
  const statusConfig = {
    'applied': { label: 'Applied', color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
    'under_review': { label: 'Under Review', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
    'interview': { label: 'Interview', color: 'bg-purple-100 text-purple-800', icon: MessageSquare },
    'offer': { label: 'Offer', color: 'bg-green-100 text-green-800', icon: Star },
    'rejected': { label: 'Rejected', color: 'bg-red-100 text-red-800', icon: XCircle },
    'withdrawn': { label: 'Withdrawn', color: 'bg-gray-100 text-gray-800', icon: XCircle }
  };

  useEffect(() => {
    const fetchAppliedJobs = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await axios.get('/api/applied_jobs');
        const jobsWithStatus = (response.data.applied_jobs || []).map(job => ({
          ...job,
          status: job.status || 'applied',
          notes: job.notes || [],
          followUpDate: job.followUpDate || null,
          salary: job.salary || '',
          jobType: job.jobType || 'Full-time',
          remote: job.remote || false
        }));
        setJobs(jobsWithStatus);
        setFilteredJobs(jobsWithStatus);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load applied jobs.');
      } finally {
        setLoading(false);
      }
    };
    fetchAppliedJobs();
  }, []);

  // Filter and sort jobs
  useEffect(() => {
    let filtered = jobs.filter(job => {
      const matchesSearch = 
        job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.location?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || job.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });

    // Sort jobs
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'date_applied') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredJobs(filtered);
  }, [jobs, searchTerm, statusFilter, sortBy, sortOrder]);

  const handleViewJob = (job) => {
    updateSessionStats({ jobs_viewed: (sessionStats.jobs_viewed || 0) + 1 });
  };

  const updateJobStatus = async (jobId, newStatus) => {
    try {
      await axios.post('/api/update_applied_job', { job_id: jobId, status: newStatus });
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, status: newStatus } : job
        )
      );
      updateSessionStats({ jobs_applied: (sessionStats.jobs_applied || 0) });
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const addNote = async (jobId) => {
    if (!newNote.trim()) return;
    try {
      const note = {
        id: Date.now(),
        text: newNote,
        date: new Date().toISOString()
      };
      await axios.post('/api/add_applied_job_note', { job_id: jobId, note });
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, notes: [...(job.notes || []), note] }
            : job
        )
      );
      setNewNote('');
      setShowAddNote(false);
      updateSessionStats({ jobs_applied: (sessionStats.jobs_applied || 0) });
    } catch (error) {
      console.error('Failed to add note:', error);
    }
  };

  const exportApplications = () => {
    const csvContent = [
      ['Title', 'Company', 'Location', 'Status', 'Date Applied', 'Notes'],
      ...filteredJobs.map(job => [
        job.title || '',
        job.company || '',
        job.location || '',
        statusConfig[job.status]?.label || 'Applied',
        job.date_applied || '',
        (job.notes || []).map(note => note.text).join('; ')
      ])
    ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `applications-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getAnalytics = () => {
    const total = jobs.length;
    const statusCounts = {};
    const monthlyCounts = {};
    
    jobs.forEach(job => {
      // Count by status
      statusCounts[job.status] = (statusCounts[job.status] || 0) + 1;
      
      // Count by month
      const date = new Date(job.date_applied);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      monthlyCounts[monthKey] = (monthlyCounts[monthKey] || 0) + 1;
    });

    return { total, statusCounts, monthlyCounts };
  };

  const analytics = getAnalytics();

  if (loading) {
    return (
      <div className="flex items-center justify-center space-x-2 p-6">
        <Loader2 className="w-6 h-6 animate-spin text-linkedin-600" />
        <span className="text-gray-600">Loading applied jobs...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Applications</h1>
        <p className="text-gray-600">Track your job applications</p>
      </div>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Application Tracker</h1>
            <p className="text-gray-600">Track and manage your job applications</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </button>
            <button
              onClick={exportApplications}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      {showAnalytics && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Analytics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-600">Total Applications</p>
              <p className="text-2xl font-bold text-blue-900">{analytics.total}</p>
            </div>
            {Object.entries(analytics.statusCounts).map(([status, count]) => (
              <div key={status} className={`${statusConfig[status]?.color.replace('text-', 'bg-').replace('bg-', 'bg-').replace('100', '50')} p-4 rounded-lg`}>
                <p className={`text-sm ${statusConfig[status]?.color.split(' ')[1]}`}>{statusConfig[status]?.label}</p>
                <p className={`text-2xl font-bold ${statusConfig[status]?.color.split(' ')[1]}`}>{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search jobs, companies, or locations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4 ml-2" /> : <ChevronDown className="w-4 h-4 ml-2" />}
            </button>
          </div>
          <p className="text-sm text-gray-600">{filteredJobs.length} applications</p>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
              >
                <option value="all">All Statuses</option>
                {Object.entries(statusConfig).map(([key, config]) => (
                  <option key={key} value={key}>{config.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
              >
                <option value="date_applied">Date Applied</option>
                <option value="title">Job Title</option>
                <option value="company">Company</option>
                <option value="status">Status</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Order</label>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
              >
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Applications List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {filteredJobs.length === 0 ? (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No applications found matching your criteria.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredJobs.map((job, idx) => {
              const StatusIcon = statusConfig[job.status]?.icon || CheckCircle;
              return (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="font-medium text-gray-900">{job.title || 'Job Title'}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusConfig[job.status]?.color}`}>
                          <StatusIcon className="w-3 h-3 inline mr-1" />
                          {statusConfig[job.status]?.label}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                        <div className="flex items-center">
                          <Building className="w-4 h-4 mr-1" />
                          {job.company || 'Company'}
                        </div>
                        <div className="flex items-center">
                          <MapPin className="w-4 h-4 mr-1" />
                          {job.location || 'Location'}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          {job.date_applied ? new Date(job.date_applied).toLocaleDateString() : 'Date'}
                        </div>
                      </div>

                      {/* Notes Preview */}
                      {job.notes && job.notes.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500 mb-1">Latest Note:</p>
                          <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                            {job.notes[job.notes.length - 1].text}
                          </p>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <select
                        value={job.status}
                        onChange={(e) => updateJobStatus(job.id || idx, e.target.value)}
                        className="text-xs border border-gray-300 rounded px-2 py-1"
                      >
                        {Object.entries(statusConfig).map(([key, config]) => (
                          <option key={key} value={key}>{config.label}</option>
                        ))}
                      </select>
                      
                      <button
                        onClick={() => {
                          setSelectedJob(job);
                          setShowAddNote(true);
                        }}
                        className="p-2 text-gray-600 hover:text-linkedin-600 hover:bg-gray-100 rounded"
                        title="Add Note"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      
                      <a
                        href={job.jobUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-600 hover:text-linkedin-600 hover:bg-gray-100 rounded"
                        title="View Job"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Note Modal */}
      {showAddNote && selectedJob && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Add Note for {selectedJob.title}
            </h3>
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add a note about this application..."
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent resize-none"
            />
            <div className="flex justify-end space-x-2 mt-4">
              <button
                onClick={() => {
                  setShowAddNote(false);
                  setSelectedJob(null);
                  setNewNote('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={() => addNote(selectedJob.id || 0)}
                className="px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700"
              >
                Add Note
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Applications; 