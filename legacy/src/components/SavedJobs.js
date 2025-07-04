import React, { useState, useEffect, useMemo } from 'react';
import { Loader2, RefreshCw, ExternalLink, Search, Filter, Calendar, MapPin, Building } from 'lucide-react';
import axios from 'axios';

const SavedJobs = () => {
  const [savedJobs, setSavedJobs] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [error, setError] = useState('');
  
  // Advanced search states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedCompany, setSelectedCompany] = useState('all');
  const [selectedDateRange, setSelectedDateRange] = useState('all');
  const [sortBy, setSortBy] = useState('date_saved');
  const [showFilters, setShowFilters] = useState(false);

  const fetchSavedJobs = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('/api/list_saved_jobs');
      setSavedJobs(response.data.saved_jobs || []);
    } catch (err) {
      setError('Failed to load saved jobs.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    setLoadingRecs(true);
    setError('');
    try {
      const response = await axios.get('/api/job_recommendations');
      setRecommendations(response.data.recommended_jobs || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load recommendations.');
    } finally {
      setLoadingRecs(false);
    }
  };

  useEffect(() => {
    fetchSavedJobs();
  }, []);

  // Get unique values for filters
  const locations = useMemo(() => {
    const locs = [...new Set(savedJobs.map(job => job.location).filter(Boolean))];
    return ['all', ...locs];
  }, [savedJobs]);

  const companies = useMemo(() => {
    const comps = [...new Set(savedJobs.map(job => job.company).filter(Boolean))];
    return ['all', ...comps];
  }, [savedJobs]);

  // Filter and search logic for saved jobs
  const filteredSavedJobs = useMemo(() => {
    return savedJobs.filter(job => {
      const matchesSearch = 
        job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.description?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesLocation = selectedLocation === 'all' || job.location === selectedLocation;
      const matchesCompany = selectedCompany === 'all' || job.company === selectedCompany;
      
      // Date range filtering
      let matchesDateRange = true;
      if (selectedDateRange !== 'all' && job.date_saved) {
        const savedDate = new Date(job.date_saved);
        const now = new Date();
        const daysDiff = Math.floor((now - savedDate) / (1000 * 60 * 60 * 24));
        
        switch (selectedDateRange) {
          case 'today':
            matchesDateRange = daysDiff === 0;
            break;
          case 'week':
            matchesDateRange = daysDiff <= 7;
            break;
          case 'month':
            matchesDateRange = daysDiff <= 30;
            break;
          case 'older':
            matchesDateRange = daysDiff > 30;
            break;
        }
      }
      
      return matchesSearch && matchesLocation && matchesCompany && matchesDateRange;
    }).sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'company':
          return (a.company || '').localeCompare(b.company || '');
        case 'location':
          return (a.location || '').localeCompare(b.location || '');
        case 'date_saved':
          return new Date(b.date_saved || 0) - new Date(a.date_saved || 0);
        default:
          return 0;
      }
    });
  }, [savedJobs, searchTerm, selectedLocation, selectedCompany, selectedDateRange, sortBy]);

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedLocation('all');
    setSelectedCompany('all');
    setSelectedDateRange('all');
    setSortBy('date_saved');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Saved Jobs</h1>
        <p className="text-gray-600">Jobs you have saved for later and personalized recommendations.</p>
      </div>

      {/* Advanced Search Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Advanced Search</h2>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            <Filter className="w-4 h-4" />
            <span>{showFilters ? 'Hide' : 'Show'} Filters</span>
          </button>
        </div>

        {/* Search Input */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search jobs by title, company, or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {locations.map(location => (
                  <option key={location} value={location}>
                    {location === 'all' ? 'All Locations' : location}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Company</label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {companies.map(company => (
                  <option key={company} value={company}>
                    {company === 'all' ? 'All Companies' : company}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date Saved</label>
              <select
                value={selectedDateRange}
                onChange={(e) => setSelectedDateRange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="older">Older</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="date_saved">Date Saved</option>
                <option value="title">Job Title</option>
                <option value="company">Company</option>
                <option value="location">Location</option>
              </select>
            </div>
          </div>
        )}

        {/* Search Results Summary */}
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Showing {filteredSavedJobs.length} of {savedJobs.length} saved jobs</span>
          {(searchTerm || selectedLocation !== 'all' || selectedCompany !== 'all' || selectedDateRange !== 'all') && (
            <button
              onClick={clearFilters}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Saved Jobs Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Saved Jobs</h2>
          <button
            onClick={fetchSavedJobs}
            disabled={loading}
            className="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            <span>Refresh</span>
          </button>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center space-x-2 p-6">
            <Loader2 className="w-6 h-6 animate-spin text-linkedin-600" />
            <span className="text-gray-600">Loading saved jobs...</span>
          </div>
        ) : filteredSavedJobs.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {savedJobs.length === 0 ? (
              <p>No saved jobs yet. Use the "Save" button when viewing jobs to save them here.</p>
            ) : (
              <div>
                <p>No jobs match your search criteria.</p>
                <button
                  onClick={clearFilters}
                  className="mt-2 text-blue-600 hover:text-blue-800 underline"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSavedJobs.map((job, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-gray-900 truncate flex-1">{job.title}</h3>
                  <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                </div>
                <div className="space-y-1 mb-3">
                  <p className="text-sm text-gray-600 truncate flex items-center">
                    <Building className="w-3 h-3 mr-1" />
                    {job.company}
                  </p>
                  <p className="text-xs text-gray-500 truncate flex items-center">
                    <MapPin className="w-3 h-3 mr-1" />
                    {job.location}
                  </p>
                  <p className="text-xs text-gray-400 flex items-center">
                    <Calendar className="w-3 h-3 mr-1" />
                    Saved: {formatDate(job.date_saved)}
                  </p>
                </div>
                <a 
                  href={job.job_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-linkedin-600 hover:underline text-xs inline-flex items-center"
                >
                  View Job
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Job Recommendations Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Job Recommendations</h2>
          <button
            onClick={fetchRecommendations}
            disabled={loadingRecs}
            className="flex items-center space-x-2 px-3 py-1 text-sm bg-linkedin-100 text-linkedin-700 rounded hover:bg-linkedin-200 disabled:opacity-50"
          >
            {loadingRecs ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            <span>Get Recommendations</span>
          </button>
        </div>
        
        {loadingRecs ? (
          <div className="flex items-center justify-center space-x-2 p-6">
            <Loader2 className="w-6 h-6 animate-spin text-linkedin-600" />
            <span className="text-gray-600">Loading recommendations...</span>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((job, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="font-medium text-gray-900 truncate">{job.title}</h3>
                <p className="text-sm text-gray-600 truncate">{job.company}</p>
                <p className="text-xs text-gray-500">{job.location}</p>
                <p className="text-xs text-gray-400 mb-2">{job.posted}</p>
                <p className="text-xs text-gray-700 mb-2">{job.descriptionSnippet}</p>
                <a href={job.jobUrl} target="_blank" rel="noopener noreferrer" className="text-linkedin-600 hover:underline text-xs">View Job</a>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">Click "Get Recommendations" to see personalized job suggestions from LinkedIn.</p>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}
    </div>
  );
};

export default SavedJobs; 