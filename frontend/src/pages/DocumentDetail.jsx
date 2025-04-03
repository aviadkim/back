import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import DocumentViewer from '../components/documents/DocumentViewer';
import DocumentMetadata from '../components/documents/DocumentMetadata';
import ExtractedDataPanel from '../components/documents/ExtractedDataPanel';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Button from '../components/ui/Button';
import '../styles/DocumentDetail.css';

const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('preview');

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/documents/${id}`);
        setDocument(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load document. Please try again later.');
        toast.error('Error loading document');
        console.error('Error fetching document:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();
  }, [id]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await axios.delete(`/api/documents/${id}`);
        toast.success('Document deleted successfully');
        navigate('/documents');
      } catch (err) {
        toast.error('Failed to delete document');
        console.error('Error deleting document:', err);
      }
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (!document) {
    return <div className="not-found">Document not found</div>;
  }

  return (
    <div className="document-detail-container">
      <div className="document-header">
        <h1>{document.filename}</h1>
        <div className="document-actions">
          <Button
            onClick={() => window.open(`/api/documents/${id}/download`, '_blank')}
            variant="primary"
          >
            Download
          </Button>
          <Button
            onClick={() => navigate(`/chat?documentId=${id}`)}
            variant="secondary"
          >
            Ask Questions
          </Button>
          <Button
            onClick={handleDelete}
            variant="danger"
          >
            Delete
          </Button>
        </div>
      </div>

      <div className="document-tabs">
        <button
          className={activeTab === 'preview' ? 'active' : ''}
          onClick={() => setActiveTab('preview')}
        >
          Preview
        </button>
        <button
          className={activeTab === 'data' ? 'active' : ''}
          onClick={() => setActiveTab('data')}
        >
          Extracted Data
        </button>
        <button
          className={activeTab === 'metadata' ? 'active' : ''}
          onClick={() => setActiveTab('metadata')}
        >
          Metadata
        </button>
      </div>

      <div className="document-content">
        {activeTab === 'preview' && (
          <DocumentViewer document={document} />
        )}
        {activeTab === 'data' && (
          <ExtractedDataPanel document={document} />
        )}
        {activeTab === 'metadata' && (
          <DocumentMetadata document={document} />
        )}
      </div>
    </div>
  );
};

export default DocumentDetail;
