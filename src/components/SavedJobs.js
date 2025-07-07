import React, { useState, useEffect } from 'react';
import { Search, XCircle, ArrowUpDown, Bookmark, Building, MapPin, Calendar } from 'lucide-react';
import axios from 'axios';

function SavedJobs() {
  const [savedJobs, setSavedJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('dateSaved');
  const [sortAsc, setSortAsc] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSavedJobs();
  }, []);

  useEffect(() => {
    filterAndSortJobs();
  }, [savedJobs, searchQuery, sortBy, sortAsc]);

  const fetchSavedJobs = async () => {
    try {
      const response = await axios.get('/api/saved_jobs');
      setSavedJobs(response.data.jobs || []);
    } catch (error) {
      console.error('Failed to fetch saved jobs:', error);
      setSavedJobs([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortJobs = () => {
    let filtered = savedJobs.filter(job =>
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.location.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Sort jobs
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'company':
          aValue = a.company.toLowerCase();
          bValue = b.company.toLowerCase();
          break;
        case 'location':
          aValue = a.location.toLowerCase();
          bValue = b.location.toLowerCase();
          break;
        case 'dateSaved':
        default:
          aValue = new Date(a.dateSaved);
          bValue = new Date(b.dateSaved);
          break;
      }

      if (aValue < bValue) return sortAsc ? -1 : 1;
      if (aValue > bValue) return sortAsc ? 1 : -1;
      return 0;
    });

    setFilteredJobs(filtered);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSortBy('dateSaved');
    setSortAsc(false);
  };

  const removeSavedJob = async (jobId) => {
    try {
      await axios.delete(`/api/saved_jobs/${jobId}`);
      setSavedJobs(prev => prev.filter(job => job.id !== jobId));
    } catch (error) {
      console.error('Failed to remove saved job:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="container container-lg">
        <div className="p-xl">
          <div className="card">
            <div className="card-body text-center">
              <p className="text-secondary">Loading saved jobs...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container container-lg">
      <div className="p-xl">
        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-primary flex items-center gap-sm">
              <Bookmark className="w-5 h-5" />
              Saved Jobs
            </h1>
          </div>
          
          <div className="card-body">
            {/* Search and Filters */}
            <div className="flex flex-col md:flex-row md:items-end md:gap-lg mb-lg">
              <div className="flex-1 mb-sm md:mb-0">
                <div className="relative">
                  <Search className="absolute left-md top-1/2 transform -translate-y-1/2 w-5 h-5 text-tertiary" />
                  <input
                    type="text"
                    placeholder="Search saved jobs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="form-input pl-xl"
                  />
                </div>
              </div>
              <div className="flex gap-sm">
                <button onClick={clearFilters} className="btn btn-secondary">
                  <XCircle className="w-4 h-4" />
                  Clear Filters
                </button>
              </div>
            </div>

            {/* Sort Options */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-md mb-lg">
              <button 
                onClick={() => setSortAsc(a => !a)} 
                className="btn btn-secondary flex items-center gap-sm"
              >
                <ArrowUpDown className="w-4 h-4" />
                {sortAsc ? 'Ascending' : 'Descending'}
              </button>
              
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)} 
                className="form-input"
              >
                <option value="dateSaved">Date Saved</option>
                <option value="title">Job Title</option>
                <option value="company">Company</option>
                <option value="location">Location</option>
              </select>
            </div>

            {/* Results Count */}
            <div className="mb-md text-secondary text-sm">
              Found {filteredJobs.length} saved job{filteredJobs.length !== 1 ? 's' : ''}
            </div>

            {/* Jobs List */}
            {filteredJobs.length === 0 ? (
              <div className="text-center py-xl text-tertiary">
                {searchQuery ? 'No saved jobs found matching your criteria.' : 'No saved jobs found.'}
              </div>
            ) : (
              <div className="space-y-md">
                {filteredJobs.map(job => (
                  <div key={job.id} className="card">
                    <div className="card-body">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-lg text-primary mb-xs">{job.title}</div>
                          <div className="text-secondary mb-xs">{job.company} • {job.location}</div>
                          <div className="text-tertiary text-xs">Saved: {job.dateSaved}</div>
                        </div>
                        
                        <div className="flex gap-sm mt-sm md:mt-0">
                          <button 
                            onClick={() => window.open(job.url, '_blank')}
                            className="btn btn-primary btn-sm"
                          >
                            View Job
                          </button>
                          <button 
                            onClick={() => removeSavedJob(job.id)}
                            className="btn btn-error btn-sm"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SavedJobs; 