import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';
import JobSearch from './JobSearch';

jest.mock('axios');

describe('JobSearch UI & Interactivity', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

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
        url: 'https://example.com/job/1',
      },
    ];
    axios.get.mockResolvedValueOnce({ data: { jobs: mockJobs } });
    render(<MemoryRouter><JobSearch updateSessionStats={() => {}} sessionStats={{}} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Integration Test Job')).toBeInTheDocument());
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });

  it('renders automation controls and toggles', async () => {
    axios.get.mockResolvedValueOnce({ data: { jobs: [] } });
    render(<MemoryRouter><JobSearch updateSessionStats={() => {}} sessionStats={{}} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText(/AI Automation Suite/i)).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /Start Full Automation/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Pause/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Stop/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reset Stats/i })).toBeInTheDocument();
    // Check toggles
    expect(screen.getByLabelText(/Auto Apply/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Auto Save/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Auto Connect/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Auto Message/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Remote Only/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/AI Resume/i)).toBeInTheDocument();
  });

  it('automation control buttons are interactable', async () => {
    axios.get.mockResolvedValueOnce({ data: { jobs: [] } });
    axios.post.mockResolvedValue({ data: { success: true } });
    render(<MemoryRouter><JobSearch updateSessionStats={() => {}} sessionStats={{}} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText(/AI Automation Suite/i)).toBeInTheDocument());
    const startBtn = screen.getByRole('button', { name: /Start Full Automation/i });
    fireEvent.click(startBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/automation/start', expect.any(Object)));
    const pauseBtn = screen.getByRole('button', { name: /Pause/i });
    fireEvent.click(pauseBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/automation/pause'));
    const stopBtn = screen.getByRole('button', { name: /Stop/i });
    fireEvent.click(stopBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/automation/stop'));
    const resetBtn = screen.getByRole('button', { name: /Reset Stats/i });
    fireEvent.click(resetBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/automation/reset'));
  });

  it('renders advanced filters and settings', async () => {
    axios.get.mockResolvedValueOnce({ data: { jobs: [] } });
    render(<MemoryRouter><JobSearch updateSessionStats={() => {}} sessionStats={{}} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText(/AI Automation Suite/i)).toBeInTheDocument());
    expect(screen.getByLabelText(/Max Jobs Per Run/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Search Keywords/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Target Companies/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Exclude Companies/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Target Salary/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Location/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Industry/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Company Size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Funding Stage/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Job Matching Score/i)).toBeInTheDocument();
  });

  it('job card links and buttons work', async () => {
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
        url: 'https://example.com/job/1',
      },
    ];
    axios.get.mockResolvedValueOnce({ data: { jobs: mockJobs } });
    axios.post.mockResolvedValue({ data: { success: true } });
    render(<MemoryRouter><JobSearch updateSessionStats={() => {}} sessionStats={{}} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Integration Test Job')).toBeInTheDocument());
    // Save and Apply buttons
    const saveBtn = screen.getByRole('button', { name: /Save/i });
    fireEvent.click(saveBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/save_job', { job_id: 1 }));
    const applyBtn = screen.getByRole('button', { name: /Apply/i });
    fireEvent.click(applyBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/apply_job', { job_id: 1 }));
  });
}); 