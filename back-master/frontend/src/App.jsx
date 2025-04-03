import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import DocumentList from './pages/DocumentList';
import DocumentUploader from './pages/DocumentUploader';
import DocumentDetail from './pages/DocumentDetail';
import ChatInterface from './pages/ChatInterface';
import TableGenerator from './pages/TableGenerator';
import Dashboard from './pages/Dashboard';
import { DocumentProvider } from './context/DocumentContext';
import { AuthProvider } from './context/AuthContext';
import './styles/index.css';

function App() {
  return (
    <AuthProvider>
      <DocumentProvider>
        <Router>
          <div className="app-container">
            <Navbar />
            <div className="content-wrapper">
              <Sidebar />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/documents" element={<DocumentList />} />
                  <Route path="/documents/:id" element={<DocumentDetail />} />
                  <Route path="/upload" element={<DocumentUploader />} />
                  <Route path="/chat" element={<ChatInterface />} />
                  <Route path="/tables" element={<TableGenerator />} />
                </Routes>
              </main>
            </div>
            <Toaster position="top-right" />
          </div>
        </Router>
      </DocumentProvider>
    </AuthProvider>
  );
}

export default App;
