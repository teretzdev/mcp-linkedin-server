import React from 'react';
import { Building, MapPin, Clock, DollarSign, Star, Users, TrendingUp, Bookmark, Send, Eye } from 'lucide-react';

const JobCard = ({ job, saveJob, applyToJob }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          <img src={job.logo} alt={job.company} className="w-12 h-12 rounded-lg" />
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-xl font-semibold text-gray-800">{job.title}</h3>
              {job.easyApply && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Easy Apply</span>
              )}
              {job.remote && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Remote</span>
              )}
            </div>
            <div className="flex items-center space-x-4 text-gray-600 mb-3">
              <div className="flex items-center"><Building className="w-4 h-4 mr-1" /><span>{job.company}</span></div>
              <div className="flex items-center"><MapPin className="w-4 h-4 mr-1" /><span>{job.location}</span></div>
              <div className="flex items-center"><Clock className="w-4 h-4 mr-1" /><span>{job.posted}</span></div>
            </div>
            <div className="flex items-center space-x-4 text-gray-600 mb-3">
              <div className="flex items-center"><DollarSign className="w-4 h-4 mr-1" /><span>{job.salary}</span></div>
              <span>•</span>
              <span>{job.experience}</span>
              <span>•</span>
              <span>{job.type}</span>
            </div>
            <p className="text-gray-700 mb-4 line-clamp-2">{job.description}</p>
            <div className="flex flex-wrap gap-2 mb-4">
              {job.skills.map((skill, index) => (
                <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">{skill}</span>
              ))}
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
              <div className="flex items-center"><Star className="w-4 h-4 mr-1" /><span>{job.rating}</span></div>
              <div className="flex items-center"><Users className="w-4 h-4 mr-1" /><span>{job.applicants} applicants</span></div>
              <div className="flex items-center"><TrendingUp className="w-4 h-4 mr-1" /><span>{job.companySize}</span></div>
            </div>
          </div>
        </div>
        <div className="flex flex-col space-y-2 ml-4">
          <button onClick={() => saveJob(job.id)} className={`p-2 rounded-lg border transition-colors ${job.saved ? 'bg-blue-50 border-blue-200 text-blue-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}>
            <Bookmark className="w-5 h-5" />
          </button>
          <button onClick={() => applyToJob(job)} className={`p-2 rounded-lg border transition-colors ${job.easyApply ? 'bg-green-50 border-green-200 text-green-600 hover:bg-green-100' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}>
            {job.easyApply ? <Send className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-4">
          <button onClick={() => applyToJob(job)} className={`px-4 py-2 rounded-lg font-medium transition-colors ${job.easyApply ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-blue-600 text-white hover:bg-blue-700'}`}>{job.easyApply ? 'Easy Apply' : 'View Job'}</button>
          <button onClick={() => saveJob(job.id)} className={`px-4 py-2 border rounded-lg transition-colors ${job.saved ? 'border-blue-300 text-blue-600 bg-blue-50' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}`}>{job.saved ? 'Saved' : 'Save Job'}</button>
        </div>
      </div>
    </div>
  );
};

export default JobCard; 