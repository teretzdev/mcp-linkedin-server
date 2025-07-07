import React, { useState } from 'react';
import { Search, Building, MapPin, User } from 'lucide-react';
import axios from 'axios';

function ProfileSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await axios.post('/api/search_profiles', {
        query: searchQuery
      });
      setSearchResults(response.data.profiles || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="container container-lg">
      <div className="p-xl">
        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-primary">Profile Search</h1>
            <p className="text-secondary">
              Search for LinkedIn profiles to connect with professionals in your industry
            </p>
          </div>
          
          <div className="card-body">
            {/* Search Form */}
            <div className="card mb-lg">
              <div className="card-body">
                <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-md">
                  <div className="flex-1">
                    <label className="form-label">Search Query</label>
                    <div className="relative">
                      <Search className="absolute left-md top-1/2 transform -translate-y-1/2 w-5 h-5 text-tertiary" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="e.g., Software Engineer at Google, Marketing Manager"
                        className="form-input pl-xl"
                      />
                    </div>
                  </div>
                  <div className="flex items-end">
                    <button
                      type="submit"
                      disabled={isSearching || !searchQuery.trim()}
                      className="btn btn-primary"
                    >
                      {isSearching ? 'Searching...' : 'Search Profiles'}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-primary">
                    Search Results ({searchResults.length})
                  </h2>
                </div>
                <div className="card-body">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
                    {searchResults.map((profile, index) => (
                      <div key={index} className="card">
                        <div className="card-body">
                          <div className="flex items-start gap-md">
                            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                              {profile.name?.charAt(0) || 'U'}
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium text-primary truncate">
                                {profile.name || 'Unknown Name'}
                              </h3>
                              <p className="text-sm text-secondary truncate">
                                {profile.headline || 'No headline'}
                              </p>
                              <div className="flex items-center gap-sm mt-xs">
                                <Building className="w-3 h-3 text-tertiary" />
                                <span className="text-xs text-tertiary truncate">
                                  {profile.company || 'No company'}
                                </span>
                              </div>
                              <div className="flex items-center gap-sm mt-xs">
                                <MapPin className="w-3 h-3 text-tertiary" />
                                <span className="text-xs text-tertiary truncate">
                                  {profile.location || 'No location'}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-sm mt-md">
                            <button className="btn btn-primary btn-sm flex-1">
                              Connect
                            </button>
                            <button className="btn btn-secondary btn-sm">
                              View Profile
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Loading State */}
            {isSearching && (
              <div className="card">
                <div className="card-body text-center py-xl">
                  <span className="text-secondary">Searching LinkedIn profiles...</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfileSearch; 