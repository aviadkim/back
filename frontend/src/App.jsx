import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar'; // Restored with correct path
import Sidebar from './components/Sidebar'; // Restored with placeholder
import DocumentsPage from './pages/DocumentsPage';
import UploadPage from './pages/UploadPage'; // Renamed from DocumentUploader
import DocumentDetailPage from './pages/DocumentDetailPage'; // Renamed from DocumentDetail
// import ChatInterface from './pages/ChatInterface'; // Commented out - file missing
import CustomTablesPage from './pages/CustomTablesPage'; // Renamed from TableGenerator
import Dashboard from './pages/Dashboard';
import { DocumentProvider } from './context/DocumentContext';
// import { AuthProvider } from './context/AuthContext'; // Commented out - file missing
import './index.css';

function App() {
  return (
      <DocumentProvider>
        <Router>
          <div className="app-container">
            <Navbar /> {/* Restored */}
            <div className="content-wrapper">
              <Sidebar /> {/* Restored with placeholder */}
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/documents/:id" element={<DocumentDetailPage />} />
                  <Route path="/upload" element={<UploadPage />} />
                  {/* <Route path="/chat" element={<ChatInterface />} /> */} {/* Commented out - component missing */}
                  <Route path="/tables" element={<CustomTablesPage />} />
                </Routes>
              </main>
            </div>
            <Toaster position="top-right" />
          </div>
        </Router>
      </DocumentProvider>
  );
}

export default App;
