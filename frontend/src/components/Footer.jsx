// src/components/Footer.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-section">
            <h3 className="footer-title">FinDoc Analyzer</h3>
            <p className="footer-description">
              פלטפורמה מתקדמת לעיבוד מסמכים פיננסיים באמצעות בינה מלאכותית.
            </p>
          </div>
          <div className="footer-section">
            <h3 className="footer-title">תכונות</h3>
            <ul className="footer-links">
              <li><Link to="/features/ocr">עיבוד מסמכים</Link></li>
              <li><Link to="/features/tables">זיהוי טבלאות</Link></li>
              <li><Link to="/features/isin">זיהוי ISIN</Link></li>
              <li><Link to="/features/chat">עוזר חכם</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h3 className="footer-title">משאבים</h3>
            <ul className="footer-links">
              <li><Link to="/docs">תיעוד</Link></li>
              <li><Link to="/api">API</Link></li>
              <li><Link to="/faq">שאלות נפוצות</Link></li>
              <li><Link to="/blog">בלוג</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h3 className="footer-title">צור קשר</h3>
            <ul className="footer-contact">
              <li>
                <i className="icon-email"></i>
                <span>info@findoc-analyzer.com</span>
              </li>
              <li>
                <i className="icon-phone"></i>
                <span>03-1234567</span>
              </li>
              <li>
                <i className="icon-location"></i>
                <span>רוטשילד 22, תל אביב</span>
              </li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2025 FinDoc Analyzer. כל הזכויות שמורות.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;