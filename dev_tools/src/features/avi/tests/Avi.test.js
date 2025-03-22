import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Avi } from '../index';

// Mock fetch API
global.fetch = jest.fn();

describe('Avi Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders loading state initially', () => {
    // Mock the fetch implementation
    fetch.mockImplementationOnce(() => {
      return new Promise(resolve => {
        // This promise never resolves to simulate loading
      });
    });

    render(<Avi />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders data when fetch succeeds', async () => {
    // Mock data
    const mockData = { example: 'data' };
    
    // Mock the fetch implementation
    fetch.mockImplementationOnce(() => {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockData)
      });
    });

    render(<Avi />);
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Expect data to be rendered
    expect(screen.getByText(JSON.stringify(mockData, null, 2))).toBeInTheDocument();
  });

  it('renders error when fetch fails', async () => {
    // Mock the fetch implementation
    fetch.mockImplementationOnce(() => {
      return Promise.resolve({
        ok: false,
        status: 500
      });
    });

    render(<Avi />);
    
    // Wait for loading to finish and error to show
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
