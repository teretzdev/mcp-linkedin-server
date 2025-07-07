import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import ApplicantKnowledgeBase from './ApplicantKnowledgeBase';

jest.mock('axios');

describe('ApplicantKnowledgeBase UI & Interactivity', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches applicant profile from API and displays it', async () => {
    const mockProfile = {
      personalInfo: {
        name: 'Test User',
        email: 'testuser@email.com',
        phone: '+1 (555) 123-4567',
        location: 'Test City',
        linkedin: 'linkedin.com/in/testuser',
        github: 'github.com/testuser',
        portfolio: 'testuser.dev'
      },
      skills: [
        { name: 'React', level: 'Expert', years: 4, category: 'Frontend' },
        { name: 'Python', level: 'Intermediate', years: 3, category: 'Programming' }
      ],
      experiences: [
        { title: 'Developer', company: 'TestCorp', duration: '2020-2022', description: 'Did stuff' }
      ],
      education: [
        { degree: 'BSc Computer Science', school: 'Test University', year: '2020' }
      ]
    };
    axios.get.mockResolvedValueOnce({ data: mockProfile });
    render(<ApplicantKnowledgeBase />);
    await waitFor(() => expect(screen.getByText('Test User')).toBeInTheDocument());
    expect(screen.getByText('testuser@email.com')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });

  it('searches and filters skills', async () => {
    const mockProfile = {
      personalInfo: { name: 'Test User', email: '', phone: '', location: '', linkedin: '', github: '', portfolio: '' },
      skills: [
        { name: 'React', level: 'Expert', years: 4, category: 'Frontend' },
        { name: 'Python', level: 'Intermediate', years: 3, category: 'Programming' }
      ],
      experiences: [],
      education: []
    };
    axios.get.mockResolvedValueOnce({ data: mockProfile });
    render(<ApplicantKnowledgeBase />);
    await waitFor(() => expect(screen.getByText('React')).toBeInTheDocument());
    // Search
    fireEvent.change(screen.getByPlaceholderText(/search by skill name/i), { target: { value: 'Python' } });
    expect(screen.getByText('Python')).toBeInTheDocument();
    // Filter by category
    fireEvent.change(screen.getByLabelText(/Category/i), { target: { value: 'Frontend' } });
    expect(screen.getByText('React')).toBeInTheDocument();
    // Filter by level
    fireEvent.change(screen.getByLabelText(/Skill Level/i), { target: { value: 'Expert' } });
    expect(screen.getByText('React')).toBeInTheDocument();
  });

  it('clear filters button resets search and filters', async () => {
    const mockProfile = {
      personalInfo: { name: 'Test User', email: '', phone: '', location: '', linkedin: '', github: '', portfolio: '' },
      skills: [
        { name: 'React', level: 'Expert', years: 4, category: 'Frontend' },
        { name: 'Python', level: 'Intermediate', years: 3, category: 'Programming' }
      ],
      experiences: [],
      education: []
    };
    axios.get.mockResolvedValueOnce({ data: mockProfile });
    render(<ApplicantKnowledgeBase />);
    await waitFor(() => expect(screen.getByText('React')).toBeInTheDocument());
    fireEvent.change(screen.getByPlaceholderText(/search by skill name/i), { target: { value: 'Python' } });
    expect(screen.getByText('Python')).toBeInTheDocument();
    // Click clear filters
    fireEvent.click(screen.getByText(/Clear Filters/i));
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });

  it('renders personal info links', async () => {
    const mockProfile = {
      personalInfo: {
        name: 'Test User',
        email: 'testuser@email.com',
        phone: '+1 (555) 123-4567',
        location: 'Test City',
        linkedin: 'linkedin.com/in/testuser',
        github: 'github.com/testuser',
        portfolio: 'testuser.dev'
      },
      skills: [],
      experiences: [],
      education: []
    };
    axios.get.mockResolvedValueOnce({ data: mockProfile });
    render(<ApplicantKnowledgeBase />);
    await waitFor(() => expect(screen.getByText('Test User')).toBeInTheDocument());
    expect(screen.getByText('linkedin.com/in/testuser')).toBeInTheDocument();
    expect(screen.getByText('github.com/testuser')).toBeInTheDocument();
    expect(screen.getByText('testuser.dev')).toBeInTheDocument();
  });
}); 