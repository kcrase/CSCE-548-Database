// src/pages/Applications.jsx
import { useEffect, useState } from 'react'
import { getApplications, getJobPostings, createApplication, updateApplication, deleteApplication } from '../api/client'
import Modal from '../components/Modal'
import { PriorityDots } from '../components/StatusBadge'
import { useToast } from '../components/Toast'

const empty = { job_id: '', applied_date: '', source: '', priority: '3', resume: '' }

const SOURCES = ['LinkedIn', 'Indeed', 'Company Website', 'Referral', 'Glassdoor', 'Handshake', 'Other']

export default function Applications() {
  const [rows, setRows]       = useState([])
  const [jobs, setJobs]       = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal]     = useState(null)
  const [form, setForm]       = useState(empty)
  const toast = useToast()

  const load = () => Promise.all([getApplications(), getJobPostings()])
    .then(([a, j]) => { setRows(a); setJobs(j) })
    .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const jobTitle = id => jobs.find(j => j.job_id === id)?.job_title ?? '—'

  const openCreate = () => { setForm(empty); setModal('create') }
  const openEdit   = row => {
    setForm({
      job_id: row.job_id, applied_date: row.applied_date ?? '',
      source: row.source ?? '', priority: String(row.priority ?? 3),
      resume: row.resume ?? '',
    })
    setModal(row)
  }

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSave = async () => {
    if (!form.job_id) { toast('Job posting is required', 'error'); return }
    try {
      const payload = {
        job_id: Number(form.job_id),
        applied_date: form.applied_date || null,
        source: form.source || null,
        priority: form.priority ? Number(form.priority) : null,
        resume: form.resume || null,
      }
      if (modal === 'create') { await createApplication(payload); toast('Application created') }
      else { await updateApplication(modal.application_id, payload); toast('Application updated') }
      setModal(null); load()
    } catch { toast('Something went wrong', 'error') }
  }

  const handleDelete = async row => {
    if (!confirm(`Delete this application for "${jobTitle(row.job_id)}"?`)) return
    try { await deleteApplication(row.application_id); toast('Application deleted'); load() }
    catch { toast('Delete failed — it may have linked statuses', 'error') }
  }

  if (loading) return <div className="loading"><div className="spinner" /> Loading…</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Applications</h1>
          <p className="page-subtitle">{rows.length} applications tracked</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Application</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Job</th>
              <th>Applied</th>
              <th>Source</th>
              <th>Priority</th>
              <th>Resume</th>
              <th style={{ width: 100 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={6}><div className="empty-state"><h3>No applications yet</h3></div></td></tr>
            )}
            {rows.map(row => (
              <tr key={row.application_id}>
                <td style={{ fontWeight: 500 }}>{jobTitle(row.job_id)}</td>
                <td className="td-muted">{row.applied_date ?? '—'}</td>
                <td className="td-muted">{row.source ?? '—'}</td>
                <td><PriorityDots priority={row.priority ?? 0} /></td>
                <td className="td-muted">{row.resume ?? '—'}</td>
                <td>
                  <div className="action-row">
                    <button className="btn btn-ghost btn-sm" onClick={() => openEdit(row)}>Edit</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(row)}>Del</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <Modal
          title={modal === 'create' ? 'Add Application' : 'Edit Application'}
          onClose={() => setModal(null)}
          onSubmit={handleSave}
        >
          <div className="form-group">
            <label className="form-label">Job Posting *</label>
            <select value={form.job_id} onChange={set('job_id')}>
              <option value="">Select a job posting…</option>
              {jobs.map(j => <option key={j.job_id} value={j.job_id}>{j.job_title}</option>)}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Applied Date</label>
              <input type="date" value={form.applied_date} onChange={set('applied_date')} />
            </div>
            <div className="form-group">
              <label className="form-label">Priority (1–5)</label>
              <input type="number" min="1" max="5" value={form.priority} onChange={set('priority')} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Source</label>
            <select value={form.source} onChange={set('source')}>
              <option value="">Select source…</option>
              {SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Resume Path</label>
            <input value={form.resume} onChange={set('resume')} placeholder="/resumes/my_resume.pdf" />
          </div>
        </Modal>
      )}
    </div>
  )
}
