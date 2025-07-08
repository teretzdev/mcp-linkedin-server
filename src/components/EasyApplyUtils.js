// Utility functions for Easy Apply Assistant

import axios from 'axios';

export async function analyzeJobFit(jobDetails, applicantProfile, geminiKey) {
  if (!geminiKey) return null;
  try {
    const response = await axios.post('/api/easy_apply/analyze_fit', {
      job_context: jobDetails,
      applicant_profile: applicantProfile,
      gemini_api_key: geminiKey,
      question_id: 'fit_analysis',
      question: 'Job fit analysis',
      question_type: 'text',
      question_category: 'analysis',
      required: false
    });
    if (response.data.success) {
      return response.data;
    }
  } catch (error) {
    // Fallback: return null
  }
  return null;
}

export async function generateAnswer({ questionId, question, questionType, questionCategory, required, options, maxLength, jobContext, applicantProfile, previousAnswers, geminiKey }) {
  if (!geminiKey) return '';
  try {
    const response = await axios.post('/api/easy_apply/generate_answer', {
      question_id: questionId,
      question,
      question_type: questionType,
      question_category: questionCategory,
      required,
      options,
      max_length: maxLength,
      job_context: jobContext,
      applicant_profile: applicantProfile,
      previous_answers: previousAnswers,
      gemini_api_key: geminiKey
    });
    if (response.data.success) {
      return response.data.answer;
    } else {
      return response.data.fallback_answer || '';
    }
  } catch (error) {
    return '';
  }
} 