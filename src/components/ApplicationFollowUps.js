import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Calendar, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  Plus, 
  Edit3, 
  Trash2,
  Mail,
  Phone,
  MessageSquare
} from 'lucide-react';
import axios from 'axios';

const ApplicationFollowUps = () => {
  const [followUps, setFollowUps] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [newFollowUp, setNewFollowUp] = useState({
    type: 'email',
    date: '',
    notes: '',
    completed: false
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [applicationsResponse, followUpsResponse] = await Promise.all([
          axios.get('/api/list_applied_jobs'),
          axios.get('/api/list_follow_ups')
        ]);
        
        setApplications(applicationsResponse.data.applied_jobs || []);
        setFollowUps(followUpsResponse.data.follow_ups || []);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const addFollowUp = async () => {
    if (!selectedApplication || !newFollowUp.date) return;
    
    try {
      const followUp = {
        id: Date.now().toString(),
        applicationId: selectedApplication.id,
        applicationTitle: selectedApplication.title,
        applicationCompany: selectedApplication.company,
        type: newFollowUp.type,
        date: newFollowUp.date,
        notes: newFollowUp.notes,
        completed: false,
        createdAt: new Date().toISOString()
      };
      
      // In a real app, this would call an API
      setFollowUps(prev => [...prev, followUp]);
      
      // Reset form
      setNewFollowUp({
        type: 'email',
        date: '',
        notes: '',
        completed: false
      });
      setSelectedApplication(null);
      setShowAddModal(false);
    } catch (error) {
      console.error('Failed to add follow-up:', error);
    }
  };

  const toggleFollowUp = async (followUpId) => {
    setFollowUps(prev => 
      prev.map(followUp => 
        followUp.id === followUpId 
          ? { ...followUp, completed: !followUp.completed }
          : followUp
      )
    );
  };

  const deleteFollowUp = async (followUpId) => {
    setFollowUps(prev => prev.filter(followUp => followUp.id !== followUpId));
  };

  const getFollowUpIcon = (type) => {
    switch (type) {
      case 'email': return Mail;
      case 'phone': return Phone;
      case 'linkedin': return MessageSquare;
      default: return Bell;
    }
  };

  const getFollowUpColor = (type) => {
    switch (type) {
      case 'email': return 'bg-blue-100 text-blue-800';
      case 'phone': return 'bg-green-100 text-green-800';
      case 'linkedin': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getUpcomingFollowUps = () => {
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    return followUps.filter(followUp => {
      const followUpDate = new Date(followUp.date);
      return !followUp.completed && followUpDate >= today && followUpDate <= nextWeek;
    }).sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const getOverdueFollowUps = () => {
    const today = new Date();
    
    return followUps.filter(followUp => {
      const followUpDate = new Date(followUp.date);
      return !followUp.completed && followUpDate < today;
    }).sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const upcomingFollowUps = getUpcomingFollowUps();
  const overdueFollowUps = getOverdueFollowUps();

  if (loading) {
    return (
      <div className="flex items-center justify-center space-x-2 p-6">
        <Clock className="w-6 h-6 animate-spin text-linkedin-600" />
        <span className="text-gray-600">Loading follow-ups...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Follow-up Tracker</h1>
            <p className="text-gray-600">Stay on top of your job application follow-ups</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Follow-up
          </button>
        </div>
      </div>

      {/* Overdue Follow-ups */}
      {overdueFollowUps.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <h2 className="text-lg font-semibold text-red-900">Overdue Follow-ups</h2>
          </div>
          <div className="space-y-3">
            {overdueFollowUps.map(followUp => {
              const Icon = getFollowUpIcon(followUp.type);
              return (
                <div key={followUp.id} className="bg-white p-4 rounded-lg border border-red-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Icon className="w-5 h-5 text-red-600" />
                      <div>
                        <p className="font-medium text-gray-900">{followUp.applicationTitle}</p>
                        <p className="text-sm text-gray-600">{followUp.applicationCompany}</p>
                        <p className="text-xs text-red-600">
                          Due: {new Date(followUp.date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleFollowUp(followUp.id)}
                        className="p-2 text-green-600 hover:bg-green-100 rounded"
                        title="Mark as completed"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteFollowUp(followUp.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded"
                        title="Delete follow-up"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  {followUp.notes && (
                    <p className="text-sm text-gray-600 mt-2">{followUp.notes}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Upcoming Follow-ups */}
      {upcomingFollowUps.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Clock className="w-5 h-5 text-yellow-600 mr-2" />
            <h2 className="text-lg font-semibold text-yellow-900">Upcoming Follow-ups</h2>
          </div>
          <div className="space-y-3">
            {upcomingFollowUps.map(followUp => {
              const Icon = getFollowUpIcon(followUp.type);
              return (
                <div key={followUp.id} className="bg-white p-4 rounded-lg border border-yellow-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Icon className="w-5 h-5 text-yellow-600" />
                      <div>
                        <p className="font-medium text-gray-900">{followUp.applicationTitle}</p>
                        <p className="text-sm text-gray-600">{followUp.applicationCompany}</p>
                        <p className="text-xs text-yellow-600">
                          Due: {new Date(followUp.date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleFollowUp(followUp.id)}
                        className="p-2 text-green-600 hover:bg-green-100 rounded"
                        title="Mark as completed"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteFollowUp(followUp.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded"
                        title="Delete follow-up"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  {followUp.notes && (
                    <p className="text-sm text-gray-600 mt-2">{followUp.notes}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* All Follow-ups */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">All Follow-ups</h2>
        {followUps.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No follow-ups created yet.</p>
        ) : (
          <div className="space-y-3">
            {followUps
              .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
              .map(followUp => {
                const Icon = getFollowUpIcon(followUp.type);
                const isOverdue = new Date(followUp.date) < new Date() && !followUp.completed;
                return (
                  <div 
                    key={followUp.id} 
                    className={`p-4 rounded-lg border ${
                      followUp.completed 
                        ? 'bg-green-50 border-green-200' 
                        : isOverdue 
                          ? 'bg-red-50 border-red-200' 
                          : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-5 h-5 ${
                          followUp.completed 
                            ? 'text-green-600' 
                            : isOverdue 
                              ? 'text-red-600' 
                              : 'text-gray-600'
                        }`} />
                        <div>
                          <p className={`font-medium ${
                            followUp.completed ? 'text-green-900' : 'text-gray-900'
                          }`}>
                            {followUp.applicationTitle}
                          </p>
                          <p className="text-sm text-gray-600">{followUp.applicationCompany}</p>
                          <p className={`text-xs ${
                            followUp.completed 
                              ? 'text-green-600' 
                              : isOverdue 
                                ? 'text-red-600' 
                                : 'text-gray-600'
                          }`}>
                            Due: {new Date(followUp.date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFollowUpColor(followUp.type)}`}>
                          {followUp.type}
                        </span>
                        <button
                          onClick={() => toggleFollowUp(followUp.id)}
                          className={`p-2 rounded ${
                            followUp.completed 
                              ? 'text-green-600 hover:bg-green-100' 
                              : 'text-gray-600 hover:bg-gray-100'
                          }`}
                          title={followUp.completed ? 'Mark as incomplete' : 'Mark as completed'}
                        >
                          <CheckCircle className={`w-4 h-4 ${followUp.completed ? 'fill-current' : ''}`} />
                        </button>
                        <button
                          onClick={() => deleteFollowUp(followUp.id)}
                          className="p-2 text-red-600 hover:bg-red-100 rounded"
                          title="Delete follow-up"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    {followUp.notes && (
                      <p className="text-sm text-gray-600 mt-2">{followUp.notes}</p>
                    )}
                  </div>
                );
              })}
          </div>
        )}
      </div>

      {/* Add Follow-up Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Follow-up</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Application</label>
                <select
                  value={selectedApplication?.id || ''}
                  onChange={(e) => {
                    const app = applications.find(a => a.id === e.target.value);
                    setSelectedApplication(app);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                >
                  <option value="">Select an application</option>
                  {applications.map(app => (
                    <option key={app.id} value={app.id}>
                      {app.title} at {app.company}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Follow-up Type</label>
                <select
                  value={newFollowUp.type}
                  onChange={(e) => setNewFollowUp(prev => ({ ...prev, type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                >
                  <option value="email">Email</option>
                  <option value="phone">Phone Call</option>
                  <option value="linkedin">LinkedIn Message</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
                <input
                  type="date"
                  value={newFollowUp.date}
                  onChange={(e) => setNewFollowUp(prev => ({ ...prev, date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                <textarea
                  value={newFollowUp.notes}
                  onChange={(e) => setNewFollowUp(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder="Add notes about this follow-up..."
                  className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent resize-none"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setSelectedApplication(null);
                  setNewFollowUp({
                    type: 'email',
                    date: '',
                    notes: '',
                    completed: false
                  });
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={addFollowUp}
                disabled={!selectedApplication || !newFollowUp.date}
                className="px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Follow-up
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApplicationFollowUps; 