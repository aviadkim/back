// src/components/home/FeatureCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './FeatureCard.css';

function FeatureCard({ feature }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">
        <i className={`icon-${feature.icon}`}></i>
      </div>
      <h3 className="feature-title">{feature.title}</h3>
      <p className="feature-description">{feature.description}</p>
      <Link to={feature.link} className="feature-link">
        לפרטים נוספים <i className="icon-arrow-left"></i>
      </Link>
    </div>
  );
}

export default FeatureCard;