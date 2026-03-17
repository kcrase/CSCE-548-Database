// src/pages/Dashboard.jsx
import { useEffect, useState } from 'react'
import { getStatuses, STATUS_TYPES } from '../api/client'
import StatusBadge, { PriorityDots } from '../components/StatusBadge'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const [statuses, setStatuses] = useState([])
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    getStatuses()
      .then(setStatuses)
      .finally(() => setLoading(false))
  }, [])

  // Group by most recent status per application
  const byStatus = STATUS_TYPES.reduce((acc, s) => ({ ...acc, [s]: [] }), {})
  statuses.forEach(s => {
    if (byStatus[s.status]) byStatus[s.status].push(s)
  })

  const total       = statuses.length
  const active      = statuses.filter(s => !['REJECTED','WITHDRAWN','GHOSTED','ACCEPTED'].includes(s.status)).length
  const offers      = byStatus['OFFER'].length + byStatus['ACCEPTED'].length
  const interviews  = byStatus['INTERVIEW'].length

  if (loading) return <div className="loading"><div className="spinner" /> Loading pipeline…</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Your job search pipeline at a glance</p>
        </div>
        <Link to="/statuses" className="btn btn-primary">+ New Status</Link>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {[
          { value: total,      label: 'Total Tracked'   },
          { value: active,     label: 'Active'          },
          { value: interviews, label: 'Interviews'      },
          { value: offers,     label: 'Offers'          },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Kanban */}
      <div className="kanban">
        {STATUS_TYPES.map(status => {
          const cards = byStatus[status]
          return (
            <div key={status} className="kanban-col">
              <div className="kanban-col-header">
                <span className="kanban-col-title">
                  <StatusBadge status={status} />
                </span>
                <span className="kanban-count">{cards.length}</span>
              </div>
              <div className="kanban-cards">
                {cards.length === 0 && (
                  <div style={{ padding: '12px 0', textAlign: 'center', color: 'var(--text-dim)', fontSize: 12 }}>
                    —
                  </div>
                )}
                {cards.map(s => (
                  <div key={s.status_id} className="kanban-card">
                    <div className="kanban-card-title">{s.job.job_title}</div>
                    <div className="kanban-card-company">{s.company.name}</div>
                    <div className="kanban-card-meta">
                      <PriorityDots priority={s.application.priority ?? 0} />
                      {s.job.job_location && (
                        <span style={{ marginLeft: 'auto' }}>{s.job.job_location}</span>
                      )}
                    </div>
                    {s.contact && (
                      <div style={{ marginTop: 6, fontSize: 11, color: 'var(--text-dim)' }}>
                        ◐ {s.contact.full_name}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
