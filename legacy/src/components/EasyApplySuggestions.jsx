import React from 'react';

const EasyApplySuggestions = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) return null;
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mt-6">
      <h5 className="text-lg font-medium text-gray-800 mb-2">Suggestions</h5>
      <ul className="list-disc pl-6 text-gray-700">
        {suggestions.map((s, i) => <li key={i}>{s.text || s.suggestion || s.message}</li>)}
      </ul>
    </div>
  );
};

export default EasyApplySuggestions; 