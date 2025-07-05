import React, { useEffect, useState } from 'react';
import ApplicationsFilters from './ApplicationsFilters';
import ApplicationsList from './ApplicationsList';
import ApplicationsAnalytics from './ApplicationsAnalytics';
import ApplicationsNotes from './ApplicationsNotes';
import { filterApplications, sortApplications, getApplicationsAnalytics, exportApplicationsCSV } from './ApplicationsUtils';
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

const Applications = () => {
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
        const response = await axios.get('/api/list_applied_jobs');
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

  useEffect(() => {
    let filtered = filterApplications(jobs, searchTerm, statusFilter);
    filtered = sortApplications(filtered, sortBy, sortOrder);
    setFilteredJobs(filtered);
  }, [jobs, searchTerm, statusFilter, sortBy, sortOrder]);

  const updateJobStatus = async (jobId, newStatus) => {
    try {
      // In a real app, this would call an API to update the status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, status: newStatus } : job
        )
      );
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
      
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, notes: [...(job.notes || []), note] }
            : job
        )
      );
      
      setNewNote('');
      setShowAddNote(false);
    } catch (error) {
      console.error('Failed to add note:', error);
    }
  };

  const analytics = getApplicationsAnalytics(jobs);

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
              onClick={exportApplicationsCSV(filteredJobs)}
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
      <ApplicationsFilters
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        sortBy={sortBy}
        setSortBy={setSortBy}
        sortOrder={sortOrder}
        setSortOrder={setSortOrder}
        showFilters={showFilters}
        setShowFilters={setShowFilters}
      />

      {/* Applications List */}
      <ApplicationsList
        jobs={filteredJobs}
        updateJobStatus={updateJobStatus}
        setSelectedJob={setSelectedJob}
        setShowAddNote={setShowAddNote}
        setShowAnalytics={setShowAnalytics}
      />

      {/* Add Note Modal */}
      {showAddNote && selectedJob && (
        <ApplicationsNotes
          job={selectedJob}
          newNote={newNote}
          setNewNote={setNewNote}
          addNote={addNote}
          showAddNote={showAddNote}
          setShowAddNote={setShowAddNote}
        />
      )}
    </div>
  );
};

export default Applications; 