import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
} from 'lucide-react';
import './Dashboard.css';
import Sidebar from './sidebar/Sidebar';

const Dashboard = () => {
  const [candidateData, setCandidateData] = useState([]);
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [searchQuery, setSearchQuery] = useState('');

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file); // must match your backend field name

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/upload-files-process/',
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      setCandidateData(data);
      sessionStorage.setItem('candidates', JSON.stringify(data));
    } catch (error) {
      console.error('File upload error:', error);
    }
  };

  useEffect(() => {
    const stored = sessionStorage.getItem('candidates');
    if (stored) {
      setCandidateData(JSON.parse(stored));
    }
  }, []);

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSorted = [...candidateData]
    .filter(
      (c) =>
        !searchQuery ||
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.skills.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      const aVal = a[sortField] || '';
      const bVal = b[sortField] || '';
      return sortDirection === 'asc'
        ? aVal.toString().localeCompare(bVal.toString())
        : bVal.toString().localeCompare(aVal.toString());
    });

  const sortIcon = (field) =>
    sortField === field ? (
      sortDirection === 'asc' ? (
        <ChevronUp className="sort-icon" />
      ) : (
        <ChevronDown className="sort-icon" />
      )
    ) : null;

  return (
    <>
      <Sidebar />
      <div className="candidates-container">
        <div className="header-section">
          <div className="controls">
            <div className="search-container">
              <div className="search-icon">
                <Search />
              </div>
              <input
                type="text"
                placeholder="Search candidates..."
                className="search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="action-buttons">
              <button className="filter-button">
                <Filter className="filter-icon" />
                Filter
              </button>
              <label className="add-button">
                Upload Resume
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    if (e.target.files.length > 0) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                />
              </label>
            </div>
          </div>
        </div>

        <div className="table-container">
          <table className="candidates-table">
            <thead>
              <tr>
                <th
                  className="sortable-header"
                  onClick={() => handleSort('name')}
                >
                  <div className="header-content">
                    Name {sortIcon('name')}
                  </div>
                </th>
                <th>Contact</th>
                <th
                  className="sortable-header"
                  onClick={() => handleSort('education')}
                >
                  <div className="header-content">
                    Education {sortIcon('education')}
                  </div>
                </th>
                <th
                  className="sortable-header"
                  onClick={() => handleSort('experience')}
                >
                  <div className="header-content">
                    Experience {sortIcon('experience')}
                  </div>
                </th>
                <th
                  className="sortable-header"
                  onClick={() => handleSort('skills')}
                >
                  <div className="header-content">
                    Skills {sortIcon('skills')}
                  </div>
                </th>
                <th className="actions-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSorted.map((c) => (
                <tr key={c.email} className="candidate-row">
                  <td>
                    <div className="candidate-name">
                      <div className="avatar">
                        <span>{c.name.charAt(0)}</span>
                      </div>
                      <div className="name-info">
                        <div className="name">{c.name}</div>
                        <div className="file-name">{c.fileName}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="contact-info">
                      <div className="email">{c.email}</div>
                      <div className="phone">{c.phone}</div>
                    </div>
                  </td>
                  <td>
                    <div className="education">{c.education}</div>
                  </td>
                  <td>
                    <div className="experience">{c.experience}</div>
                  </td>
                  <td>
                    <div className="skills-container">
                      {c.skills
                        .split(',')
                        .slice(0, 3)
                        .map((skill) => (
                          <span
                            key={`${c.email}-${skill.trim()}`}
                            className="skill-tag"
                          >
                            {skill.trim()}
                          </span>
                        ))}
                      {c.skills.split(',').length > 3 && (
                        <span className="more-skills">
                          +{c.skills.split(',').length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="actions">
                      <button className="view-button">View</button>
                      <button className="more-button">
                        <MoreHorizontal />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="pagination">
          <div className="results-count">
            Showing {filteredAndSorted.length} of {candidateData.length} candidates
          </div>
          <div className="page-controls">
            <button className="prev-button" disabled>
              Previous
            </button>
            <button className="page-button active">1</button>
            <button className="page-button">2</button>
            <button className="next-button">Next</button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
