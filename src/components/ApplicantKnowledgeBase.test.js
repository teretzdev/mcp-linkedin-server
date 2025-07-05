import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import ApplicantKnowledgeBase from './ApplicantKnowledgeBase';

jest.mock('axios');

describe('ApplicantKnowledgeBase Integration', () => {
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
    // Wait for the profile name to appear
    await waitFor(() => expect(screen.getByText('Test User')).toBeInTheDocument());
    expect(screen.getByText('testuser@email.com')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });
}); 