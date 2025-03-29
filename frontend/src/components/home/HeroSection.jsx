// src/components/home/HeroSection.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import UploadWidget from '../documents/UploadWidget';
import './HeroSection.css';

function HeroSection() {
  return (
    <section className="hero-section">
      <div className="container">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">הפיכת מסמכים פיננסיים לתובנות פעילות</h1>
            <p className="hero-description">
              פלטפורמה מבוססת בינה מלאכותית המחלצת, מנתחת ומארגנת מידע ממסמכים פיננסיים בעברית ובאנגלית
            </p>
            <div className="hero-actions">
              <Link to="/documents" className="btn-primary btn-large">
                <i className="icon-upload"></i> העלה מסמך
              </Link>
              <button className="btn-secondary btn-large">
                <i className="icon-play"></i> צפה בהדגמה
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="demo-animation">
              {/* כאן תהיה אנימציה של המרת מסמך לנתונים או תמונה סטטית */}
              <img src="/images/demo-animation.png" alt="Document analysis demo" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;