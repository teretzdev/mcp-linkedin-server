import React from 'react';

const ApplicationsNotes = ({ job, newNote, setNewNote, addNote, showAddNote, setShowAddNote }) => {
  if (!job) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Add Note for {job.title}
        </h3>
        <textarea
          value={newNote}
          onChange={e => setNewNote(e.target.value)}
          placeholder="Add a note about this application..."
          className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent resize-none"
        />
        <div className="flex justify-end space-x-2 mt-4">
          <button
            onClick={() => {
              setShowAddNote(false);
              setNewNote('');
            }}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={() => addNote(job.id)}
            className="px-4 py-2 bg-linkedin-600 text-white rounded-lg hover:bg-linkedin-700"
          >
            Add Note
          </button>
        </div>
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Previous Notes</h4>
          <ul className="space-y-2">
            {(job.notes || []).map(note => (
              <li key={note.id} className="bg-gray-50 p-2 rounded text-sm text-gray-700">
                {note.text}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ApplicationsNotes; 