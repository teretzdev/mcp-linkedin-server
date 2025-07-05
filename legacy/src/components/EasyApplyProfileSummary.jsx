import React from 'react';

const EasyApplyProfileSummary = ({ applicantProfile }) => {
  if (!applicantProfile) return null;
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mt-6">
      <h3 className="text-lg font-medium text-gray-800 mb-4">Your Profile Summary</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-sm text-gray-500">Name</p>
          <p className="font-medium">{applicantProfile.name}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Experience</p>
          <p className="font-medium">{applicantProfile.experience_years} years</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Location</p>
          <p className="font-medium">{applicantProfile.location}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Authorization</p>
          <p className="font-medium">{applicantProfile.work_authorization}</p>
        </div>
      </div>
    </div>
  );
};

export default EasyApplyProfileSummary; 