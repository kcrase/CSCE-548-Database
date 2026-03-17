// src/components/StatusBadge.jsx
export default function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{status}</span>
}

export function PriorityDots({ priority = 0, max = 5 }) {
  return (
    <span className="priority">
      {Array.from({ length: max }, (_, i) => (
        <span key={i} className={`priority-dot${i < priority ? ' active' : ''}`} />
      ))}
    </span>
  )
}
