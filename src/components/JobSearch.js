import React, { useState, useMemo, useEffect } from 'react';
import { Search, Filter, XCircle, ArrowUpDown, LayoutList, LayoutGrid } from 'lucide-react';
import axios from 'axios';

const EXPERIENCE_LEVELS = ['Entry Level', 'Mid Level', 'Senior Level'];
const JOB_TYPES = ['Full-time', 'Part-time', 'Contract'];
const SALARY_RANGES = ['$50k - $80k', '$80k - $120k', '$120k - $160k', '$120k+'];
const allSkills = ['React', 'JavaScript', 'Python', 'Django', 'Node.js'];
const SORT_OPTIONS = [
  { value: 'most_relevant', label: 'Most Relevant' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'date', label: 'Date' },
  { value: 'most_recent', label: 'Most Recent' },
  { value: 'highest_salary', label: 'Highest Salary' },
  { value: 'highest_rated', label: 'Highest Rated' },
];

function JobSearch({ updateSessionStats, sessionStats }) {
  // State for search and filters
  const [searchQuery, setSearchQuery] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [jobType, setJobType] = useState('');
  const [salaryRange, setSalaryRange] = useState('');
  const [skills, setSkills] = useState([]);
  const [sortBy, setSortBy] = useState('relevant');
  const [viewMode, setViewMode] = useState('list');
  const [jobs, setJobs] = useState([]);

  const toggleSkill = skill => {
    setSkills(skills => skills.includes(skill) ? skills.filter(s => s !== skill) : [...skills, skill]);
  };

  useEffect(() => {
    // Fetch jobs from backend
    const fetchJobs = async () => {
      try {
        const response = await axios.get('/api/job_search');
        setJobs(response.data.jobs || []);
      } catch (error) {
        setJobs([]);
      }
    };
    fetchJobs();
  }, []);

  const filteredJobs = useMemo(() => {
    let filtered = jobs;
    if (searchQuery) filtered = filtered.filter(j => j.title.toLowerCase().includes(searchQuery.toLowerCase()) || j.company.toLowerCase().includes(searchQuery.toLowerCase()));
    if (experienceLevel) filtered = filtered.filter(j => j.experienceLevel === experienceLevel);
    if (jobType) filtered = filtered.filter(j => j.jobType === jobType);
    if (salaryRange) filtered = filtered.filter(j => j.salaryRange === salaryRange);
    if (skills.length) filtered = filtered.filter(j => skills.every(skill => j.skills.includes(skill)));
    // Sorting
    if (sortBy === 'newest') filtered = [...filtered].sort((a, b) => new Date(b.datePosted) - new Date(a.datePosted));
    if (sortBy === 'salary') filtered = [...filtered].sort((a, b) => {
      const getSalary = s => parseInt(s.replace(/[^0-9]/g, ''));
      return getSalary(b.salaryRange) - getSalary(a.salaryRange);
    });
    return filtered;
  }, [jobs, searchQuery, experienceLevel, jobType, salaryRange, skills, sortBy]);

  const clearFilters = () => {
    setSearchQuery('');
    setExperienceLevel('');
    setJobType('');
    setSalaryRange('');
    setSkills([]);
    setSortBy('relevant');
  };

  const handleViewJob = (job) => {
    // Called when a job is viewed
    updateSessionStats({ jobs_viewed: (sessionStats.jobs_viewed || 0) + 1 });
    // Optionally, mark job as viewed in backend
  };

  const handleSaveJob = async (job) => {
    try {
      await axios.post('/api/save_job', { job_id: job.id });
      updateSessionStats({ jobs_saved: (sessionStats.jobs_saved || 0) + 1 });
    } catch (error) {}
  };

  const handleApplyJob = async (job) => {
    try {
      await axios.post('/api/apply_job', { job_id: job.id });
      updateSessionStats({ jobs_applied: (sessionStats.jobs_applied || 0) + 1 });
    } catch (error) {}
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Filter className="w-5 h-5 text-blue-500" /> Job Search
        </h1>
        <div className="flex flex-col md:flex-row md:items-end md:space-x-4 mb-6">
          <div className="flex-1 mb-2 md:mb-0">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search for jobs, companies, skills"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
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
          <select value={experienceLevel} onChange={e => setExperienceLevel(e.target.value)} className="col-span-1 p-2 border rounded-lg">
            <option value="">Experience Level</option>
            {EXPERIENCE_LEVELS.map(level => <option key={level} value={level}>{level}</option>)}
          </select>
          <select value={jobType} onChange={e => setJobType(e.target.value)} className="col-span-1 p-2 border rounded-lg">
            <option value="">Job Type</option>
            {JOB_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
          <select value={salaryRange} onChange={e => setSalaryRange(e.target.value)} className="col-span-1 p-2 border rounded-lg">
            <option value="">Salary Range</option>
            {SALARY_RANGES.map(range => <option key={range} value={range}>{range}</option>)}
          </select>
          <div className="col-span-2 flex flex-wrap items-center space-x-2">
            {allSkills.map(skill => (
              <button
                key={skill}
                onClick={() => toggleSkill(skill)}
                className={`px-2 py-1 rounded-lg border ${skills.includes(skill) ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                {skill}
              </button>
            ))}
          </div>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="col-span-1 p-2 border rounded-lg">
            {SORT_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
          </select>
          <div className="col-span-1 flex items-center space-x-2">
            <button onClick={() => setViewMode('list')} className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'}`}><LayoutList className="w-4 h-4" /></button>
            <button onClick={() => setViewMode('grid')} className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'}`}><LayoutGrid className="w-4 h-4" /></button>
          </div>
        </div>
        <div className="mb-4 text-gray-600 text-sm">
          Results: {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
        </div>
        <div>
          {filteredJobs.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No jobs found matching your criteria.</div>
          ) : (
            <ul className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : 'divide-y divide-gray-200'}>
              {filteredJobs.map(job => (
                <li key={job.id} onClick={() => handleViewJob(job)} className={viewMode === 'grid' ? 'p-4 border rounded-lg bg-gray-50' : 'py-4 flex flex-col md:flex-row md:items-center md:justify-between'}>
                  <div>
                    <div className="font-semibold text-lg text-gray-800">{job.title}</div>
                    <div className="text-gray-600">{job.company} &middot; {job.location}</div>
                    <div className="text-gray-500 text-sm">Experience: {job.experienceLevel} | Type: {job.jobType} | Salary: {job.salaryRange}</div>
                    <div className="text-gray-400 text-xs">Skills: {job.skills.join(', ')}</div>
                  </div>
                  <div className="text-gray-400 text-sm mt-2 md:mt-0">Posted: {job.datePosted}</div>
                  <div className="flex space-x-2 mt-2 md:mt-0">
                    <button onClick={e => { e.stopPropagation(); handleSaveJob(job); }} className="px-2 py-1 bg-blue-100 text-blue-700 rounded">Save</button>
                    <button onClick={e => { e.stopPropagation(); handleApplyJob(job); }} className="px-2 py-1 bg-green-100 text-green-700 rounded">Apply</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default JobSearch; 