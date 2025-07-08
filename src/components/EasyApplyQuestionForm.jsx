import React from 'react';
import { Loader2, Brain, CheckCircle, AlertCircle } from 'lucide-react';

const EasyApplyQuestionForm = ({ questions, answers, onAnswerChange, onGenerateAnswer, isProcessing, suggestions = [] }) => {
  if (!questions.length) return null;
  return (
    <div className="space-y-6 mt-6">
      {questions.map((question) => {
        const answer = answers[question.id] || '';
        return (
          <div key={question.id} className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-800 mb-2">
                  {question.question}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                </h3>
                {question.type === 'text' && (
                  <input
                    type="text"
                    value={answer}
                    onChange={e => onAnswerChange(question.id, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your answer..."
                  />
                )}
                {question.type === 'select' && (
                  <select
                    value={answer}
                    onChange={e => onAnswerChange(question.id, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select an option...</option>
                    {question.options?.map((option, index) => (
                      <option key={index} value={option}>{option}</option>
                    ))}
                  </select>
                )}
                {question.type === 'textarea' && (
                  <textarea
                    value={answer}
                    onChange={e => onAnswerChange(question.id, e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your detailed answer..."
                  />
                )}
              </div>
              <button
                onClick={() => onGenerateAnswer(question.id, question)}
                disabled={isProcessing}
                className="ml-4 flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {isProcessing ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Brain className="w-4 h-4 mr-2" />
                )}
                AI Help
              </button>
            </div>
            {/* Suggestions for this question */}
            {suggestions.filter(s => s.questionId === question.id).map((suggestion, index) => (
              <div key={index} className={`flex items-start p-3 rounded-lg mt-3 ${
                suggestion.type === 'improvement' ? 'bg-yellow-50 border border-yellow-200' : 'bg-green-50 border border-green-200'
              }`}>
                {suggestion.type === 'improvement' ? (
                  <AlertCircle className="w-4 h-4 text-yellow-600 mr-2 mt-0.5" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2 mt-0.5" />
                )}
                <p className="text-sm text-gray-700">{suggestion.message}</p>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
};

export default EasyApplyQuestionForm; 