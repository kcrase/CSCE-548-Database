// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ToastProvider } from './components/Toast'
import Navbar from './components/Navbar'
import Dashboard   from './pages/Dashboard'
import Companies   from './pages/Companies'
import Contacts    from './pages/Contacts'
import JobPostings from './pages/JobPostings'
import Applications from './pages/Applications'
import Statuses    from './pages/Statuses'

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <div className="app-shell">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/"             element={<Dashboard />}    />
              <Route path="/statuses"     element={<Statuses />}     />
              <Route path="/applications" element={<Applications />} />
              <Route path="/job-postings" element={<JobPostings />}  />
              <Route path="/companies"    element={<Companies />}    />
              <Route path="/contacts"     element={<Contacts />}     />
            </Routes>
          </main>
        </div>
      </ToastProvider>
    </BrowserRouter>
  )
}
