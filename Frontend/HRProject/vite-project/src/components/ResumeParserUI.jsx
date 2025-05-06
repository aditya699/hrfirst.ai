import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Paperclip, X } from 'lucide-react';
import axios from 'axios';
import './ResumeParserUI.css';
import Sidebar from './sidebar/Sidebar';

const ResumeParserUI = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [displayProgress, setDisplayProgress] = useState(0);
  const [uploadResults, setUploadResults] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);
  useEffect(() => {
    if (!isUploading) {
      setDisplayProgress(0);
      return;
    }
    const STEP = 0.8;
    const INTERVAL = 30;
    const id = setInterval(() => {
      setDisplayProgress(prev => {
        const target = Math.min(
          uploadProgress >= 99 ? 99 : uploadProgress,
          100
        );
        if (prev + STEP < target) return prev + STEP;
        if (prev < target) return target;
        return prev;
      });
    }, INTERVAL);

    return () => clearInterval(id);
  }, [uploadProgress, isUploading]);

  const processResumesForDashboard = (apiResponse) => {
    if (!apiResponse.details) return [];
    return Object.keys(apiResponse.details).map((fileName) => {
      const d = apiResponse.details[fileName] || {};
      return {
        name: d.name || 'Unknown',
        fileName,
        email: d.email || '',
        phone: d.phone || '',
        education: d.education || '',
        experience: d.experience || '',
        skills: d.skills || '',
        status: 'New',
      };
    });
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.length) {
      setSelectedFiles((p) => [...p, ...Array.from(e.dataTransfer.files)]);
    }
  };
  const handleFileSelect = (e) => {
    if (e.target.files?.length) {
      setSelectedFiles((p) => [...p, ...Array.from(e.target.files)]);
    }
  };
  const removeFile = (i) =>
    setSelectedFiles((p) => p.filter((_, idx) => idx !== i));
  const triggerFileInput = () => fileInputRef.current.click();
  const handleUpload = async () => {
    if (!selectedFiles.length) return;
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResults(null);

    const formData = new FormData();
    selectedFiles.forEach((f) => formData.append('files', f));
    formData.append('session_cookie', '123');

    try {
      const config = {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: ({ loaded, total }) =>
          setUploadProgress(Math.round((loaded * 100) / total)),
      };
      const res = await axios.post(
        'http://127.0.0.1:8000/api/upload-files-process/',
        formData,
        config
      );
      setUploadResults(res.data);
      const dashboard = processResumesForDashboard(res.data);
      const existing = JSON.parse(sessionStorage.getItem('candidates') || '[]');
      const updating = [...existing, ...dashboard];
      sessionStorage.setItem(
        'candidates',
        JSON.stringify(dashboard)
      );
    } catch (err) {
      const msg =
        err.response
          ? `Server error: ${err.response.status} - ${err.response.data?.detail || 'Unknown error'
          }`
          : err.request
            ? 'No response received from server. Please check if the server is running.'
            : `Error: ${err.message}`;
      setUploadError(msg);
    } finally {
      setUploadProgress(100);
      setTimeout(() => {
        setIsUploading(false);
        window.location.href = '/candidates';
      }, 500);
    }
  };

  const renderUploadResults = () =>
    uploadResults && (
      <div className="results-container">
        <h3 className="results-title">Upload Results</h3>
        <div className="results-content">
          {uploadResults.message && <p>{uploadResults.message}</p>}
          {uploadResults.job_description && (
            <div className="parsed-data">
              <h4>Job Description</h4>
              <div className="job-description-content">
                {typeof uploadResults.job_description === 'string'
                  ? uploadResults.job_description
                  : Object.entries(uploadResults.job_description).map(
                    ([k, v]) => (
                      <div className="job-field" key={k}>
                        <strong>{k.replace(/_/g, ' ').toUpperCase()}:</strong>{' '}
                        {v}
                      </div>
                    )
                  )}
              </div>
            </div>
          )}
        </div>
      </div>
    );

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* progress overlay */}
      {isUploading && (
        <div className="upload-overlay">
          <div className="progress-modal">
            <h3>Uploading Files</h3>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${displayProgress}%` }}
              />
            </div>
            <p className="progress-percentage">
              {displayProgress.toFixed(0)}% Complete
            </p>
            <p className="friendly-message">
              Grab a coffee or tea until the file processing completes!
              <br />
              We're extracting and analyzing the resume data.
            </p>
          </div>
        </div>
      )}
      <Sidebar />
      <div className="main-content">
        <div className="hero-section">
          <div className="container">
            <h1 className="hero-title">
              Transform Resume Processing with <span className="highlight">AI</span>
            </h1>
            <p className="hero-description">
              Upload multiple resumes and instantly extract key candidate details,
              skills, and qualifications with our advanced{' '}
              <span className="highlight">AI</span> technology.
            </p>

            <div
              className={`upload-area ${isDragging ? 'dragging' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="upload-icon-container">
                <div className="upload-icon">
                  <ArrowUp className="arrow-icon" />
                </div>
              </div>

              <div className="upload-content">
                <h3 className="upload-title">
                  Drag and drop your resume files here
                </h3>
                <p className="upload-description">
                  Our <span className="highlight">AI</span> will automatically
                  extract and organize all important candidate information
                </p>
                <p className="upload-formats">
                  Supports PDF, DOCX and DOC files
                </p>
              </div>

              <div className="upload-button-container">
                <button className="upload-button" onClick={triggerFileInput}>
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

            {/* selected files */}
            {!!selectedFiles.length && (
              <div className="selected-files-container">
                <h3 className="selected-files-title">
                  Selected Files ({selectedFiles.length})
                </h3>
                <div className="file-list">
                  {selectedFiles.map((f, i) => (
                    <div className="file-item" key={i}>
                      <div className="file-item-icon">
                        <Paperclip size={16} />
                      </div>
                      <div className="file-item-name">{f.name}</div>
                      <div className="file-item-size">
                        {(f.size / 1024).toFixed(1)} KB
                      </div>
                      <button
                        className="file-item-remove"
                        onClick={() => removeFile(i)}
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>

                <div className="upload-actions">
                  <button
                    className="action-button upload-btn"
                    onClick={handleUpload}
                    disabled={isUploading}
                  >
                    Upload {selectedFiles.length}{' '}
                    {selectedFiles.length === 1 ? 'File' : 'Files'}
                  </button>
                  <button
                    className="action-button clear-btn"
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

            {renderUploadResults()}
          </div>
        </div>

        {/* Features Section */}
        <div className="features-section">
          <div className="container">
            <h2 className="section-title">Key Features</h2>

            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">
                  <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="feature-title">Bulk Processing</h3>
                <p className="feature-description">Upload and process multiple resumes simultaneously with high accuracy</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
                <h3 className="feature-title">Smart Extraction</h3>
                <p className="feature-description">AI-powered parsing extracts skills, experience, education, and contact details</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="feature-title">Advanced Analytics</h3>
                <p className="feature-description">Get insights on candidate pools and make data-driven hiring decisions</p>
              </div>
            </div>
          </div>
        </div>

        {/* Mission Statement */}
        <div className="mission-section">
          <div className="mission-container">
            <h2 className="mission-title">Our Mission</h2>
            <p className="mission-text">
              At <span className="highlight">HR</span>First.ai, we don't replace <span className="highlight">HR</span> professionals—we empower them. We believe that by automating repetitive tasks through advanced <span className="highlight">AI</span>, we free up human resources teams to focus on what they do best: building meaningful connections and creating exceptional workplace cultures.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ResumeParserUI;
