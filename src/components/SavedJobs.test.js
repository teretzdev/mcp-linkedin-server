import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';
import SavedJobs from './SavedJobs';

jest.mock('axios');

describe('SavedJobs UI & Interactivity', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches saved jobs from API and displays them', async () => {
    const mockJobs = [
      {
        id: 1,
        title: 'Saved Test Job',
        company: 'Saved Company',
        location: 'Remote',
        dateSaved: '2024-06-01',
        url: 'https://example.com/job/1',
      },
    ];
    axios.get.mockResolvedValueOnce({ data: { jobs: mockJobs } });
    render(<MemoryRouter><SavedJobs /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Saved Test Job')).toBeInTheDocument());
    expect(screen.getByText('Saved Company')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });

  it('searches and sorts saved jobs', async () => {
    const mockJobs = [
      { id: 1, title: 'Alpha', company: 'A', location: 'Remote', dateSaved: '2024-06-01', url: '#' },
      { id: 2, title: 'Beta', company: 'B', location: 'Onsite', dateSaved: '2024-06-02', url: '#' },
    ];
    axios.get.mockResolvedValueOnce({ data: { jobs: mockJobs } });
    render(<MemoryRouter><SavedJobs /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Alpha')).toBeInTheDocument());
    // Search
    fireEvent.change(screen.getByPlaceholderText(/search saved jobs/i), { target: { value: 'Beta' } });
    expect(screen.getByText('Beta')).toBeInTheDocument();
    // Sort
    fireEvent.change(screen.getByDisplayValue('Date Saved'), { target: { value: 'title' } });
    expect(screen.getByDisplayValue('Job Title')).toBeInTheDocument();
  });

  it('job card links and remove button work', async () => {
    const mockJobs = [
      { id: 1, title: 'Alpha', company: 'A', location: 'Remote', dateSaved: '2024-06-01', url: 'https://example.com/job/1' },
    ];
    axios.get.mockResolvedValueOnce({ data: { jobs: mockJobs } });
    axios.delete.mockResolvedValue({});
    render(<MemoryRouter><SavedJobs /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Alpha')).toBeInTheDocument());
    // View Job button
    const viewBtn = screen.getByRole('button', { name: /view job/i });
    expect(viewBtn).toBeInTheDocument();
    // Remove button
    const removeBtn = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeBtn);
    await waitFor(() => expect(axios.delete).toHaveBeenCalledWith('/api/saved_jobs/1'));
  });
}); 