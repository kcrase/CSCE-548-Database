// src/pages/Statuses.jsx
import { useEffect, useState } from 'react'
import {
  getStatuses, getCompanies, getContacts, getJobPostings, getApplications,
  createStatus, updateStatus, deleteStatus, STATUS_TYPES
} from '../api/client'
import Modal from '../components/Modal'
import StatusBadge, { PriorityDots } from '../components/StatusBadge'
import { useToast } from '../components/Toast'

const empty = { company_id: '', contact_id: '', job_id: '', application_id: '', status: 'SAVED' }

export default function Statuses() {
  const [rows, setRows]           = useState([])
  const [companies, setCompanies] = useState([])
  const [contacts, setContacts]   = useState([])
  const [jobs, setJobs]           = useState([])
  const [apps, setApps]           = useState([])
  const [loading, setLoading]     = useState(true)
  const [modal, setModal]         = useState(null)
  const [form, setForm]           = useState(empty)
  const toast = useToast()

  const load = () => Promise.all([
    getStatuses(), getCompanies(), getContacts(), getJobPostings(), getApplications()
  ]).then(([s, co, ct, j, a]) => {
    setRows(s); setCompanies(co); setContacts(ct); setJobs(j); setApps(a)
  }).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const openCreate = () => { setForm(empty); setModal('create') }
  const openEdit   = row => {
    setForm({
      company_id:     row.company.company_id,
      contact_id:     row.contact?.contact_id ?? '',
      job_id:         row.job.job_id,
      application_id: row.application.application_id,
      status:         row.status,
    })
    setModal(row)
  }

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  // Filter contacts by selected company
  const filteredContacts = contacts.filter(c => !form.company_id || c.company_id === Number(form.company_id))
  // Filter jobs by selected company
  const filteredJobs = jobs.filter(j => !form.company_id || j.company_id === Number(form.company_id))
  // Filter apps by selected job
  const filteredApps = apps.filter(a => !form.job_id || a.job_id === Number(form.job_id))

  const handleSave = async () => {
    if (!form.company_id || !form.job_id || !form.application_id) {
      toast('Company, job posting, and application are required', 'error'); return
    }
    try {
      const payload = {
        company_id:     Number(form.company_id),
        contact_id:     form.contact_id ? Number(form.contact_id) : null,
        job_id:         Number(form.job_id),
        application_id: Number(form.application_id),
        status:         form.status,
      }
      if (modal === 'create') { await createStatus(payload); toast('Status created') }
      else { await updateStatus(modal.status_id, payload); toast('Status updated') }
      setModal(null); load()
    } catch { toast('Something went wrong', 'error') }
  }

  const handleDelete = async row => {
    if (!confirm(`Delete this status entry?`)) return
    try { await deleteStatus(row.status_id); toast('Status deleted'); load() }
    catch { toast('Delete failed', 'error') }
  }

  // Quick advance — bump to next status
  const handleAdvance = async row => {
    const idx = STATUS_TYPES.indexOf(row.status)
    if (idx >= STATUS_TYPES.length - 1) return
    const next = STATUS_TYPES[idx + 1]
    try {
      await updateStatus(row.status_id, {
        company_id:     row.company.company_id,
        contact_id:     row.contact?.contact_id ?? null,
        job_id:         row.job.job_id,
        application_id: row.application.application_id,
        status:         next,
      })
      toast(`Advanced to ${next}`)
      load()
    } catch { toast('Update failed', 'error') }
  }

  if (loading) return <div className="loading"><div className="spinner" /> Loading pipeline…</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Pipeline</h1>
          <p className="page-subtitle">{rows.length} status entries tracked</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Status</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Job Title</th>
              <th>Company</th>
              <th>Contact</th>
              <th>Source</th>
              <th>Priority</th>
              <th style={{ width: 160 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={7}><div className="empty-state"><h3>No statuses yet</h3><p>Start tracking by adding your first application status</p></div></td></tr>
            )}
            {rows.map(row => {
              const canAdvance = STATUS_TYPES.indexOf(row.status) < STATUS_TYPES.length - 1
              return (
                <tr key={row.status_id}>
                  <td><StatusBadge status={row.status} /></td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{row.job.job_title}</div>
                    {row.job.job_location && <div className="td-muted">{row.job.job_location}</div>}
                  </td>
                  <td>
                    <div>{row.company.name}</div>
                    {row.company.company_location && <div className="td-muted">{row.company.company_location}</div>}
                  </td>
                  <td className="td-muted">
                    {row.contact ? (
                      <div>
                        <div>{row.contact.full_name}</div>
                        <div style={{ fontSize: 11 }}>{row.contact.title}</div>
                      </div>
                    ) : '—'}
                  </td>
                  <td className="td-muted">{row.application.source ?? '—'}</td>
                  <td><PriorityDots priority={row.application.priority ?? 0} /></td>
                  <td>
                    <div className="action-row">
                      {canAdvance && (
                        <button className="btn btn-ghost btn-sm" onClick={() => handleAdvance(row)} title="Advance to next status">→</button>
                      )}
                      <button className="btn btn-ghost btn-sm" onClick={() => openEdit(row)}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(row)}>Del</button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {modal && (
        <Modal
          title={modal === 'create' ? 'Add Application Status' : 'Edit Status'}
          onClose={() => setModal(null)}
          onSubmit={handleSave}
        >
          <div className="form-group">
            <label className="form-label">Status *</label>
            <select value={form.status} onChange={set('status')}>
              {STATUS_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Company *</label>
            <select value={form.company_id} onChange={e => {
              setForm(f => ({ ...f, company_id: e.target.value, contact_id: '', job_id: '', application_id: '' }))
            }}>
              <option value="">Select a company…</option>
              {companies.map(c => <option key={c.company_id} value={c.company_id}>{c.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Contact (optional)</label>
            <select value={form.contact_id} onChange={set('contact_id')}>
              <option value="">No contact</option>
              {filteredContacts.map(c => <option key={c.contact_id} value={c.contact_id}>{c.full_name} — {c.title ?? ''}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Job Posting *</label>
            <select value={form.job_id} onChange={e => {
              setForm(f => ({ ...f, job_id: e.target.value, application_id: '' }))
            }}>
              <option value="">Select a job posting…</option>
              {filteredJobs.map(j => <option key={j.job_id} value={j.job_id}>{j.job_title}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Application *</label>
            <select value={form.application_id} onChange={set('application_id')}>
              <option value="">Select an application…</option>
              {filteredApps.map(a => (
                <option key={a.application_id} value={a.application_id}>
                  App #{a.application_id} — {a.source ?? 'No source'} {a.applied_date ? `(${a.applied_date})` : ''}
                </option>
              ))}
            </select>
          </div>
        </Modal>
      )}
    </div>
  )
}
