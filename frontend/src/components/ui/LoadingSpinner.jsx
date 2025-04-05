import React from 'react';

// Basic placeholder LoadingSpinner component
function LoadingSpinner() {
  // Simple text-based spinner
  const spinnerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '2rem',
    fontSize: '1.2rem',
    color: '#555'
  };

  return (
    <div style={spinnerStyle}>
      Loading...
    </div>
  );
}

export default LoadingSpinner;