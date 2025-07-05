// Utility functions for job filtering and sorting

export function filterJobs(jobs, filters, searchQuery, location) {
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

  return filtered;
}

export function sortJobs(jobs, sortBy) {
  const sorted = [...jobs];
  sorted.sort((a, b) => {
    switch (sortBy) {
      case 'relevance':
        return 0; // Keep original order for relevance
      case 'salary':
        return b.salaryMin - a.salaryMin;
      case 'date':
        // Assume posted is a string like '2 days ago', fallback to 0
        return 0;
      case 'rating':
        return b.rating - a.rating;
      case 'applicants':
        return a.applicants - b.applicants; // Fewer applicants = less competition
      default:
        return 0;
    }
  });
  return sorted;
} 