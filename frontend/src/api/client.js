// src/api/client.js
import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

// ── Companies ─────────────────────────────────────────────────────────
export const getCompanies    = ()         => http.get('/companies').then(r => r.data)
export const getCompany      = (id)       => http.get(`/companies/${id}`).then(r => r.data)
export const createCompany   = (data)     => http.post('/companies', data).then(r => r.data)
export const updateCompany   = (id, data) => http.put(`/companies/${id}`, data).then(r => r.data)
export const deleteCompany   = (id)       => http.delete(`/companies/${id}`)

// ── Contacts ──────────────────────────────────────────────────────────
export const getContacts     = ()         => http.get('/contacts').then(r => r.data)
export const getContact      = (id)       => http.get(`/contacts/${id}`).then(r => r.data)
export const createContact   = (data)     => http.post('/contacts', data).then(r => r.data)
export const updateContact   = (id, data) => http.put(`/contacts/${id}`, data).then(r => r.data)
export const deleteContact   = (id)       => http.delete(`/contacts/${id}`)

// ── Job Postings ──────────────────────────────────────────────────────
export const getJobPostings  = ()         => http.get('/job-postings').then(r => r.data)
export const getJobPosting   = (id)       => http.get(`/job-postings/${id}`).then(r => r.data)
export const createJobPosting = (data)    => http.post('/job-postings', data).then(r => r.data)
export const updateJobPosting = (id, data)=> http.put(`/job-postings/${id}`, data).then(r => r.data)
export const deleteJobPosting = (id)      => http.delete(`/job-postings/${id}`)

// ── Applications ──────────────────────────────────────────────────────
export const getApplications  = ()        => http.get('/applications').then(r => r.data)
export const getApplication   = (id)      => http.get(`/applications/${id}`).then(r => r.data)
export const createApplication = (data)   => http.post('/applications', data).then(r => r.data)
export const updateApplication = (id,data)=> http.put(`/applications/${id}`, data).then(r => r.data)
export const deleteApplication = (id)     => http.delete(`/applications/${id}`)

// ── Application Statuses ──────────────────────────────────────────────
export const getStatuses      = ()        => http.get('/application-statuses').then(r => r.data)
export const getStatus        = (id)      => http.get(`/application-statuses/${id}`).then(r => r.data)
export const createStatus     = (data)    => http.post('/application-statuses', data).then(r => r.data)
export const updateStatus     = (id,data) => http.put(`/application-statuses/${id}`, data).then(r => r.data)
export const deleteStatus     = (id)      => http.delete(`/application-statuses/${id}`)

export const STATUS_TYPES = [
  'SAVED', 'APPLIED', 'SCREEN', 'INTERVIEW',
  'ASSESSMENT', 'OFFER', 'ACCEPTED', 'REJECTED', 'WITHDRAWN', 'GHOSTED'
]

export const EMPLOYMENT_TYPES = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Remote']
