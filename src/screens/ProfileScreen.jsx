import Avatar from '../components/Avatar'
import { avg, fileIcon } from '../utils/helpers'
import { useTheme } from '../context/ThemeContext'

const SETTINGS = [
  { icon: '🔔', label: 'Notifications',      right: ''         },
  { icon: '🔒', label: 'Privacy & Security', right: ''         },
  { icon: '🏫', label: 'My Class',           right: 'CE Sem 6' },
  { icon: '📊', label: 'Grade Analytics',    right: ''         },
  { icon: '❓', label: 'Help & Support',     right: ''         },
  { icon: '⭐', label: 'Rate the App',       right: ''         },
]

export default function ProfileScreen({ currentUser, notes, onLogout }) {
  const { isDark } = useTheme()

  if (!currentUser) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)' }}>
        Loading profile…
      </div>
    )
  }

  const userName = currentUser.name || 'StudyHive User'
  const userRole = currentUser.role || 'student'
  const mine     = notes.filter(n => n.uid === currentUser.id)
  const totalDl  = mine.reduce((a, n) => a + n.dl, 0)
  const allR     = mine.flatMap(n => n.ratings)

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative', zIndex: 2 }}>
      <div className="scroll-y" style={{ flex: 1 }}>

        {/* Hero banner */}
        <div className="profile-hero">
          {/* Top-right actions */}
          <div style={{ position: 'absolute', top: 16, right: 16, display: 'flex', gap: 8 }}>
            <button
              className="btn-ghost"
              onClick={onLogout}
              style={{ padding: '7px 14px', fontSize: 13 }}
            >
              Sign out
            </button>
          </div>

          <div className="profile-avatar">{currentUser.av}</div>

          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 22, fontWeight: 900, marginBottom: 8,
            color: '#080a07', letterSpacing: '-0.5px',
          }}>
            {userName}
          </h2>

          <span className="profile-badge">
            {userRole === 'teacher' ? '👨‍🏫 Teacher' : '🎓 Student · CE Sem 6'}
          </span>
        </div>

        {/* Stats row — overlaps hero */}
        <div style={{ display: 'flex', gap: 10, padding: '16px 16px 0', marginTop: -30 }}>
          {[
            ['📄', mine.length, 'Notes'],
            ['⬇️', totalDl, 'Downloads'],
            ['⭐', avg(allR), 'Avg Rating'],
          ].map(([ic, v, lb]) => (
            <div key={lb} className="stat-card" style={{ boxShadow: 'var(--glass-shadow)' }}>
              <div style={{ fontSize: 20 }}>{ic}</div>
              <div className="stat-val">{v}</div>
              <div className="stat-lbl">{lb}</div>
            </div>
          ))}
        </div>

        <div style={{ padding: '16px 16px 32px' }}>

          {/* Mode indicator (Molten Academy — dark always) */}
          <div className="settings-item" style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 20 }}>🔥</span>
              <div>
                <div style={{
                  fontSize: 15, fontWeight: 600,
                  color: 'var(--text-primary)',
                  fontFamily: 'var(--font-body)',
                }}>
                  Molten Academy Theme
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-dim)', fontFamily: 'var(--font-body)' }}>
                  Dark glassmorphism — always on
                </div>
              </div>
            </div>
            <span className="glass-badge">Active</span>
          </div>

          {/* My uploads */}
          <h3 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 16, fontWeight: 800,
            margin: '4px 0 14px', color: 'var(--text-primary)',
          }}>
            My Uploads
          </h3>

          {mine.length === 0
            ? (
              <div className="empty-state">
                <div className="empty-icon">📂</div>
                <p>No uploads yet.<br />Share your knowledge with classmates!</p>
              </div>
            )
            : mine.map(n => (
              <div key={n.id} className="card" style={{
                padding: 14, marginBottom: 10,
                display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer',
              }}>
                <div style={{ fontSize: 28 }}>{fileIcon(n.ftype)}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 700, fontSize: 14,
                    color: 'var(--text-primary)',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}>
                    {n.title}
                  </div>
                  <div style={{ color: 'var(--text-dim)', fontSize: 12, marginTop: 3, fontFamily: 'var(--font-body)' }}>
                    ⭐ {avg(n.ratings)} · ⬇️ {n.dl} · 💬 {n.comments.length}
                  </div>
                </div>
                <span style={{ color: 'var(--accent-primary)', fontSize: 18 }}>›</span>
              </div>
            ))
          }

          {/* Settings */}
          <h3 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 16, fontWeight: 800,
            margin: '22px 0 14px', color: 'var(--text-primary)',
          }}>
            Settings
          </h3>

          {SETTINGS.map(({ icon, label, right }) => (
            <div key={label} className="settings-item">
              <div style={{ display: 'flex', alignItems: 'center', gap: 13 }}>
                <span style={{ fontSize: 20 }}>{icon}</span>
                <span style={{ fontSize: 15, color: 'var(--text-primary)', fontFamily: 'var(--font-body)' }}>
                  {label}
                </span>
              </div>
              {right
                ? <span className="glass-badge">{right}</span>
                : <span style={{ color: 'var(--text-dim)', fontSize: 13 }}>›</span>
              }
            </div>
          ))}

          <button className="btn-danger" onClick={onLogout} style={{ marginTop: 14 }}>
            🚪 Sign Out
          </button>

          <p style={{
            color: 'var(--text-dim)', fontSize: 11,
            textAlign: 'center', marginTop: 20,
            fontFamily: 'var(--font-mono)',
          }}>
            ScholarGrid v2.0.0 · CE Final Year Project
          </p>
        </div>
      </div>
    </div>
  )
}
