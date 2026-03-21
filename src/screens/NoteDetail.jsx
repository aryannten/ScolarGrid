import { useState } from 'react'
import Avatar from '../components/Avatar'
import Stars from '../components/Stars'
import { avg, getUser, fileIcon } from '../utils/helpers'

export default function NoteDetail({ note: init, currentUser, onBack, onUpdate }) {
  const [note,     setNote]     = useState(init)
  const [comment,  setComment]  = useState('')
  const [myRating, setMyRating] = useState(init.myRating)
  const [dlDone,   setDlDone]   = useState(false)
  const u = getUser(note.uid)

  const handleRate = (r) => {
    const newR = myRating > 0
      ? [...note.ratings.slice(0, -1), r]
      : [...note.ratings, r]
    setMyRating(r)
    const upd = { ...note, ratings: newR, myRating: r }
    setNote(upd); onUpdate(upd)
  }

  const handleDl = () => {
    if (dlDone) return
    setDlDone(true)
    const upd = { ...note, dl: note.dl + 1 }
    setNote(upd); onUpdate(upd)
    setTimeout(() => setDlDone(false), 2200)
  }

  const addComment = () => {
    if (!comment.trim()) return
    const upd = { ...note, comments: [...note.comments, { uid: currentUser.id, text: comment.trim(), time: 'Just now' }] }
    setNote(upd); onUpdate(upd); setComment('')
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative', zIndex: 2 }}>
      {/* Header */}
      <div className="page-header">
        <button onClick={onBack} style={{
          background: 'none', border: 'none',
          color: 'var(--accent-primary)', fontSize: 24, padding: 0, lineHeight: 1, cursor: 'pointer',
        }}>←</button>
        <h3 style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 800, fontSize: 17, flex: 1,
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
          color: 'var(--text-primary)',
        }}>
          Note Details
        </h3>
        <button style={{ background: 'none', border: 'none', color: 'var(--accent-glow)', fontSize: 20, cursor: 'pointer' }}>🔖</button>
      </div>

      <div className="scroll-y" style={{ flex: 1, padding: '16px 16px 24px' }}>

        {/* Preview card */}
        <div className="card" style={{ padding: '24px 20px', marginBottom: 14, textAlign: 'center' }}>
          <div style={{ fontSize: 56, marginBottom: 12 }}>{fileIcon(note.ftype)}</div>
          <span className={`file-badge ${note.ftype}`}>{note.ftype}</span>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 19, fontWeight: 800,
            margin: '10px 0 6px', lineHeight: 1.3, color: 'var(--text-primary)',
          }}>
            {note.title}
          </h2>
          <span style={{ color: 'var(--accent-primary)', fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-body)' }}>
            {note.subject}
          </span>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 10, lineHeight: 1.7, fontFamily: 'var(--font-body)' }}>
            {note.desc}
          </p>
        </div>

        {/* Uploader */}
        <div className="card" style={{ padding: 14, marginBottom: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Avatar user={u} size={44} />
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)', fontFamily: 'var(--font-display)' }}>
                {u?.name}
              </div>
              <div style={{ color: 'var(--text-dim)', fontSize: 12, fontFamily: 'var(--font-body)' }}>
                {u?.role === 'teacher' ? '👨‍🏫 Teacher' : '🎓 Student'} · {note.date}
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{
              fontFamily: 'var(--font-display)',
              color: 'var(--accent-glow)', fontSize: 24, fontWeight: 800, lineHeight: 1,
            }}>
              {avg(note.ratings)}
            </div>
            <div style={{ color: 'var(--text-dim)', fontSize: 10, marginTop: 2, fontFamily: 'var(--font-body)' }}>⭐ avg</div>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
          {[['⬇️', note.dl, 'Downloads'], ['💬', note.comments.length, 'Comments'], ['⭐', note.ratings.length, 'Ratings']].map(([ic, v, lb]) => (
            <div key={lb} className="stat-card">
              <div style={{ fontSize: 20 }}>{ic}</div>
              <div className="stat-val">{v}</div>
              <div className="stat-lbl">{lb}</div>
            </div>
          ))}
        </div>

        {/* Download */}
        <button
          className="btn-primary"
          onClick={handleDl}
          style={{
            marginBottom: 14, fontSize: 16,
            background: dlDone
              ? 'linear-gradient(135deg, var(--accent-secondary), #16a34a)'
              : undefined,
            boxShadow: dlDone
              ? '0 0 32px rgba(34,197,94,0.4)'
              : undefined,
            transition: 'all 0.35s',
          }}
        >
          {dlDone ? '✅ Downloaded!' : '⬇️ Download Notes'}
        </button>

        {/* Rating */}
        <div className="card" style={{ padding: 20, marginBottom: 14 }}>
          <h4 style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700, fontSize: 15, marginBottom: 14, color: 'var(--text-primary)',
          }}>
            Rate These Notes
          </h4>
          <div className="rating-stars-lg">
            {[1, 2, 3, 4, 5].map(s => (
              <span
                key={s}
                className={`rating-star-lg ${s <= myRating ? 'active' : ''}`}
                onClick={() => handleRate(s)}
              >★</span>
            ))}
          </div>
          <p style={{
            color: 'var(--text-dim)', fontSize: 13,
            textAlign: 'center', marginTop: 10,
            fontFamily: 'var(--font-body)',
          }}>
            {myRating === 0 ? 'Tap a star to rate' : `You rated: ${myRating}/5 — Thank you! 🎉`}
          </p>
        </div>

        {/* Comments */}
        <div className="card" style={{ padding: 18 }}>
          <h4 style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700, fontSize: 15, marginBottom: 16, color: 'var(--text-primary)',
          }}>
            💬 Comments ({note.comments.length})
          </h4>

          {note.comments.map((c, i) => {
            const cu = getUser(c.uid)
            return (
              <div key={i} className="comment-row">
                <Avatar user={cu} size={34} />
                <div className="comment-bubble">
                  <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', marginBottom: 4 }}>
                    <span style={{
                      fontWeight: 700, fontSize: 13, color: 'var(--text-primary)',
                      fontFamily: 'var(--font-display)',
                    }}>
                      {cu?.name}
                    </span>
                    <span style={{ color: 'var(--text-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                      {c.time}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: 13, margin: 0, lineHeight: 1.5, fontFamily: 'var(--font-body)' }}>
                    {c.text}
                  </p>
                </div>
              </div>
            )
          })}

          {/* Add comment */}
          <div style={{ display: 'flex', gap: 10, marginTop: 8, alignItems: 'center' }}>
            <Avatar user={currentUser} size={34} />
            <input
              className="input"
              value={comment}
              onChange={e => setComment(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && addComment()}
              placeholder="Write a comment…"
              style={{ borderRadius: 24, padding: '9px 16px', fontSize: 13 }}
            />
            <button onClick={addComment} style={{
              background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))',
              border: '1px solid rgba(212,160,23,0.4)',
              borderRadius: '50%', width: 40, height: 40,
              flexShrink: 0, fontSize: 16, color: '#080a07',
              boxShadow: '0 0 16px rgba(212,160,23,0.35)',
              cursor: 'pointer',
            }}>➤</button>
          </div>
        </div>
      </div>
    </div>
  )
}
