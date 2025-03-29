// src/components/Navbar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.svg';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="navbar-logo">
          <img src={logo} alt="FinDoc Analyzer Logo" />
        </Link>
        <div className="navbar-links">
          <Link to="/" className="navbar-link">בית</Link>
          <Link to="/documents" className="navbar-link">המסמכים שלי</Link>
          <Link to="/custom-tables" className="navbar-link">טבלאות מותאמות</Link>
        </div>
        <div className="navbar-actions">
          <button className="btn-primary">כניסה / הרשמה</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;