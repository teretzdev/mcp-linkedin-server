import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SettingsPage from './SettingsPage';

describe('SettingsPage Gemini Key', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('saves Gemini key to localStorage and calls onGeminiKeyChange', () => {
    const mockOnGeminiKeyChange = jest.fn();
    render(<SettingsPage geminiKey="" onGeminiKeyChange={mockOnGeminiKeyChange} />);

    const input = screen.getByPlaceholderText(/paste your gemini api key/i);
    fireEvent.change(input, { target: { value: 'test-gemini-key-123' } });

    const saveButton = screen.getByText(/save gemini key/i);
    fireEvent.click(saveButton);

    expect(localStorage.getItem('gemini_api_key')).toBe('test-gemini-key-123');
    expect(mockOnGeminiKeyChange).toHaveBeenCalledWith('test-gemini-key-123');
    expect(screen.getByText(/gemini key saved/i)).toBeInTheDocument();
  });
}); 