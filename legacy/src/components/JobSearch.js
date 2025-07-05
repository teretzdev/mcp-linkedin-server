import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, MapPin, Building, Clock, DollarSign, Star, Bookmark, Send, Eye, X, TrendingUp, Users } from 'lucide-react';
import axios from 'axios';
import JobFilters from './JobFilters';
import JobList from './JobList';
import { filterJobs, sortJobs } from './JobSearchUtils';

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
    let filtered = filterJobs(jobs, filters, searchQuery, location);
    filtered = sortJobs(filtered, sortBy);
    setFilteredJobs(filtered);
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
        <JobFilters
          filters={filters}
          setFilters={setFilters}
          companies={companies}
          allSkills={allSkills}
          showFilters={showFilters}
          setShowFilters={setShowFilters}
          clearFilters={clearFilters}
          sortBy={sortBy}
          setSortBy={setSortBy}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          location={location}
          setLocation={setLocation}
          toggleSkill={toggleSkill}
        />
        <JobList
          jobs={filteredJobs}
          saveJob={saveJob}
          applyToJob={applyToJob}
          isLoading={isLoading}
          viewMode={viewMode}
        />
      </div>
    </div>
  );
};

export default JobSearch; 