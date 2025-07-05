import React from 'react';
import JobCard from './JobCard';

const JobList = ({ jobs, saveJob, applyToJob, isLoading, viewMode }) => {
  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Loading jobs...</div>;
  }
  if (!jobs.length) {
    return <div className="text-center py-8 text-gray-500">No jobs found matching your criteria.</div>;
  }
  return (
    <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
      {jobs.map(job => (
        <JobCard key={job.id} job={job} saveJob={saveJob} applyToJob={applyToJob} />
      ))}
    </div>
  );
};

export default JobList; 