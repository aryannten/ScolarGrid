import { useState } from 'react'

export default function ChatListScreen({ chats, onOpen }) {
  const [q, setQ] = useState('')
  const filtered = chats.filter(c =>
    c.name.toLowerCase().includes(q.toLowerCase()) ||
    c.code.toLowerCase().includes(q.toLowerCase())
  )

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
            📡 Channels
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 2, fontFamily: 'var(--font-body)' }}>
            CE Sem 6 · {chats.length} subject channels
          </p>
        </div>
        <button style={{
          background: 'rgba(212,160,23,0.10)',
          border: '1px solid rgba(212,160,23,0.25)',
          borderRadius: 12, padding: '9px 13px',
          fontSize: 16, color: 'var(--accent-primary)',
          transition: 'var(--transition)',
        }}>＋</button>
      </div>

      {/* Search */}
      <div style={{ padding: '12px 16px 0', background: 'rgba(8,10,7,0.6)', flexShrink: 0 }}>
        <div className="search-bar">
          <span style={{ color: 'var(--text-dim)', fontSize: 16 }}>🔍</span>
          <input
            placeholder="Search channels…"
            value={q} onChange={e => setQ(e.target.value)}
          />
        </div>
      </div>

      {/* Channel list */}
      <div className="scroll-y" style={{ flex: 1, padding: '12px 14px 24px' }}>
        {filtered.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <p>No channels match "{q}"</p>
          </div>
        )}
        {filtered.map((chat, i) => (
          <div
            key={chat.id}
            className={`channel-card anim-fadeUp ${chat.unread > 0 ? 'unread' : ''}`}
            style={{ animationDelay: `${i * 0.06}s` }}
            onClick={() => onOpen(chat)}
          >
            {/* Icon */}
            <div style={{ position: 'relative', flexShrink: 0 }}>
              <div style={{
                width: 52, height: 52, borderRadius: 14, fontSize: 24,
                background: 'rgba(212,160,23,0.08)',
                border: '1px solid rgba(212,160,23,0.18)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {chat.icon}
              </div>
              {chat.unread > 0 && (
                <div style={{
                  position: 'absolute', top: -4, right: -4,
                  background: 'linear-gradient(135deg,var(--accent-primary),var(--accent-warm))',
                  borderRadius: 10, minWidth: 20, height: 20,
                  fontSize: 10, fontWeight: 800, color: '#080a07',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  padding: '0 5px', boxShadow: '0 0 12px rgba(212,160,23,0.5)',
                  fontFamily: 'var(--font-body)',
                }}>
                  {chat.unread}
                </div>
              )}
            </div>

            {/* Text */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{
                    fontWeight: 700, fontSize: 15,
                    color: 'var(--text-primary)',
                    fontFamily: 'var(--font-display)',
                  }}>
                    {chat.name}
                  </span>
                  <span className="glass-badge" style={{ fontSize: 9 }}>{chat.code}</span>
                </div>
                <span style={{ color: 'var(--text-dim)', fontSize: 11, flexShrink: 0, fontFamily: 'var(--font-body)' }}>
                  {chat.time}
                </span>
              </div>
              <p style={{
                color: 'var(--text-secondary)', fontSize: 13, margin: 0,
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                fontFamily: 'var(--font-body)',
              }}>
                {chat.lastMsg}
              </p>
              <span style={{ color: 'var(--text-dim)', fontSize: 11, marginTop: 4, display: 'block', fontFamily: 'var(--font-body)' }}>
                👥 {chat.members} members
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
