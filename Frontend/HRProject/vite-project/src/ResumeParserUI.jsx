import React, { useState, useRef } from 'react';
import './ResumeParserUI.css';
import { FiUpload, FiFile, FiCheck, FiPaperclip } from 'react-icons/fi';

const ResumeParserUI = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
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

  // Features data
  const features = [
    {
      id: 1,
      title: 'Contact Information',
      description: 'Automatically extract name, email, phone number'
    },
    {
      id: 2,
      title: 'Work Experience',
      description: 'Parse job titles, companies, and timelines'
    },
    {
      id: 3,
      title: 'Education',
      description: 'Extract degrees, institutions, and graduation dates'
    },
    {
      id: 4,
      title: 'Skills Analysis',
      description: 'Identify technical and soft skills from content'
    }
  ];

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="logo">HRFirst.ai</div>
        <nav className="nav-menu">
          <a href="#" className="nav-item active">
            <FiUpload className="nav-icon" />
            <span>Upload Resumes</span>
          </a>
          {/* <a href="#" className="nav-item">
            <FiFile className="nav-icon" />
            <span>All Resumes</span>
          </a> */}
        </nav>
      </div>
      
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
              <button className="upload-btn">
                Upload {selectedFiles.length} {selectedFiles.length === 1 ? 'File' : 'Files'}
              </button>
              <button 
                className="clear-btn"
                onClick={() => setSelectedFiles([])}
              >
                Clear All
              </button>
            </div>
          </div>
        )}
        
        {/* <div className="features-section">
          <h2 className="features-title">Supported Features</h2>
          
          {features.map(feature => (
            <div className="feature-card" key={feature.id}>
              <div className="feature-icon">
                <FiCheck className="check-icon" />
              </div>
              <div className="feature-content">
                <h3 className="feature-name">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            </div>
          ))}
        </div> */}
      </div>
    </div>
  );
};

export default ResumeParserUI;