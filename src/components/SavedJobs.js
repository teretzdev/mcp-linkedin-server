import React, { useState, useMemo, useEffect } from 'react';
import { Search, Filter, Calendar, XCircle, ArrowUpDown, Building2, MapPin, Clock, Bell, FileText } from 'lucide-react';
import axios from 'axios';

const SORT_OPTIONS = [
  { value: 'date', label: 'Date Saved' },
  { value: 'title', label: 'Job Title' },
  { value: 'company', label: 'Company' },
];

function SavedJobs({ updateSessionStats, sessionStats }) {
  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedDateRange, setSelectedDateRange] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [sortAsc, setSortAsc] = useState(false);
  const [jobs, setJobs] = useState([]);

  // Unique locations and companies for filter dropdowns
  const locations = useMemo(() => Array.from(new Set(jobs.map(j => j.location))), [jobs]);
  const companies = useMemo(() => Array.from(new Set(jobs.map(j => j.company))), [jobs]);

  // Filtering logic
  const filteredJobs = useMemo(() => {
    let filtered = jobs.filter(job => {
      const matchesSearch =
        !searchTerm ||
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesLocation = !selectedLocation || job.location === selectedLocation;
      const matchesCompany = !selectedCompany || job.company === selectedCompany;
      const matchesDateRange = !selectedDateRange || (() => {
        const now = new Date();
        const jobDate = new Date(job.dateSaved);
        if (selectedDateRange === 'today') {
          return now.toDateString() === jobDate.toDateString();
        } else if (selectedDateRange === 'thisweek') {
          const startOfWeek = new Date(now);
          startOfWeek.setDate(now.getDate() - now.getDay());
          return jobDate >= startOfWeek && jobDate <= now;
        } else if (selectedDateRange === 'last7') {
          return (now - jobDate) / (1000 * 60 * 60 * 24) <= 7;
        } else if (selectedDateRange === 'last30') {
          return (now - jobDate) / (1000 * 60 * 60 * 24) <= 30;
        }
        return true;
      })();
      return matchesSearch && matchesLocation && matchesCompany && matchesDateRange;
    });
    // Sorting
    filtered = filtered.sort((a, b) => {
      if (sortBy === 'date') {
        return sortAsc
          ? new Date(a.dateSaved) - new Date(b.dateSaved)
          : new Date(b.dateSaved) - new Date(a.dateSaved);
      } else if (sortBy === 'title') {
        return sortAsc
          ? a.title.localeCompare(b.title)
          : b.title.localeCompare(a.title);
      } else if (sortBy === 'company') {
        return sortAsc
          ? a.company.localeCompare(b.company)
          : b.company.localeCompare(a.company);
      }
      return 0;
    });
    return filtered;
  }, [jobs, searchTerm, selectedLocation, selectedCompany, selectedDateRange, sortBy, sortAsc]);

  useEffect(() => {
    // Fetch saved jobs from backend
    const fetchJobs = async () => {
      try {
        const response = await axios.get('/api/saved_jobs');
        setJobs(response.data.saved_jobs || []);
      } catch (error) {
        setJobs([]);
      }
    };
    fetchJobs();
  }, []);

  const handleViewJob = (job) => {
    updateSessionStats({ jobs_viewed: (sessionStats.jobs_viewed || 0) + 1 });
  };

  const handleRemoveSavedJob = async (job) => {
    try {
      await axios.post('/api/remove_saved_job', { job_id: job.id });
      setJobs(jobs => jobs.filter(j => j.id !== job.id));
      updateSessionStats({ jobs_saved: Math.max((sessionStats.jobs_saved || 1) - 1, 0) });
    } catch (error) {}
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedLocation('');
    setSelectedCompany('');
    setSelectedDateRange('');
    setSortBy('date');
    setSortAsc(false);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <div className="flex flex-col md:flex-row md:items-end md:space-x-4 mb-6">
        <div className="flex-1 mb-2 md:mb-0">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search jobs by title"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="search-input"
            />
          </div>
        </div>
        <div className="flex space-x-2">
          <button onClick={clearFilters} className="flex items-center px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
            <XCircle className="w-4 h-4 mr-1" />
            Clear Filters
          </button>
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
        <select value={selectedLocation} onChange={e => setSelectedLocation(e.target.value)} className="col-span-1 p-2 border rounded-lg">
          <option value="">All Locations</option>
          <option value="Remote">Remote</option>
          <option value="San Francisco">San Francisco</option>
        </select>
        <select value={selectedCompany} onChange={e => setSelectedCompany(e.target.value)} className="col-span-1 p-2 border rounded-lg">
          <option value="">All Companies</option>
          <option value="Company A">Company A</option>
          <option value="Company B">Company B</option>
          <option value="Company C">Company C</option>
        </select>
        <select value={selectedDateRange} onChange={e => setSelectedDateRange(e.target.value)} className="col-span-1 p-2 border rounded-lg">
          <option value="">All Time</option>
          <option value="today">Today</option>
          <option value="thisweek">This Week</option>
          <option value="last7">Last 7 days</option>
          <option value="last30">Last 30 days</option>
        </select>
        <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="col-span-1 p-2 border rounded-lg">
          {SORT_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
        </select>
        <button onClick={() => setSortAsc(a => !a)} className="col-span-1 flex items-center px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
          <ArrowUpDown className="w-4 h-4 mr-1" />
          {sortAsc ? 'Asc' : 'Desc'}
        </button>
      </div>
      <div className="mb-4 text-gray-600 text-sm">
        Results: {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
      </div>
      <div>
        {filteredJobs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">No saved jobs found matching your criteria.</div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {filteredJobs.map(job => (
              <li key={job.id} onClick={() => handleViewJob(job)} className="py-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <div>
                    <div className="font-semibold text-lg text-gray-800">{job.title}</div>
                    <div className="text-gray-600">{job.company} &middot; {job.location}</div>
                    <div className="text-gray-400 text-xs">Saved: {job.dateSaved}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2 mt-2 md:mt-0">
                  <button onClick={e => { e.stopPropagation(); handleRemoveSavedJob(job); }} className="px-2 py-1 bg-red-100 text-red-700 rounded">Remove</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default SavedJobs; 