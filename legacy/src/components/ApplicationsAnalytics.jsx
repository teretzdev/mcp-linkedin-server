import React from 'react';

const ApplicationsAnalytics = ({ analytics }) => {
  if (!analytics) return null;
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Analytics</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-blue-600">Total Applications</p>
          <p className="text-2xl font-bold text-blue-900">{analytics.total}</p>
        </div>
        {Object.entries(analytics.statusCounts || {}).map(([status, count]) => (
          <div key={status} className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">{status}</p>
            <p className="text-2xl font-bold text-gray-900">{count}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ApplicationsAnalytics; 