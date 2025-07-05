import React from 'react';
import { Filter, MapPin } from 'lucide-react';

const JobFilters = ({ filters, setFilters, companies, allSkills, showFilters, setShowFilters, clearFilters, sortBy, setSortBy, searchQuery, setSearchQuery, location, setLocation, toggleSkill }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="flex flex-col md:flex-row gap-4 mb-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search for jobs, companies, skills, or keywords..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex-1">
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={location}
              onChange={e => setLocation(e.target.value)}
              placeholder="Location (e.g. Remote, San Francisco)"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <Filter className="w-4 h-4 mr-2" />
          Filters
        </button>
      </div>
      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
            <select
              value={filters.experienceLevel}
              onChange={e => setFilters({ ...filters, experienceLevel: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Any Experience</option>
              <option value="Entry">Entry Level</option>
              <option value="Mid">Mid Level</option>
              <option value="Senior">Senior Level</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Job Type</label>
            <select
              value={filters.jobType}
              onChange={e => setFilters({ ...filters, jobType: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Any Type</option>
              <option value="Full-time">Full-time</option>
              <option value="Part-time">Part-time</option>
              <option value="Contract">Contract</option>
              <option value="Internship">Internship</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Company</label>
            <select
              value={filters.company}
              onChange={e => setFilters({ ...filters, company: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              {companies.map(company => (
                <option key={company} value={company}>{company || 'Any Company'}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Salary Range</label>
            <select
              value={filters.salaryRange}
              onChange={e => setFilters({ ...filters, salaryRange: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Any Salary</option>
              <option value="50000-80000">$50k - $80k</option>
              <option value="80000-120000">$80k - $120k</option>
              <option value="120000-160000">$120k - $160k</option>
              <option value="160000-200000">$160k+</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Skills</label>
            <div className="flex flex-wrap gap-2">
              {allSkills.map(skill => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => toggleSkill(skill)}
                  className={`px-3 py-1 rounded-full text-sm border transition-colors ${filters.skills.includes(skill) ? 'bg-blue-100 border-blue-300 text-blue-700' : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'}`}
                >
                  {skill}
                </button>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Other Filters</label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.remote}
                onChange={e => setFilters({ ...filters, remote: e.target.checked })}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Remote Only</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.easyApply}
                onChange={e => setFilters({ ...filters, easyApply: e.target.checked })}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Easy Apply</span>
            </label>
          </div>
        </div>
      )}
      <div className="flex items-center gap-4 mt-4">
        <label className="block text-sm font-medium text-gray-700">Sort By:</label>
        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="relevance">Relevance</option>
          <option value="salary">Salary</option>
          <option value="date">Date Posted</option>
          <option value="rating">Rating</option>
          <option value="applicants">Applicants</option>
        </select>
        <button onClick={clearFilters} className="ml-auto text-blue-600 hover:text-blue-800 text-sm underline">Clear All Filters</button>
      </div>
    </div>
  );
};

export default JobFilters; 