const TABS = [
  { id: 'chat',    icon: '📡', label: 'Channels' },
  { id: 'notes',  icon: '📄', label: 'Notes'    },
  { id: 'upload', icon: '⬆️', label: 'Upload'   },
  { id: 'profile',icon: '👤', label: 'Profile'  },
]

export default function BottomNav({ active, onChange }) {
  return (
    <nav className="bottom-nav">
      {TABS.map((t) => (
        <button
          key={t.id}
          className={`nav-btn ${active === t.id ? 'active' : ''}`}
          onClick={() => onChange(t.id)}
          aria-label={t.label}
        >
          <div className="nav-icon-wrap">{t.icon}</div>
          <span className="nav-label">{t.label}</span>
          <div className="nav-pip" />
        </button>
      ))}
    </nav>
  )
}
