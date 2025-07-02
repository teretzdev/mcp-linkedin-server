import React, { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

const Applications = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAppliedJobs = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await axios.get('/api/list_applied_jobs');
        setJobs(response.data.applied_jobs || []);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load applied jobs.');
      } finally {
        setLoading(false);
      }
    };
    fetchAppliedJobs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Applications</h1>
        <p className="text-gray-600">Jobs you have applied to using this tool.</p>
      </div>
      {loading ? (
        <div className="flex items-center justify-center space-x-2 p-6">
          <Loader2 className="w-6 h-6 animate-spin text-linkedin-600" />
          <span className="text-gray-600">Loading applied jobs...</span>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Applied Jobs ({jobs.length})</h2>
          {jobs.length === 0 ? (
            <p className="text-gray-500">No jobs applied yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {jobs.map((job, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h3 className="font-medium text-gray-900 truncate">{job.title || 'Job'}</h3>
                  <p className="text-sm text-gray-600 truncate">{job.company || ''}</p>
                  <p className="text-xs text-gray-500">{job.location || ''}</p>
                  <p className="text-xs text-gray-400 mb-2">{job.date_applied || ''}</p>
                  <a href={job.jobUrl} target="_blank" rel="noopener noreferrer" className="text-linkedin-600 hover:underline text-xs">View</a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Applications; 