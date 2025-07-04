import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, MapPin, Building, Clock, DollarSign, Star, Bookmark, Send, Eye, X, TrendingUp, Users } from 'lucide-react';
import axios from 'axios';

const JobSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    experienceLevel: '',
    jobType: '',
    salaryRange: '',
    remote: false,
    easyApply: false,
    company: '',
    skills: []
  });
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('relevance');
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  // Sample job data with more details
  const sampleJobs = [
    {
      id: 1,
      title: 'Senior React Developer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      type: 'Full-time',
      salary: '$120,000 - $150,000',
      salaryMin: 120000,
      salaryMax: 150000,
      experience: '5+ years',
      posted: '2 days ago',
      description: 'We are looking for a Senior React Developer to join our team and help build scalable web applications. You will work with modern technologies and collaborate with cross-functional teams.',
      easyApply: true,
      remote: true,
      skills: ['React', 'JavaScript', 'TypeScript', 'Node.js', 'Redux'],
      logo: 'https://via.placeholder.com/50',
      companySize: '500-1000',
      industry: 'Technology',
      rating: 4.2,
      applicants: 45
    },
    {
      id: 2,
      title: 'Frontend Engineer',
      company: 'StartupXYZ',
      location: 'Remote',
      type: 'Full-time',
      salary: '$100,000 - $130,000',
      salaryMin: 100000,
      salaryMax: 130000,
      experience: '3+ years',
      posted: '1 week ago',
      description: 'Join our fast-growing startup as a Frontend Engineer. You will be responsible for building user interfaces and ensuring great user experience across our platform.',
      easyApply: true,
      remote: true,
      skills: ['React', 'Vue.js', 'CSS', 'HTML', 'JavaScript'],
      logo: 'https://via.placeholder.com/50',
      companySize: '50-200',
      industry: 'SaaS',
      rating: 4.5,
      applicants: 23
    },
    {
      id: 3,
      title: 'Full Stack Developer',
      company: 'Enterprise Solutions',
      location: 'New York, NY',
      type: 'Full-time',
      salary: '$130,000 - $160,000',
      salaryMin: 130000,
      salaryMax: 160000,
      experience: '7+ years',
      posted: '3 days ago',
      description: 'We need a Full Stack Developer with strong backend skills to help us build robust enterprise applications. Experience with cloud platforms and microservices is a plus.',
      easyApply: false,
      remote: false,
      skills: ['React', 'Node.js', 'Python', 'PostgreSQL', 'AWS'],
      logo: 'https://via.placeholder.com/50',
      companySize: '1000+',
      industry: 'Enterprise Software',
      rating: 3.8,
      applicants: 67
    },
    {
      id: 4,
      title: 'UI/UX Developer',
      company: 'Design Studio Pro',
      location: 'Los Angeles, CA',
      type: 'Contract',
      salary: '$80,000 - $110,000',
      salaryMin: 80000,
      salaryMax: 110000,
      experience: '2+ years',
      posted: '5 days ago',
      description: 'Creative UI/UX Developer needed to create beautiful and functional user interfaces. Strong design sense and frontend development skills required.',
      easyApply: true,
      remote: false,
      skills: ['React', 'CSS', 'Figma', 'Adobe Creative Suite', 'JavaScript'],
      logo: 'https://via.placeholder.com/50',
      companySize: '10-50',
      industry: 'Design',
      rating: 4.7,
      applicants: 12
    }
  ];

  useEffect(() => {
    setJobs(sampleJobs);
    setFilteredJobs(sampleJobs);
  }, []);

  useEffect(() => {
    applyFilters();
  }, [jobs, filters, searchQuery, location, sortBy]);

  // Get unique values for filters
  const companies = useMemo(() => {
    const comps = [...new Set(jobs.map(job => job.company))];
    return ['', ...comps];
  }, [jobs]);

  const allSkills = useMemo(() => {
    const skillSet = new Set();
    jobs.forEach(job => job.skills.forEach(skill => skillSet.add(skill)));
    return Array.from(skillSet);
  }, [jobs]);

  const applyFilters = () => {
    let filtered = [...jobs];

    // Search query filter
    if (searchQuery) {
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Location filter
    if (location) {
      filtered = filtered.filter(job =>
        job.location.toLowerCase().includes(location.toLowerCase())
      );
    }

    // Experience level filter
    if (filters.experienceLevel) {
      filtered = filtered.filter(job => job.experience.includes(filters.experienceLevel));
    }

    // Job type filter
    if (filters.jobType) {
      filtered = filtered.filter(job => job.type === filters.jobType);
    }

    // Company filter
    if (filters.company) {
      filtered = filtered.filter(job => job.company === filters.company);
    }

    // Skills filter
    if (filters.skills.length > 0) {
      filtered = filtered.filter(job =>
        filters.skills.some(skill => job.skills.includes(skill))
      );
    }

    // Salary range filter
    if (filters.salaryRange) {
      const [min, max] = filters.salaryRange.split('-').map(Number);
      filtered = filtered.filter(job => 
        job.salaryMin >= min && job.salaryMax <= max
      );
    }

    // Remote filter
    if (filters.remote) {
      filtered = filtered.filter(job => job.remote);
    }

    // Easy Apply filter
    if (filters.easyApply) {
      filtered = filtered.filter(job => job.easyApply);
    }

    // Sort results
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'relevance':
          return 0; // Keep original order for relevance
        case 'salary':
          return b.salaryMin - a.salaryMin;
        case 'date':
          return new Date(a.posted) - new Date(b.posted);
        case 'rating':
          return b.rating - a.rating;
        case 'applicants':
          return a.applicants - b.applicants; // Fewer applicants = less competition
        default:
          return 0;
      }
    });

    setFilteredJobs(filtered);
  };

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      // Use enhanced job search API
      const response = await axios.post('/api/search_jobs_enhanced', {
        query: searchQuery,
        location: location,
        filters: filters,
        count: 20
      });
      
      if (response.data.status === 'success') {
        setJobs(response.data.jobs);
        setFilteredJobs(response.data.jobs);
      } else {
        throw new Error(response.data.message || 'Search failed');
      }
    } catch (error) {
      console.error('Search failed:', error);
      // Fallback to sample data for demo
      setJobs(sampleJobs);
      setFilteredJobs(sampleJobs);
    } finally {
      setIsLoading(false);
    }
  };

  const saveJob = async (jobId) => {
    try {
      const job = jobs.find(j => j.id === jobId);
      if (!job) return;
      
      // Use enhanced save job API
      const response = await axios.post('/api/save_job_enhanced', {
        job_url: job.jobUrl || `https://linkedin.com/jobs/view/${jobId}`
      });
      
      if (response.data.status === 'success') {
        // Toggle saved status locally
        setJobs(jobs.map(j => 
          j.id === jobId ? { ...j, saved: !j.saved } : j
        ));
      }
    } catch (error) {
      console.error('Failed to save job:', error);
      // Fallback to local toggle
      setJobs(jobs.map(j => 
        j.id === jobId ? { ...j, saved: !j.saved } : j
      ));
    }
  };

  const applyToJob = (job) => {
    if (job.easyApply) {
      // Navigate to Easy Apply Assistant
      window.location.href = `/easy-apply?jobId=${job.id}`;
    } else {
      // Open job in new tab
      window.open(`https://linkedin.com/jobs/view/${job.id}`, '_blank');
    }
  };

  const toggleSkill = (skill) => {
    setFilters(prev => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter(s => s !== skill)
        : [...prev.skills, skill]
    }));
  };

  const clearFilters = () => {
    setFilters({
      experienceLevel: '',
      jobType: '',
      salaryRange: '',
      remote: false,
      easyApply: false,
      company: '',
      skills: []
    });
    setSearchQuery('');
    setLocation('');
    setSortBy('relevance');
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">Job Search</h1>
          
          {/* Search Bar */}
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for jobs, companies, skills, or keywords..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="flex-1">
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="City, state, or remote"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <button
              onClick={handleSearch}
              disabled={isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Search className="w-5 h-5 mr-2" />
                  Search Jobs
                </>
              )}
            </button>
          </div>

          {/* Advanced Filters Toggle and Results Summary */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                <Filter className="w-4 h-4 mr-2" />
                Advanced Filters
              </button>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
                >
                  <div className="w-4 h-4 grid grid-cols-2 gap-0.5">
                    <div className="bg-current rounded-sm"></div>
                    <div className="bg-current rounded-sm"></div>
                    <div className="bg-current rounded-sm"></div>
                    <div className="bg-current rounded-sm"></div>
                  </div>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
                >
                  <div className="w-4 h-4 space-y-1">
                    <div className="bg-current rounded-sm h-0.5"></div>
                    <div className="bg-current rounded-sm h-0.5"></div>
                    <div className="bg-current rounded-sm h-0.5"></div>
                  </div>
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="relevance">Most Relevant</option>
                <option value="date">Most Recent</option>
                <option value="salary">Highest Salary</option>
                <option value="rating">Highest Rated</option>
                <option value="applicants">Least Competition</option>
              </select>
              <p className="text-sm text-gray-600">
                {filteredJobs.length} jobs found
              </p>
            </div>
          </div>

          {/* Advanced Filters Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level
                  </label>
                  <select
                    value={filters.experienceLevel}
                    onChange={(e) => setFilters({...filters, experienceLevel: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Any Experience</option>
                    <option value="Entry">Entry Level</option>
                    <option value="Mid">Mid Level</option>
                    <option value="Senior">Senior Level</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Type
                  </label>
                  <select
                    value={filters.jobType}
                    onChange={(e) => setFilters({...filters, jobType: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Any Type</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company
                  </label>
                  <select
                    value={filters.company}
                    onChange={(e) => setFilters({...filters, company: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {companies.map(company => (
                      <option key={company} value={company}>
                        {company || 'Any Company'}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Salary Range
                  </label>
                  <select
                    value={filters.salaryRange}
                    onChange={(e) => setFilters({...filters, salaryRange: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Any Salary</option>
                    <option value="50000-80000">$50k - $80k</option>
                    <option value="80000-120000">$80k - $120k</option>
                    <option value="120000-160000">$120k - $160k</option>
                    <option value="160000-200000">$160k+</option>
                  </select>
                </div>
              </div>

              {/* Skills Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skills
                </label>
                <div className="flex flex-wrap gap-2">
                  {allSkills.map(skill => (
                    <button
                      key={skill}
                      onClick={() => toggleSkill(skill)}
                      className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                        filters.skills.includes(skill)
                          ? 'bg-blue-100 border-blue-300 text-blue-700'
                          : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {skill}
                    </button>
                  ))}
                </div>
              </div>

              {/* Checkboxes */}
              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.remote}
                    onChange={(e) => setFilters({...filters, remote: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Remote Only</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.easyApply}
                    onChange={(e) => setFilters({...filters, easyApply: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Easy Apply</span>
                </label>
                <button
                  onClick={clearFilters}
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Job Results */}
        <div className={`space-y-4 ${viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : ''}`}>
          {filteredJobs.map((job) => (
            <div key={job.id} className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <img src={job.logo} alt={job.company} className="w-12 h-12 rounded-lg" />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-xl font-semibold text-gray-800">{job.title}</h3>
                      {job.easyApply && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          Easy Apply
                        </span>
                      )}
                      {job.remote && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          Remote
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-gray-600 mb-3">
                      <div className="flex items-center">
                        <Building className="w-4 h-4 mr-1" />
                        <span>{job.company}</span>
                      </div>
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span>{job.location}</span>
                      </div>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        <span>{job.posted}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-gray-600 mb-3">
                      <div className="flex items-center">
                        <DollarSign className="w-4 h-4 mr-1" />
                        <span>{job.salary}</span>
                      </div>
                      <span>•</span>
                      <span>{job.experience}</span>
                      <span>•</span>
                      <span>{job.type}</span>
                    </div>

                    <p className="text-gray-700 mb-4 line-clamp-2">{job.description}</p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills.map((skill, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>

                    {/* Additional job details */}
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                      <div className="flex items-center">
                        <Star className="w-4 h-4 mr-1" />
                        <span>{job.rating}</span>
                      </div>
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        <span>{job.applicants} applicants</span>
                      </div>
                      <div className="flex items-center">
                        <TrendingUp className="w-4 h-4 mr-1" />
                        <span>{job.companySize}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <button
                    onClick={() => saveJob(job.id)}
                    className={`p-2 rounded-lg border transition-colors ${
                      job.saved
                        ? 'bg-blue-50 border-blue-200 text-blue-600'
                        : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Bookmark className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => applyToJob(job)}
                    className={`p-2 rounded-lg border transition-colors ${
                      job.easyApply
                        ? 'bg-green-50 border-green-200 text-green-600 hover:bg-green-100'
                        : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {job.easyApply ? <Send className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => applyToJob(job)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      job.easyApply
                        ? 'bg-green-600 text-white hover:bg-green-700'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {job.easyApply ? 'Easy Apply' : 'View Job'}
                  </button>
                  <button 
                    onClick={() => saveJob(job.id)}
                    className={`px-4 py-2 border rounded-lg transition-colors ${
                      job.saved
                        ? 'border-blue-300 text-blue-600 bg-blue-50'
                        : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {job.saved ? 'Saved' : 'Save Job'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredJobs.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <Search className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">No jobs found</h3>
            <p className="text-gray-500 mb-4">Try adjusting your search criteria or filters</p>
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Clear All Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobSearch; 