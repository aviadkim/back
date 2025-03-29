// src/App.jsx - הקובץ הראשי של אפליקציית React
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import DocumentsPage from './pages/DocumentsPage';
import DocumentDetailPage from './pages/DocumentDetailPage';
import CustomTablesPage from './pages/CustomTablesPage';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/documents/:documentId" element={<DocumentDetailPage />} />
            <Route path="/custom-tables" element={<CustomTablesPage />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
