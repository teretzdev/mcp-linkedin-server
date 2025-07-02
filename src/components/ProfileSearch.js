import React, { useState } from 'react';
import { Search, User, MapPin, Building, Mail, ExternalLink, Loader2 } from 'lucide-react';
import axios from 'axios';

const ProfileSearch = () => {
  const [query, setQuery] = useState('');
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await axios.post('/api/search_linkedin_profiles', {
        query: query.trim(),
        count: parseInt(count)
      });
      setResults(response.data.profiles || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Profile Search</h1>
        <p className="text-gray-600">
          Search for LinkedIn profiles based on keywords, job titles, or company names
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Query
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., software engineer, marketing manager, Google"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Results
              </label>
              <select
                value={count}
                onChange={(e) => setCount(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-linkedin-500"
              >
                <option value={5}>5 profiles</option>
                <option value={10}>10 profiles</option>
                <option value={15}>15 profiles</option>
                <option value={20}>20 profiles</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Search className="w-5 h-5" />
                )}
                <span>{loading ? 'Searching...' : 'Search Profiles'}</span>
              </button>
            </div>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Search Results ({results.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((profile, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start space-x-3">
                  <div className="w-12 h-12 bg-linkedin-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-6 h-6 text-linkedin-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">
                      {profile.name || 'Unknown Name'}
                    </h3>
                    <p className="text-sm text-gray-600 truncate">
                      {profile.title || 'No title available'}
                    </p>
                    {profile.company && (
                      <div className="flex items-center space-x-1 mt-1">
                        <Building className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-500 truncate">
                          {profile.company}
                        </span>
                      </div>
                    )}
                    {profile.location && (
                      <div className="flex items-center space-x-1 mt-1">
                        <MapPin className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-500 truncate">
                          {profile.location}
                        </span>
                      </div>
                    )}
                    {profile.url && (
                      <a
                        href={profile.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 mt-2 text-xs text-linkedin-600 hover:text-linkedin-700"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>View Profile</span>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-6 h-6 animate-spin text-linkedin-600" />
            <span className="text-gray-600">Searching LinkedIn profiles...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileSearch; 