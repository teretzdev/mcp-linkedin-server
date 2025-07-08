import React from 'react';
import ApplicationCard from './ApplicationCard';

const ApplicationsList = ({ jobs, updateJobStatus, setSelectedJob, setShowAddNote, setShowAnalytics }) => {
  if (!jobs.length) {
    return <div className="text-center py-8 text-gray-500">No applications found matching your criteria.</div>;
  }
  return (
    <div className="space-y-4">
      {jobs.map(job => (
        <ApplicationCard
          key={job.id}
          job={job}
          updateJobStatus={updateJobStatus}
          setSelectedJob={setSelectedJob}
          setShowAddNote={setShowAddNote}
          setShowAnalytics={setShowAnalytics}
        />
      ))}
    </div>
  );
};

export default ApplicationsList; 