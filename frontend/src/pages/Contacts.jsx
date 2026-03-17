// src/pages/Contacts.jsx
import { useEffect, useState } from 'react'
import { getContacts, getCompanies, createContact, updateContact, deleteContact } from '../api/client'
import Modal from '../components/Modal'
import { useToast } from '../components/Toast'

const empty = { company_id: '', full_name: '', title: '', email: '', phone: '', linkedin: '' }

export default function Contacts() {
  const [rows, setRows]         = useState([])
  const [companies, setCompanies] = useState([])
  const [loading, setLoading]   = useState(true)
  const [modal, setModal]       = useState(null)
  const [form, setForm]         = useState(empty)
  const toast = useToast()

  const load = () => Promise.all([getContacts(), getCompanies()])
    .then(([c, co]) => { setRows(c); setCompanies(co) })
    .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const companyName = id => companies.find(c => c.company_id === id)?.name ?? '—'

  const openCreate = () => { setForm(empty); setModal('create') }
  const openEdit   = row => {
    setForm({
      company_id: row.company_id, full_name: row.full_name,
      title: row.title ?? '', email: row.email ?? '',
      phone: row.phone ?? '', linkedin: row.linkedin ?? '',
    })
    setModal(row)
  }

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSave = async () => {
    if (!form.company_id || !form.full_name) { toast('Company and name are required', 'error'); return }
    try {
      const payload = { ...form, company_id: Number(form.company_id) }
      if (modal === 'create') { await createContact(payload); toast('Contact created') }
      else { await updateContact(modal.contact_id, payload); toast('Contact updated') }
      setModal(null); load()
    } catch { toast('Something went wrong', 'error') }
  }

  const handleDelete = async row => {
    if (!confirm(`Delete "${row.full_name}"?`)) return
    try { await deleteContact(row.contact_id); toast('Contact deleted'); load() }
    catch { toast('Delete failed', 'error') }
  }

  if (loading) return <div className="loading"><div className="spinner" /> Loading…</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Contacts</h1>
          <p className="page-subtitle">{rows.length} contacts tracked</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Contact</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Title</th>
              <th>Company</th>
              <th>Email</th>
              <th>Phone</th>
              <th style={{ width: 100 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={6}><div className="empty-state"><h3>No contacts yet</h3></div></td></tr>
            )}
            {rows.map(row => (
              <tr key={row.contact_id}>
                <td style={{ fontWeight: 500 }}>{row.full_name}</td>
                <td className="td-muted">{row.title ?? '—'}</td>
                <td className="td-muted">{companyName(row.company_id)}</td>
                <td className="td-muted">{row.email ?? '—'}</td>
                <td className="td-muted">{row.phone ?? '—'}</td>
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
          title={modal === 'create' ? 'Add Contact' : `Edit — ${modal.full_name}`}
          onClose={() => setModal(null)}
          onSubmit={handleSave}
        >
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input value={form.full_name} onChange={set('full_name')} placeholder="Jane Doe" />
            </div>
            <div className="form-group">
              <label className="form-label">Title</label>
              <input value={form.title} onChange={set('title')} placeholder="Recruiter" />
            </div>
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
              <label className="form-label">Email</label>
              <input value={form.email} onChange={set('email')} placeholder="jane@company.com" />
            </div>
            <div className="form-group">
              <label className="form-label">Phone</label>
              <input value={form.phone} onChange={set('phone')} placeholder="555-0100" />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">LinkedIn</label>
            <input value={form.linkedin} onChange={set('linkedin')} placeholder="https://linkedin.com/in/…" />
          </div>
        </Modal>
      )}
    </div>
  )
}
