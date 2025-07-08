import React from 'react';
import { Building, MapPin, Calendar, CheckCircle, XCircle, Edit3, ExternalLink, MessageSquare, Star, Clock } from 'lucide-react';

const statusConfig = {
  'applied': { label: 'Applied', color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
  'under_review': { label: 'Under Review', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  'interview': { label: 'Interview', color: 'bg-purple-100 text-purple-800', icon: MessageSquare },
  'offer': { label: 'Offer', color: 'bg-green-100 text-green-800', icon: Star },
  'rejected': { label: 'Rejected', color: 'bg-red-100 text-red-800', icon: XCircle },
  'withdrawn': { label: 'Withdrawn', color: 'bg-gray-100 text-gray-800', icon: XCircle }
};

const ApplicationCard = ({ job, updateJobStatus, setSelectedJob, setShowAddNote, setShowAnalytics }) => {
  const StatusIcon = statusConfig[job.status]?.icon || CheckCircle;
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="font-medium text-gray-900">{job.title || 'Job Title'}</h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusConfig[job.status]?.color}`}>
              <StatusIcon className="w-3 h-3 inline mr-1" />
              {statusConfig[job.status]?.label}
            </span>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
            <div className="flex items-center"><Building className="w-4 h-4 mr-1" />{job.company || 'Company'}</div>
            <div className="flex items-center"><MapPin className="w-4 h-4 mr-1" />{job.location || 'Location'}</div>
            <div className="flex items-center"><Calendar className="w-4 h-4 mr-1" />{job.date_applied ? new Date(job.date_applied).toLocaleDateString() : 'Date'}</div>
          </div>
          {/* Notes Preview */}
          {job.notes && job.notes.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-1">Latest Note:</p>
              <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">{job.notes[job.notes.length - 1].text}</p>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <select
            value={job.status}
            onChange={e => updateJobStatus(job.id, e.target.value)}
            className="text-xs border border-gray-300 rounded px-2 py-1"
          >
            {Object.entries(statusConfig).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
          <button
            onClick={() => {
              setSelectedJob(job);
              setShowAddNote(true);
            }}
            className="p-2 text-gray-600 hover:text-linkedin-600 hover:bg-gray-100 rounded"
            title="Add Note"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <a
            href={job.jobUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 text-gray-600 hover:text-linkedin-600 hover:bg-gray-100 rounded"
            title="View Job"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default ApplicationCard; 