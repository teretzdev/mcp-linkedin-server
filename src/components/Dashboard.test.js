import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

jest.mock('axios');

describe('Dashboard UI & Interactivity', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders checklist widget and shows progress', async () => {
    axios.get.mockImplementation((url) => {
      if (url === '/api/user/profile') return Promise.resolve({ data: { name: 'Test User', current_position: 'Engineer', location: 'Test City' } });
      if (url === '/api/stats') return Promise.resolve({ data: { jobsViewed: 5, jobsApplied: 2, jobsSaved: 1, successRate: 40 } });
      if (url === '/api/activity') return Promise.resolve({ data: [] });
      if (url === '/api/ai/recommendations') return Promise.resolve({ data: [] });
      if (url === '/api/linkedin/status') return Promise.resolve({ data: { loggedIn: true } });
      if (url === '/api/linkedin/profile-status') return Promise.resolve({ data: { complete: true } });
      if (url === '/api/resume/status') return Promise.resolve({ data: { uploaded: true } });
      if (url === '/api/preferences/status') return Promise.resolve({ data: { configured: true } });
      if (url === '/api/templates/status') return Promise.resolve({ data: { created: true } });
      if (url === '/api/companies/status') return Promise.resolve({ data: { set: true } });
      if (url === '/api/salary/status') return Promise.resolve({ data: { set: true } });
      if (url === '/api/automation/status') return Promise.resolve({ data: { status: 'idle', stats: {} } });
      return Promise.resolve({ data: {} });
    });
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Getting Started Checklist')).toBeInTheDocument());
    expect(screen.getByText('100% Complete')).toBeInTheDocument();
  });

  it('renders automation controls and disables Start if critical items missing', async () => {
    axios.get.mockImplementation((url) => {
      if (url === '/api/user/profile') return Promise.resolve({ data: { name: 'Test User' } });
      if (url === '/api/stats') return Promise.resolve({ data: {} });
      if (url === '/api/activity') return Promise.resolve({ data: [] });
      if (url === '/api/ai/recommendations') return Promise.resolve({ data: [] });
      if (url === '/api/linkedin/status') return Promise.resolve({ data: { loggedIn: false } });
      if (url === '/api/linkedin/profile-status') return Promise.resolve({ data: { complete: false } });
      if (url === '/api/resume/status') return Promise.resolve({ data: { uploaded: false } });
      if (url === '/api/preferences/status') return Promise.resolve({ data: { configured: false } });
      if (url === '/api/automation/status') return Promise.resolve({ data: { status: 'idle', stats: {} } });
      return Promise.resolve({ data: {} });
    });
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('AI Automation Status')).toBeInTheDocument());
    const startBtn = screen.getByRole('button', { name: /start/i });
    expect(startBtn).toBeDisabled();
  });

  it('renders quick actions and links', async () => {
    axios.get.mockImplementation((url) => {
      if (url === '/api/user/profile') return Promise.resolve({ data: { name: 'Test User' } });
      if (url === '/api/stats') return Promise.resolve({ data: {} });
      if (url === '/api/activity') return Promise.resolve({ data: [] });
      if (url === '/api/ai/recommendations') return Promise.resolve({ data: [] });
      if (url === '/api/automation/status') return Promise.resolve({ data: { status: 'idle', stats: {} } });
      return Promise.resolve({ data: {} });
    });
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Quick Actions')).toBeInTheDocument());
    expect(screen.getByText('Start Job Search').closest('a')).toHaveAttribute('href', '/job-search');
    expect(screen.getByText('Saved Jobs').closest('a')).toHaveAttribute('href', '/saved-jobs');
    expect(screen.getByText('AI Automation').closest('a')).toHaveAttribute('href', '/ai-automation');
  });

  it('checklist action links are correct', async () => {
    axios.get.mockImplementation((url) => {
      if (url === '/api/user/profile') return Promise.resolve({ data: { name: 'Test User' } });
      if (url === '/api/stats') return Promise.resolve({ data: {} });
      if (url === '/api/activity') return Promise.resolve({ data: [] });
      if (url === '/api/ai/recommendations') return Promise.resolve({ data: [] });
      if (url === '/api/automation/status') return Promise.resolve({ data: { status: 'idle', stats: {} } });
      return Promise.resolve({ data: {} });
    });
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('Getting Started Checklist')).toBeInTheDocument());
    // At least one checklist action link should be present
    const checklistLinks = screen.getAllByRole('link', { name: /verify login|update your linkedin profile|upload resume|configure job preferences|configure automation settings|create message templates|add target companies|set salary expectations|plan networking strategy|prepare interview materials/i });
    expect(checklistLinks.length).toBeGreaterThan(0);
  });

  it('automation control buttons are interactable', async () => {
    axios.get.mockImplementation((url) => {
      if (url === '/api/user/profile') return Promise.resolve({ data: { name: 'Test User' } });
      if (url === '/api/stats') return Promise.resolve({ data: {} });
      if (url === '/api/activity') return Promise.resolve({ data: [] });
      if (url === '/api/ai/recommendations') return Promise.resolve({ data: [] });
      if (url === '/api/linkedin/status') return Promise.resolve({ data: { loggedIn: true } });
      if (url === '/api/linkedin/profile-status') return Promise.resolve({ data: { complete: true } });
      if (url === '/api/resume/status') return Promise.resolve({ data: { uploaded: true } });
      if (url === '/api/preferences/status') return Promise.resolve({ data: { configured: true } });
      if (url === '/api/automation/status') return Promise.resolve({ data: { status: 'idle', stats: {} } });
      return Promise.resolve({ data: {} });
    });
    axios.post.mockResolvedValue({ data: { success: true } });
    render(<MemoryRouter><Dashboard /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('AI Automation Status')).toBeInTheDocument());
    const startBtn = screen.getByRole('button', { name: /start/i });
    fireEvent.click(startBtn);
    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('/api/automation/start');
  });
}); 