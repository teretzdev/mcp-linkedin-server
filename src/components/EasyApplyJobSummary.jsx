import React from 'react';

const EasyApplyJobSummary = ({ jobContext }) => {
  if (!jobContext) return null;
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">{jobContext.title}</h2>
      <p className="text-gray-600 mb-2">{jobContext.company} • {jobContext.location}</p>
      <p className="text-gray-700 mb-2">{jobContext.salary_range}</p>
      <p className="text-gray-700 mb-2">{jobContext.description}</p>
      <div className="flex flex-wrap gap-2 mt-2">
        {jobContext.requirements?.map((req, i) => (
          <span key={i} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">{req}</span>
        ))}
      </div>
    </div>
  );
};

export default EasyApplyJobSummary; 