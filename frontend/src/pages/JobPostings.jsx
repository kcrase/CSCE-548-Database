// src/pages/JobPostings.jsx
import { useEffect, useState } from 'react'
import { getJobPostings, getCompanies, createJobPosting, updateJobPosting, deleteJobPosting, EMPLOYMENT_TYPES } from '../api/client'
import Modal from '../components/Modal'
import { useToast } from '../components/Toast'

const empty = { company_id: '', job_title: '', job_location: '', employment_type: '', job_url: '', salary: '', posted_date: '' }

export default function JobPostings() {
  const [rows, setRows]         = useState([])
  const [companies, setCompanies] = useState([])
  const [loading, setLoading]   = useState(true)
  const [modal, setModal]       = useState(null)
  const [form, setForm]         = useState(empty)
  const toast = useToast()

  const load = () => Promise.all([getJobPostings(), getCompanies()])
    .then(([j, c]) => { setRows(j); setCompanies(c) })
    .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const companyName = id => companies.find(c => c.company_id === id)?.name ?? '—'

  const openCreate = () => { setForm(empty); setModal('create') }
  const openEdit   = row => {
    setForm({
      company_id: row.company_id, job_title: row.job_title,
      job_location: row.job_location ?? '', employment_type: row.employment_type ?? '',
      job_url: row.job_url ?? '', salary: row.salary ?? '', posted_date: row.posted_date ?? '',
    })
    setModal(row)
  }

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSave = async () => {
    if (!form.company_id || !form.job_title) { toast('Company and job title are required', 'error'); return }
    try {
      const payload = {
        ...form,
        company_id: Number(form.company_id),
        salary: form.salary ? Number(form.salary) : null,
        posted_date: form.posted_date || null,
      }
      if (modal === 'create') { await createJobPosting(payload); toast('Job posting created') }
      else { await updateJobPosting(modal.job_id, payload); toast('Job posting updated') }
      setModal(null); load()
    } catch { toast('Something went wrong', 'error') }
  }

  const handleDelete = async row => {
    if (!confirm(`Delete "${row.job_title}"?`)) return
    try { await deleteJobPosting(row.job_id); toast('Job posting deleted'); load() }
    catch { toast('Delete failed — it may have linked applications', 'error') }
  }

  if (loading) return <div className="loading"><div className="spinner" /> Loading…</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Job Postings</h1>
          <p className="page-subtitle">{rows.length} positions tracked</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Posting</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Company</th>
              <th>Location</th>
              <th>Type</th>
              <th>Salary</th>
              <th>Posted</th>
              <th style={{ width: 100 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={7}><div className="empty-state"><h3>No job postings yet</h3></div></td></tr>
            )}
            {rows.map(row => (
              <tr key={row.job_id}>
                <td>
                  <div style={{ fontWeight: 500 }}>{row.job_title}</div>
                  {row.job_url && <a href={row.job_url} target="_blank" rel="noreferrer" className="td-muted" style={{ fontSize: 11 }}>↗ View posting</a>}
                </td>
                <td className="td-muted">{companyName(row.company_id)}</td>
                <td className="td-muted">{row.job_location ?? '—'}</td>
                <td className="td-muted">{row.employment_type ?? '—'}</td>
                <td className="td-mono">{row.salary ? `$${Number(row.salary).toLocaleString()}` : '—'}</td>
                <td className="td-muted">{row.posted_date ?? '—'}</td>
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
          title={modal === 'create' ? 'Add Job Posting' : `Edit — ${modal.job_title}`}
          onClose={() => setModal(null)}
          onSubmit={handleSave}
        >
          <div className="form-group">
            <label className="form-label">Job Title *</label>
            <input value={form.job_title} onChange={set('job_title')} placeholder="Software Engineer" />
          </div>
          <div className="form-group">
            <label className="form-label">Company *</label>
            <select value={form.company_id} onChange={set('company_id')}>
              <option value="">Select a company…</option>
              {companies.map(c => <option key={c.company_id} value={c.company_id}>{c.name}</option>)}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Location</label>
              <input value={form.job_location} onChange={set('job_location')} placeholder="Remote, Austin TX…" />
            </div>
            <div className="form-group">
              <label className="form-label">Employment Type</label>
              <select value={form.employment_type} onChange={set('employment_type')}>
                <option value="">Select…</option>
                {EMPLOYMENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Job URL</label>
            <input value={form.job_url} onChange={set('job_url')} placeholder="https://…" />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Salary</label>
              <input type="number" value={form.salary} onChange={set('salary')} placeholder="85000" />
            </div>
            <div className="form-group">
              <label className="form-label">Posted Date</label>
              <input type="date" value={form.posted_date} onChange={set('posted_date')} />
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
