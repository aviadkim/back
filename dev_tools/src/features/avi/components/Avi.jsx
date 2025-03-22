import React, { useState, useEffect } from 'react';
import './styles.css';

const Avi = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // TODO: Replace with actual API call
        const response = await fetch('/api/avi');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message);
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="avi-container">
      <h2>Avi</h2>
      
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">Error: {error}</div>}
      
      {data && (
        <div className="data-container">
          /* TODO: Render your data here */
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default Avi;
