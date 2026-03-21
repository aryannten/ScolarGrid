import { useState } from 'react'
import Avatar from '../components/Avatar'
import Stars from '../components/Stars'
import { avg, getUser } from '../utils/helpers'

export default function NotesScreen({ notes, onViewNote }) {
  const [tab, setTab] = useState('top')

  const sorted = [...notes].sort((a, b) => {
    if (tab === 'top')    return parseFloat(avg(b.ratings)) - parseFloat(avg(a.ratings))
    if (tab === 'recent') return b.id - a.id
    return b.dl - a.dl
  })

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative', zIndex: 2 }}>
      {/* Header */}
      <div className="page-header">
        <div style={{ flex: 1 }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 22, fontWeight: 800,
            background: 'linear-gradient(135deg, var(--text-primary), var(--accent-primary))',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>
            Study Notes
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 2, fontFamily: 'var(--font-body)' }}>
            {notes.length} notes available
          </p>
        </div>
        <button style={{
          background: 'rgba(212,160,23,0.10)',
          border: '1px solid rgba(212,160,23,0.2)',
          borderRadius: 10, padding: '9px 11px', fontSize: 18,
          cursor: 'pointer',
        }}>🔍</button>
      </div>

      {/* Tabs */}
      <div style={{ background: 'rgba(8,10,7,0.6)', padding: '0 16px', flexShrink: 0 }}>
        <div className="tabs">
          {[['top', '⭐ Top Rated'], ['recent', '🕒 Recent'], ['popular', '🔥 Popular']].map(([id, label]) => (
            <button
              key={id}
              className={`tab-btn ${tab === id ? 'active' : ''}`}
              onClick={() => setTab(id)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Notes grid */}
      <div className="scroll-y" style={{ flex: 1, padding: '14px 14px 24px' }}>
        {sorted.map((note, i) => {
          const u = getUser(note.uid)
          const r = parseFloat(avg(note.ratings))
          const barColor = r >= 4.5
            ? 'linear-gradient(90deg, var(--accent-glow), var(--accent-warm))'
            : r >= 4
            ? 'linear-gradient(90deg, var(--accent-primary), var(--accent-warm))'
            : 'linear-gradient(90deg, var(--glass-border-bright), var(--glass-border-bright))'

          return (
            <div
              key={note.id}
              className="note-card anim-fadeUp"
              style={{ animationDelay: `${i * 0.05}s` }}
              onClick={() => onViewNote(note)}
            >
              <div style={{ height: 3, background: barColor }} />
              <div style={{ padding: '14px 16px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10, marginBottom: 8 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
                      <span className={`file-badge ${note.ftype}`}>{note.ftype}</span>
                      <span style={{
                        color: 'var(--accent-primary)', fontSize: 11, fontWeight: 700,
                        fontFamily: 'var(--font-body)',
                      }}>
                        {note.subject}
                      </span>
                    </div>
                    <h3 style={{
                      fontSize: 16, fontWeight: 700, margin: 0, lineHeight: 1.3,
                      color: 'var(--text-primary)',
                      fontFamily: 'var(--font-display)',
                    }}>
                      {note.title}
                    </h3>
                  </div>

                  <div style={{
                    background: r >= 4.5 ? 'rgba(245,158,11,0.12)' : 'rgba(212,160,23,0.08)',
                    border: '1px solid rgba(212,160,23,0.2)',
                    borderRadius: 10, padding: '7px 10px',
                    textAlign: 'center', flexShrink: 0,
                  }}>
                    <div style={{
                      color: 'var(--accent-glow)', fontSize: 18, fontWeight: 800,
                      fontFamily: 'var(--font-display)',
                    }}>
                      {avg(note.ratings)}
                    </div>
                    <div style={{ color: 'var(--text-dim)', fontSize: 9, fontFamily: 'var(--font-body)' }}>/ 5.0</div>
                  </div>
                </div>

                <p style={{ color: 'var(--text-secondary)', fontSize: 13, margin: '0 0 12px', lineHeight: 1.5, fontFamily: 'var(--font-body)' }}>
                  {note.desc}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                  <Stars rating={r} size={14} />
                  <span style={{ color: 'var(--text-dim)', fontSize: 12, fontFamily: 'var(--font-body)' }}>
                    ({note.ratings.length} ratings)
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Avatar user={u} size={24} />
                    <span style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, fontFamily: 'var(--font-body)' }}>
                      {u?.name}
                    </span>
                    <span style={{ color: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-body)' }}>
                      {note.date}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 12 }}>
                    <span style={{ color: 'var(--text-dim)', fontSize: 12, fontFamily: 'var(--font-body)' }}>⬇ {note.dl}</span>
                    <span style={{ color: 'var(--text-dim)', fontSize: 12, fontFamily: 'var(--font-body)' }}>💬 {note.comments.length}</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
