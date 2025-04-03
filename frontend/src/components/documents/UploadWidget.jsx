/**
 * Terminal Navigation Tips:
 * - Basic horizontal list: ls
 * - Show in columns: ls -C
 * - Show one per line: ls -1
 * - Show with details: ls -l
 * - Show hidden files: ls -a
 * - Sort by time: ls -t
 * - Human readable sizes: ls -lh
 * - Most useful combo: ls -lha
 * 
 * For main directories only:
 * ls -d
 * 
 * For colorized output:
 * ls --color=auto
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import documentService from '../../services/documentService'; // Assuming service exists
import './UploadWidget.css';

/**
 * רכיב להעלאת מסמכים חדשים
 * @param {Object} props - מאפייני הרכיב
 * @param {Function} props.onUploadSuccess - פונקציה שתופעל לאחר העלאה מוצלחת (מקבלת את תגובת השרת)
 * @param {Function} props.onUploadError - פונקציה שתופעל במקרה של שגיאה בהעלאה (מקבלת הודעת שגיאה)
 */

/**
 * Terminal Navigation Tips:
 * - Install tree: sudo apt-get install tree
 * - Basic usage: tree
 * - Limit depth: tree -L 2
 * - Show only directories: tree -d
 * - Include hidden files: tree -a
 * - Colorize output: tree -C
 * Example: tree -L 2 -d -C
 */

const UploadWidget = ({ onUploadSuccess, onUploadError }) => {
  const [uploadStatus, setUploadStatus] = useState('idle'); // 'idle', 'uploading', 'success', 'error'
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('auto');
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef(null); // Ref for hidden input
  const progressIntervalRef = useRef(null); // Ref for progress interval

  // הגדרת פונקציית onDrop עבור react-dropzone
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      // Reset previous errors/status before starting new upload
      setUploadError(null);
      setUploadStatus('idle');
      setFileName(file.name);
      handleFileUpload(file);
    } else {
        // Handle rejection (e.g., wrong file type, too large)
        // react-dropzone provides fileRejections array in onDrop
        // For simplicity, just showing a generic error here
        setUploadError('קובץ לא תקין או חורג מהגודל המותר.');
        setUploadStatus('error');
        if (onUploadError) onUploadError('קובץ לא תקין או חורג מהגודל המותר.');
    }
  }, [selectedLanguage, onUploadError]); // Add onUploadError dependency

  // הגדרת dropzone עם אפשרויות
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB limit
    disabled: uploadStatus === 'uploading'
  });

  // פונקציה לטיפול בקובץ שנבחר
  const handleFileUpload = async (file) => {
    // Double check file type (though dropzone should handle it)
    const validFileTypes = ['application/pdf', 'application/vnd.ms-excel',
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           'text/csv'];
    if (!validFileTypes.includes(file.type)) {
      setUploadError('סוג קובץ לא נתמך. אנא העלה קובץ PDF, Excel או CSV.');
      setUploadStatus('error');
      if (onUploadError) onUploadError('סוג קובץ לא נתמך');
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);
    setUploadError(null);

    try {
      // Start progress simulation
      progressIntervalRef.current = simulateProgress();

      // Use the service to upload
      const response = await documentService.uploadDocument(file, selectedLanguage);

      // Clear progress simulation
      clearInterval(progressIntervalRef.current);
      setUploadProgress(100);

      setUploadStatus('success');
      if (onUploadSuccess) onUploadSuccess(response); // Pass response data (e.g., { document_id: ... })

      // Reset after a delay
      setTimeout(() => {
        handleReset();
      }, 2500); // Slightly longer delay for success message

    } catch (error) {
      // Clear progress simulation
      clearInterval(progressIntervalRef.current);

      const errorMessage = error.message || 'שגיאה לא ידועה בהעלאת הקובץ.';
      setUploadError(errorMessage);
      setUploadStatus('error');
      if (onUploadError) onUploadError(errorMessage);
    }
  };

  // פונקציה להדמיית התקדמות ההעלאה
  const simulateProgress = () => {
    // Clear any existing interval first
    if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
    }
    // Start a new interval
    return setInterval(() => {
      setUploadProgress(prev => {
        // Simulate slower progress towards the end
        const increment = prev < 70 ? Math.random() * 10 : Math.random() * 3;
        const nextProgress = prev + increment;
        return nextProgress >= 95 ? 95 : nextProgress; // Cap at 95% until success
      });
    }, 300);
  };

  // פונקציה לטיפול בלחיצה על כפתור העלאה (triggers hidden input)
  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = null; // Reset input value to allow re-uploading same file
      fileInputRef.current.click();
    }
  };

  // פונקציה לניקוי הטופס
  const handleReset = () => {
    if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current); // Clear interval on reset
    }
    setUploadStatus('idle');
    setUploadProgress(0);
    setUploadError(null);
    setFileName('');
    if (fileInputRef.current) {
        fileInputRef.current.value = null; // Ensure input is cleared
    }
  };

  // Cleanup interval on component unmount
  useEffect(() => {
      return () => {
          if (progressIntervalRef.current) {
              clearInterval(progressIntervalRef.current);
          }
      };
  }, []);


  return (
    <div className="upload-widget">
      <div className="upload-widget-header">
        <h3>העלאת מסמך חדש</h3>
        <div className="language-selector">
          <label htmlFor="language-select">שפת המסמך:</label>
          <select
            id="language-select"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            disabled={uploadStatus === 'uploading'}
          >
            <option value="auto">זיהוי אוטומטי</option>
            <option value="he">עברית</option>
            <option value="en">אנגלית</option>
            <option value="multi">רב-לשוני</option> {/* Changed from 'mixed' */}
          </select>
        </div>
      </div>

      {/* Dropzone Area */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploadStatus !== 'idle' ? 'has-content' : ''} ${uploadStatus}`}
      >
        {/* Hidden file input */}
        <input {...getInputProps()} ref={fileInputRef} style={{ display: 'none' }} />

        {uploadStatus === 'idle' && !fileName && (
          <div className="dropzone-content idle">
            <i className="fas fa-file-upload dropzone-icon"></i>
            <p>גרור לכאן קובץ או <button type="button" className="browse-button" onClick={handleButtonClick}>לחץ לבחירת קובץ</button></p>
            <p className="dropzone-hint">PDF, Excel או CSV (עד 50MB)</p>
          </div>
        )}

         {uploadStatus === 'idle' && fileName && (
           <div className="dropzone-content file-selected">
             <i className="fas fa-file-alt dropzone-icon"></i>
             <p>קובץ נבחר: <strong>{fileName}</strong></p>
             <p>לחץ על כפתור ההעלאה למטה או בחר קובץ אחר.</p>
           </div>
         )}


        {uploadStatus === 'uploading' && (
          <div className="dropzone-content uploading">
            <div className="progress-container">
              <div
                className="progress-bar"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p>מעלה את הקובץ: {fileName}</p>
            <p className="upload-percentage">{Math.round(uploadProgress)}%</p>
          </div>
        )}

        {uploadStatus === 'success' && (
          <div className="dropzone-content success">
            <i className="fas fa-check-circle dropzone-icon success-icon"></i>
            <p>הקובץ <strong>{fileName}</strong> הועלה בהצלחה!</p>
          </div>
        )}

        {uploadStatus === 'error' && (
          <div className="dropzone-content error">
            <i className="fas fa-exclamation-triangle dropzone-icon error-icon"></i>
            <p className="error-message-text">{uploadError}</p>
            <button className="try-again-button" onClick={handleReset}>
              נסה שוב
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="upload-actions">
        {uploadStatus === 'idle' && !fileName && (
          <button
            className="upload-button btn-primary" // Use theme button style
            onClick={handleButtonClick}
          >
            <i className="fas fa-folder-open"></i> בחר קובץ
          </button>
        )}
         {uploadStatus === 'idle' && fileName && (
           <button
             className="upload-button btn-primary"
             onClick={() => handleFileUpload(fileInputRef.current?.files[0])} // Re-trigger upload logic if needed
             disabled={!fileInputRef.current?.files[0]} // Should have file if fileName is set
           >
             <i className="fas fa-upload"></i> העלה את {fileName}
           </button>
         )}

        {uploadStatus === 'uploading' && (
          <button
            className="cancel-button btn-secondary" // Use theme button style
            onClick={handleReset} // Cancel should reset
          >
            <i className="fas fa-times"></i> בטל העלאה
          </button>
        )}
         {(uploadStatus === 'error' || uploadStatus === 'success') && (
             <button
                 className="upload-new-button btn-secondary"
                 onClick={handleReset} // Reset to allow new upload
             >
                 <i className="fas fa-plus"></i> העלה קובץ נוסף
             </button>
         )}
      </div>
    </div>
  );
};

export default UploadWidget;