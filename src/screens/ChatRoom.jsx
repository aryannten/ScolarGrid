import { useState, useEffect, useRef } from 'react'
import Avatar from '../components/Avatar'
import { MESSAGES, USERS, AUTO_REPLIES } from '../data/mockData'
import { getUser, fmtTime, deepCopy } from '../utils/helpers'

export default function ChatRoom({ chat, currentUser, onBack }) {
  const [msgs,  setMsgs]  = useState(() => deepCopy(MESSAGES[chat.id] || []))
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const send = () => {
    const text = input.trim()
    if (!text) return
    setMsgs(p => [...p, { id: Date.now(), sid: currentUser.id, text, time: fmtTime() }])
    setInput('')
    const others = USERS.filter(u => u.id !== currentUser.id)
    const r = others[Math.floor(Math.random() * others.length)]
    setTimeout(() => {
      setMsgs(p => [...p, {
        id: Date.now() + 1, sid: r.id,
        text: AUTO_REPLIES[Math.floor(Math.random() * AUTO_REPLIES.length)],
        time: fmtTime(),
      }])
    }, 1400)
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative', zIndex: 2 }}>
      {/* Header */}
      <div className="page-header" style={{ borderBottomColor: 'rgba(212,160,23,0.15)' }}>
        <button onClick={onBack} style={{
          background: 'none', border: 'none',
          color: 'var(--accent-primary)',
          fontSize: 24, padding: 0, lineHeight: 1, marginRight: 4, cursor: 'pointer',
        }}>←</button>

        <div style={{
          width: 44, height: 44, borderRadius: 12, fontSize: 20, flexShrink: 0,
          background: 'rgba(212,160,23,0.08)',
          border: '1px solid rgba(212,160,23,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {chat.icon}
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 800, fontSize: 16, color: 'var(--text-primary)',
            }}>
              {chat.name}
            </span>
            <span className="glass-badge" style={{ fontSize: 9 }}>{chat.code}</span>
          </div>
          <div style={{ color: 'var(--text-dim)', fontSize: 12, marginTop: 1, fontFamily: 'var(--font-body)' }}>
            👥 {chat.members} members
          </div>
        </div>

        <span style={{
          fontSize: 18, cursor: 'pointer', padding: 4,
          color: 'var(--accent-glow)',
        }}>📌</span>
      </div>

      {/* Messages */}
      <div className="scroll-y" style={{
        flex: 1, padding: '12px 14px 8px',
        background: 'transparent',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <span style={{
            background: 'rgba(255,248,230,0.04)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            color: 'var(--text-dim)',
            fontSize: 12, padding: '4px 16px', borderRadius: 20,
            border: '1px solid var(--glass-border)',
            fontFamily: 'var(--font-body)',
          }}>
            Today
          </span>
        </div>

        {msgs.map(msg => {
          const mine   = msg.sid === currentUser.id
          const sender = getUser(msg.sid)
          return (
            <div key={msg.id} className="anim-fadeUp" style={{
              display: 'flex',
              justifyContent: mine ? 'flex-end' : 'flex-start',
              marginBottom: 10, gap: 8, alignItems: 'flex-end',
            }}>
              {!mine && <Avatar user={sender} size={28} />}
              <div
                className={mine ? 'bubble-out' : 'bubble-in'}
                style={{ maxWidth: '75%', padding: '10px 14px' }}
              >
                {!mine && (
                  <div style={{
                    color: 'var(--accent-glow)',
                    fontSize: 11, fontWeight: 700,
                    marginBottom: 3,
                    fontFamily: 'var(--font-display)',
                  }}>
                    {sender?.name}
                  </div>
                )}
                <p style={{
                  fontSize: 14, margin: 0, lineHeight: 1.5,
                  wordBreak: 'break-word',
                  fontFamily: 'var(--font-body)',
                }}>
                  {msg.text}
                </p>
                <div style={{
                  display: 'flex', justifyContent: 'flex-end',
                  alignItems: 'center', gap: 4, marginTop: 4,
                }}>
                  <span style={{
                    color: mine ? 'rgba(8,10,7,0.5)' : 'var(--text-dim)',
                    fontSize: 10,
                    fontFamily: 'var(--font-mono)',
                  }}>
                    {msg.time}
                  </span>
                  {mine && <span style={{ color: 'rgba(8,10,7,0.5)', fontSize: 11 }}>✓✓</span>}
                </div>
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div style={{
        background: 'rgba(8,10,7,0.80)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        borderTop: '1px solid var(--glass-border)',
        padding: '10px 14px',
        display: 'flex', gap: 10, alignItems: 'center', flexShrink: 0,
      }}>
        <button style={{
          background: 'none', border: 'none', fontSize: 22,
          color: 'var(--text-dim)', cursor: 'pointer',
        }}>📎</button>

        <input
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder={`Message #${chat.name}…`}
          className="input"
          style={{ borderRadius: 24, padding: '11px 18px', fontSize: 14, flex: 1 }}
        />

        <button onClick={send} style={{
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))',
          border: '1px solid rgba(212,160,23,0.4)',
          borderRadius: '50%', width: 46, height: 46, flexShrink: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 18, color: '#080a07',
          boxShadow: '0 0 20px rgba(212,160,23,0.35)',
          cursor: 'pointer', transition: 'var(--transition)',
        }}>➤</button>
      </div>
    </div>
  )
}
