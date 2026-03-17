// src/pages/Companies.jsx
import { useEffect, useState } from 'react'
import { getCompanies, createCompany, updateCompany, deleteCompany } from '../api/client'
import Modal from '../components/Modal'
import { useToast } from '../components/Toast'

const empty = { name: '', website: '', company_location: '' }

export default function Companies() {
  const [rows, setRows]       = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal]     = useState(null)   // null | 'create' | row
  const [form, setForm]       = useState(empty)
  const toast = useToast()

  const load = () => getCompanies().then(setRows).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const openCreate = () => { setForm(empty); setModal('create') }
  const openEdit   = row => { setForm({ name: row.name, website: row.website ?? '', company_location: row.company_location ?? '' }); setModal(row) }

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSave = async () => {
    try {
      if (modal === 'create') {
        await createCompany(form)
        toast('Company created')
      } else {
        await updateCompany(modal.company_id, form)
        toast('Company updated')
      }
      setModal(null)
      load()
    } catch { toast('Something went wrong', 'error') }
  }

  const handleDelete = async row => {
    if (!confirm(`Delete "${row.name}"?`)) return
    try {
      await deleteCompany(row.company_id)
      toast('Company deleted')
      load()
    } catch { toast('Delete failed', 'error') }
  }

  if (loading) return <div className="loading"><div className="spinner" /> Loading…</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Companies</h1>
          <p className="page-subtitle">{rows.length} companies tracked</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Company</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Website</th>
              <th>Location</th>
              <th style={{ width: 100 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={4}><div className="empty-state"><h3>No companies yet</h3><p>Add your first company to get started</p></div></td></tr>
            )}
            {rows.map(row => (
              <tr key={row.company_id}>
                <td style={{ fontWeight: 500 }}>{row.name}</td>
                <td>
                  {row.website
                    ? <a href={row.website} target="_blank" rel="noreferrer" className="td-muted">{row.website}</a>
                    : <span className="td-muted">—</span>}
                </td>
                <td className="td-muted">{row.company_location ?? '—'}</td>
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
          title={modal === 'create' ? 'Add Company' : `Edit — ${modal.name}`}
          onClose={() => setModal(null)}
          onSubmit={handleSave}
        >
          <div className="form-group">
            <label className="form-label">Company Name *</label>
            <input value={form.name} onChange={set('name')} placeholder="Acme Corp" />
          </div>
          <div className="form-group">
            <label className="form-label">Website</label>
            <input value={form.website} onChange={set('website')} placeholder="https://acme.com" />
          </div>
          <div className="form-group">
            <label className="form-label">Location</label>
            <input value={form.company_location} onChange={set('company_location')} placeholder="Remote, Austin TX…" />
          </div>
        </Modal>
      )}
    </div>
  )
}
