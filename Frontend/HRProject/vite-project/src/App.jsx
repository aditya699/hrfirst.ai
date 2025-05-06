import React from 'react'
import ResumeParserUI from './components/ResumeParserUI'
import {BrowserRouter,Routes,Route} from 'react-router-dom'
import Dashboard from './components/Dashboard'

const App = () => {
  return (
    <>
     <BrowserRouter>
      <div>
          <Routes>
                <Route
                path="/"
                element={
                      <>
                         <ResumeParserUI/>
                      </>
                }  
                />
    
     <Route
                path="/candidates"
                element={
                      <>
                       <Dashboard/>
                      </>
                }  
                />



          </Routes>
        </div>
      </BrowserRouter>
   </>
  )
}

export default App