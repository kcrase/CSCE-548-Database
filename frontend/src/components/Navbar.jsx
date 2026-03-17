// src/components/Navbar.jsx
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',             icon: '◈', label: 'Dashboard'    },
  { to: '/statuses',     icon: '◉', label: 'Pipeline'     },
  { to: '/applications', icon: '◎', label: 'Applications' },
  { to: '/job-postings', icon: '◇', label: 'Job Postings' },
  { to: '/companies',    icon: '◆', label: 'Companies'    },
  { to: '/contacts',     icon: '◐', label: 'Contacts'     },
]

export default function Navbar() {
  return (
    <nav style={{
      width: 220,
      minWidth: 220,
      background: 'var(--bg-card)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
    }}>
      {/* Logo */}
      <div style={{ padding: '0 20px 28px' }}>
        <div style={{
          fontFamily: 'var(--font-display)',
          fontSize: 20,
          color: 'var(--accent)',
          letterSpacing: '-0.5px',
          lineHeight: 1.1,
        }}>
          Job<br />Tracker
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
          v1.0
        </div>
      </div>

      {/* Nav links */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2, padding: '0 12px' }}>
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '8px 12px',
              borderRadius: 'var(--radius)',
              fontSize: 13,
              fontWeight: 500,
              color: isActive ? 'var(--accent)' : 'var(--text-muted)',
              background: isActive ? 'var(--accent-dim)' : 'transparent',
              transition: 'all var(--transition)',
              textDecoration: 'none',
            })}
          >
            <span style={{ fontSize: 14, opacity: 0.8 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </div>

      {/* Footer */}
      <div style={{ padding: '16px 20px 0', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>
          CSCE 548
        </div>
      </div>
    </nav>
  )
}
