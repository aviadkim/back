import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Assuming App.jsx is the main component
import './index.css'; // Assuming a base index.css exists or will be created
import './App.css'; // Import the main App CSS

// Optional: Import Font Awesome if needed globally
// import '@fortawesome/fontawesome-free/css/all.min.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);