import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import SavedJobs from './SavedJobs';

jest.mock('axios');

describe('SavedJobs Integration', () => {
  it('fetches saved jobs from API and displays them', async () => {
    const mockJobs = [
      {
        id: 1,
        title: 'Saved Test Job',
        company: 'Saved Company',
        location: 'Remote',
        dateSaved: '2024-06-01',
      },
    ];
    axios.get.mockResolvedValueOnce({ data: { saved_jobs: mockJobs } });
    render(<SavedJobs updateSessionStats={() => {}} sessionStats={{}} />);
    // Wait for the job to appear
    await waitFor(() => expect(screen.getByText('Saved Test Job')).toBeInTheDocument());
    expect(screen.getByText('Saved Company')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });
}); 