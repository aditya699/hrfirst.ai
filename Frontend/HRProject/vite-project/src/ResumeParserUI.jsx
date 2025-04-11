import React, { useState, useRef } from 'react';
import './ResumeParserUI.css';
import { FiUpload, FiFile, FiCheck, FiPaperclip } from 'react-icons/fi';
import axios from 'axios';

const ResumeParserUI = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResults, setUploadResults] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files);
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResults(null);
    
    console.log('Starting file upload process');
    
    // Create FormData object
    const formData = new FormData();
    
    // Use 'files' as the parameter name to match FastAPI's expectation
    selectedFiles.forEach(file => {
      console.log(`Adding file to form: ${file.name} (${file.size} bytes)`);
      formData.append('files', file);
    });

    try {
      console.log('Sending upload request to API...');
      
      // Track upload progress using axios
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      };

      // Use the correct API endpoint path
      const response = await axios.post(
        'http://127.0.0.1:8000/api/upload-files-process/',
        formData,
        config
      );
      
      console.log('Upload successful:', response.data);
      setUploadResults(response.data);
      
      // Optional: Clear files after successful upload
      // setSelectedFiles([]);
    } catch (error) {
      console.error('Error uploading files:', error);
      
      let errorMessage = 'An error occurred while uploading files.';
      
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
        
        errorMessage = `Server error: ${error.response.status} - ${
          error.response.data?.detail || 'Unknown error'
        }`;
      } else if (error.request) {
        // The request was made but no response was received
        console.error('Error request:', error.request);
        errorMessage = 'No response received from server. Please check if the server is running.';
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error message:', error.message);
        errorMessage = `Error: ${error.message}`;
      }
      
      setUploadError(errorMessage);
    } finally {
      // Keep progress at 100% for a moment before removing the overlay
      setUploadProgress(100);
      setTimeout(() => {
        setIsUploading(false);
      }, 500);
    }
  };

  return (
    <div className={`app-container ${isUploading ? 'uploading' : ''}`}>
      {isUploading && (
        <div className="overlay">
          <div className="progress-modal">
            <div className="progress-bar-container">
              <div 
                className="progress-bar-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="progress-percentage">{uploadProgress}% Complete</p>
            <p className="friendly-message">Grab a coffee or tea until the file processing completes!</p>
          </div>
        </div>
      )}
      <div className="sidebar">
        <div className="logo">HRFirst.ai</div>
        <nav className="nav-menu">
          <a href="#" className="nav-item active">
            <FiUpload className="nav-icon" />
            <span>Upload Resumes</span>
          </a>
        </nav>
      </div>
      <div className="centered-container">
      <div className="main-content">
        <div 
          className={`drop-zone ${isDragging ? 'active' : ''}`}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="drop-zone-content">
            <div className="upload-icon">
              <FiUpload />
            </div>
            <p className="drop-text">Drag and drop your resume files here</p>
            <p className="file-formats">Supports PDF, DOCX and DOC files</p>
            
            <button onClick={triggerFileInput} className="select-files-btn">
              Select Files
            </button>
            <input 
              ref={fileInputRef}
              type="file" 
              multiple 
              accept=".pdf,.docx,.doc" 
              onChange={handleFileSelect} 
              style={{ display: 'none' }}
            />
          </div>
        </div>
        
        {selectedFiles.length > 0 && (
          <div className="selected-files">
            <h3 className="selected-files-title">Selected Files ({selectedFiles.length})</h3>
            <div className="file-list">
              {selectedFiles.map((file, index) => (
                <div className="file-item" key={index}>
                  <div className="file-item-icon">
                    <FiPaperclip />
                  </div>
                  <div className="file-item-name">{file.name}</div>
                  <div className="file-item-size">{(file.size / 1024).toFixed(1)} KB</div>
                  <button 
                    className="file-item-remove" 
                    onClick={() => removeFile(index)}
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
            
            <div className="upload-actions">
              <button 
                className="upload-btn"
                onClick={handleUpload}
                disabled={isUploading}
              >
                Upload {selectedFiles.length} {selectedFiles.length === 1 ? 'File' : 'Files'}
              </button>
              <button 
                className="clear-btn"
                onClick={() => setSelectedFiles([])}
                disabled={isUploading}
              >
                Clear All
              </button>
            </div>
          </div>
        )}
        
        {uploadError && (
          <div className="error-message">
            <p>{uploadError}</p>
          </div>
        )}
        
        {uploadResults && Array.isArray(uploadResults) && uploadResults.length > 0 && (
          <div className="upload-results">
            <h3>Upload Results</h3>
            <div className="results-list">
              {uploadResults.map((result, index) => (
                <div className="result-item" key={index}>
                  <div className="result-icon">
                    <FiCheck />
                  </div>
                  <div className="result-name">{result.filename}</div>
                  <div className={`result-status ${result.status === 'error' ? 'error' : ''}`}>
                    {result.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
    </div>
  );
};

export default ResumeParserUI;