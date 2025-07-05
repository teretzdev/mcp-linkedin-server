import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import JobSearch from './JobSearch';

jest.mock('axios');

describe('JobSearch Integration', () => {
  it('fetches jobs from API and displays them', async () => {
    const mockJobs = [
      {
        id: 1,
        title: 'Integration Test Job',
        company: 'Test Company',
        location: 'Remote',
        experienceLevel: 'Entry Level',
        jobType: 'Full-time',
        salaryRange: '$80k - $100k',
        skills: ['React', 'JavaScript'],
        datePosted: '2024-06-01',
      },
    ];
    axios.get.mockResolvedValueOnce({ data: { jobs: mockJobs } });
    render(<JobSearch updateSessionStats={() => {}} sessionStats={{}} />);
    // Wait for the job to appear
    await waitFor(() => expect(screen.getByText('Integration Test Job')).toBeInTheDocument());
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });
}); 