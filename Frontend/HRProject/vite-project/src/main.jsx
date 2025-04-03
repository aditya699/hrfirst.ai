import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import ResumeParserUI from './ResumeParserUI.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ResumeParserUI/>
  </StrictMode>,
)
