import React from 'react';

// Basic placeholder Layout component
// It just renders the children passed to it.
function Layout({ children }) {
  // You could add common layout elements here later (header, footer, etc.)
  // For now, just render the page content.
  const layoutStyle = {
    padding: '1rem', // Add some basic padding
    minHeight: 'calc(100vh - 100px)' // Example height
  };

  return (
    <div className="layout-placeholder" style={layoutStyle}>
      {children}
    </div>
  );
}

export default Layout;