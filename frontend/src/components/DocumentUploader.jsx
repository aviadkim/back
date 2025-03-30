import React, { useState } from 'react';
import axios from 'axios';

/**
 * Document Uploader Component
 * 
 * Allows users to upload financial documents for analysis
 */
const DocumentUploader = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [language, setLanguage] = useState('he');
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setError('');
  };

  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!file) {
      setError('נא לבחור קובץ להעלאה');
      return;
    }
    
    // Check file type
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['pdf', 'docx', 'xlsx', 'csv'];
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError(`סוג הקובץ אינו נתמך. סוגי קבצים מורשים: ${allowedExtensions.join(', ')}`);
      return;
    }
    
    // Check file size
    const maxSize = 20 * 1024 * 1024; // 20MB
    if (file.size > maxSize) {
      setError('הקובץ גדול מדי. יש להעלות קבצים עד 20MB');
      return;
    }
    
    setIsUploading(true);
    setUploadProgress(0);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);
    
    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });
      
      // Reset the form
      setFile(null);
      setIsUploading(false);
      setUploadProgress(0);
      
      // Call the success callback
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'שגיאה בהעלאת הקובץ, אנא נסו שוב.');
      setIsUploading(false);
    }
  };
  
  return (
    <div className="upload-container bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-primary-600">העלאת מסמך פיננסי</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="file-input-container border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
          <input
            type="file"
            id="document-file"
            onChange={handleFileChange}
            className="hidden"
            disabled={isUploading}
          />
          
          <label 
            htmlFor="document-file" 
            className="cursor-pointer block"
          >
            {file ? (
              <div className="flex flex-col items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-primary-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-medium text-primary-800">{file.name}</span>
                <span className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="text-primary-600 font-medium">לחץ לבחירת קובץ</span>
                <span className="text-sm text-gray-500 mt-1">
                  או גרור קובץ לכאן
                </span>
                <span className="text-xs text-gray-400 mt-2">
                  תומך בקבצי PDF, DOCX, XLSX, CSV עד 20MB
                </span>
              </div>
            )}
          </label>
        </div>
        
        <div className="language-selector">
          <label htmlFor="language-select" className="block text-sm font-medium text-gray-700 mb-1">
            שפת המסמך
          </label>
          <select
            id="language-select"
            value={language}
            onChange={handleLanguageChange}
            disabled={isUploading}
            className="block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="he">עברית</option>
            <option value="en">אנגלית</option>
            <option value="auto">זיהוי אוטומטי</option>
          </select>
        </div>
        
        {isUploading && (
          <div className="upload-progress">
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-primary-600 bg-primary-200">
                    מעלה...
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold inline-block text-primary-600">
                    {uploadProgress}%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary-200">
                <div 
                  style={{ width: `${uploadProgress}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500 transition-all duration-300"
                ></div>
              </div>
            </div>
          </div>
        )}
        
        <div className="submit-container">
          <button
            type="submit"
            disabled={!file || isUploading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? 'מעלה...' : 'העלאה וניתוח'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DocumentUploader;
