import React, { useState, useEffect } from 'react';
import { Search, Save, CheckCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const JobSearch = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [count, setCount] = useState(10);
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // Check for quick search data from dashboard
    const quickSearch = localStorage.getItem('quickSearch');
    if (quickSearch) {
      try {
        const searchData = JSON.parse(quickSearch);
        setQuery(searchData.query || '');
        setLocation(searchData.location || '');
        setCount(searchData.count || 10);
        localStorage.removeItem('quickSearch'); // Clear after use
      } catch (error) {
        console.log('Error parsing quick search data:', error);
      }
    }
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    setJobs([]);
    
    // Save search to recent searches
    const searchKey = `${query}${location ? ` in ${location}` : ''}`;
    const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    if (!recentSearches.includes(searchKey)) {
      recentSearches.unshift(searchKey);
      localStorage.setItem('recentSearches', JSON.stringify(recentSearches.slice(0, 5)));
    }
    
    try {
      const response = await axios.post('/api/search_jobs', {
        query: query.trim(),
        location: location.trim(),
        count: parseInt(count)
      });
      setJobs(response.data.jobs || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Job search failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (jobUrl) => {
    setSuccess('');
    setError('');
    try {
      const response = await axios.post('/api/apply_job', { job_url: jobUrl });
      setSuccess(response.data.message || 'Applied!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Apply failed.');
    }
  };

  const handleSave = async (jobUrl) => {
    setSuccess('');
    setError('');
    try {
      const response = await axios.post('/api/save_job', { job_url: jobUrl });
      setSuccess(response.data.message || 'Saved!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Job Search</h1>
        <p className="text-gray-600">Search for jobs on LinkedIn and apply or save them directly.</p>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Job Title / Keywords</label>
              <input type="text" value={query} onChange={e => setQuery(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <input type="text" value={location} onChange={e => setLocation(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Number of Jobs</label>
              <select value={count} onChange={e => setCount(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </div>
          </div>
          <button type="submit" disabled={loading || !query.trim()} className="mt-4 flex items-center space-x-2 px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            <span>{loading ? 'Searching...' : 'Search Jobs'}</span>
          </button>
        </form>
      </div>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4"><p className="text-red-800">{error}</p></div>}
      {success && <div className="bg-green-50 border border-green-200 rounded-lg p-4"><p className="text-green-800">{success}</p></div>}
      {jobs.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Results ({jobs.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((job, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="font-medium text-gray-900 truncate">{job.title}</h3>
                <p className="text-sm text-gray-600 truncate">{job.company}</p>
                <p className="text-xs text-gray-500">{job.location}</p>
                <p className="text-xs text-gray-400 mb-2">{job.posted}</p>
                <p className="text-xs text-gray-700 mb-2">{job.descriptionSnippet}</p>
                <div className="flex space-x-2 mt-2">
                  <button onClick={() => handleApply(job.jobUrl)} className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs">
                    <CheckCircle className="w-4 h-4" /> <span>Apply</span>
                  </button>
                  <button onClick={() => handleSave(job.jobUrl)} className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs">
                    <Save className="w-4 h-4" /> <span>Save</span>
                  </button>
                  <a href={job.jobUrl} target="_blank" rel="noopener noreferrer" className="ml-auto text-linkedin-600 hover:underline text-xs">View</a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {/* Recent Searches */}
      {(() => {
        const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
        if (recentSearches.length > 0) {
          return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Searches</h3>
              <div className="flex flex-wrap gap-2">
                {recentSearches.map((search, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      // Parse search and fill form
                      const parts = search.split(' in ');
                      setQuery(parts[0]);
                      setLocation(parts[1] || '');
                    }}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                  >
                    {search}
                  </button>
                ))}
              </div>
            </div>
          );
        }
        return null;
      })()}
    </div>
  );
};

export default JobSearch; 