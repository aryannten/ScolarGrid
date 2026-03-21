/* Honeycomb SVG icon for the brand mark */
function HoneycombIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 2L20.57 7V17L12 22L3.43 17V7L12 2Z"
        fill="#d4a017"
        fillOpacity="0.9"
      />
      <path
        d="M12 6L17.14 9V15L12 18L6.86 15V9L12 6Z"
        fill="#080a07"
        fillOpacity="0.5"
      />
    </svg>
  )
}

const TABS = [
  { id: 'chat',    icon: '📡', label: 'Channels' },
  { id: 'notes',  icon: '📄', label: 'Notes'    },
  { id: 'upload', icon: '⬆️', label: 'Upload'   },
  { id: 'profile',icon: '👤', label: 'Profile'  },
]

export default function Sidebar({ active, onChange }) {
  return (
    <aside className="app-sidebar glass-sidebar">
      {/* Logo */}
      <div style={{
        marginBottom: 20, padding: '0 4px',
        display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10, flexShrink: 0,
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 16px rgba(212,160,23,0.35)',
        }}>
          <HoneycombIcon />
        </div>
        <span className="sidebar-label" style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 800, fontSize: 17,
          background: 'linear-gradient(135deg, var(--text-primary), var(--accent-primary))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}>
          ScholarGrid
        </span>
      </div>

      {/* Section label */}
      <div className="sidebar-label" style={{
        color: 'var(--text-dim)', fontSize: 10,
        fontFamily: 'var(--font-body)',
        letterSpacing: '0.12em', textTransform: 'uppercase',
        padding: '0 14px', marginBottom: 6,
      }}>
        Navigation
      </div>

      <div style={{ flex: 1, width: '100%' }}>
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`sidebar-btn ${active === t.id ? 'active' : ''}`}
            onClick={() => onChange(t.id)}
          >
            <span className="sidebar-icon">{t.icon}</span>
            <span className="sidebar-label">{t.label}</span>
          </button>
        ))}
      </div>

      {/* Bottom user hint */}
      <div className="sidebar-label" style={{
        marginTop: 'auto', width: '100%',
        padding: '12px 14px',
        borderTop: '1px solid var(--glass-border)',
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          fontSize: 12, color: 'var(--text-dim)',
          fontFamily: 'var(--font-body)',
        }}>
          <span style={{ fontSize: 16 }}>✨</span>
          <span>CE Sem 6</span>
        </div>
      </div>
    </aside>
  )
}
