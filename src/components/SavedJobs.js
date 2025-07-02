import React, { useState, useEffect } from 'react';
import { Loader2, RefreshCw, ExternalLink } from 'lucide-react';
import axios from 'axios';

const SavedJobs = () => {
  const [savedJobs, setSavedJobs] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [error, setError] = useState('');

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

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Saved Jobs</h1>
        <p className="text-gray-600">Jobs you have saved for later and personalized recommendations.</p>
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
        ) : savedJobs.length === 0 ? (
          <p className="text-gray-500">No saved jobs yet. Use the "Save" button when viewing jobs to save them here.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {savedJobs.map((job, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="font-medium text-gray-900 truncate">{job.title}</h3>
                <p className="text-sm text-gray-600 truncate">{job.company}</p>
                <p className="text-xs text-gray-500">{job.location}</p>
                <p className="text-xs text-gray-400 mb-2">{job.date_saved}</p>
                <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="text-linkedin-600 hover:underline text-xs">View</a>
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