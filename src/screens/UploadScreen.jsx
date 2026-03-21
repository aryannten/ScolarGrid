import { useState } from 'react'

const FILE_TYPES = ['PDF', 'PPT', 'DOC', 'IMG']

export default function UploadScreen({ currentUser, onNoteAdded }) {
  const [ftype,    setFtype]    = useState('PDF')
  const [title,    setTitle]    = useState('')
  const [subject,  setSubject]  = useState('')
  const [desc,     setDesc]     = useState('')
  const [file,     setFile]     = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [progress, setProgress] = useState(0)
  const [done,     setDone]     = useState(false)
  const [errors,   setErrors]   = useState({})

  const validate = () => {
    const e = {}
    if (!title.trim())   e.title   = 'Title is required'
    if (!subject.trim()) e.subject = 'Subject code is required'
    return e
  }

  const submit = () => {
    const e = validate()
    if (Object.keys(e).length) { setErrors(e); return }
    setErrors({}); setLoading(true); setProgress(0)
    const iv = setInterval(() => {
      setProgress(p => { if (p >= 100) { clearInterval(iv); return 100 } return Math.min(p + 11, 100) })
    }, 140)
    setTimeout(() => {
      setLoading(false)
      onNoteAdded({
        id: Date.now(), title: title.trim(),
        subject: subject.trim().toUpperCase(),
        desc: desc.trim() || 'Uploaded notes',
        uid: currentUser.id, date: 'Mar 14, 2026',
        ftype, dl: 0, ratings: [], myRating: 0, comments: [],
      })
      setDone(true)
    }, 1600)
  }

  if (done) return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '40px 28px', textAlign: 'center',
      position: 'relative', zIndex: 2,
    }}>
      <div style={{ fontSize: 84, marginBottom: 20 }} className="anim-pop">🎉</div>
      <h2 style={{
        fontFamily: 'var(--font-display)',
        fontSize: 26, fontWeight: 900, marginBottom: 12,
        background: 'linear-gradient(135deg, var(--text-primary), var(--accent-primary))',
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
      }}>
        Notes Uploaded!
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7, marginBottom: 32, maxWidth: 280, fontFamily: 'var(--font-body)' }}>
        Your notes are live! Classmates can now view, download, and rate them.
      </p>
      <button
        className="btn-primary"
        style={{ maxWidth: 240 }}
        onClick={() => { setDone(false); setTitle(''); setSubject(''); setDesc(''); setFile(null); setProgress(0) }}
      >
        Upload Another
      </button>
    </div>
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
            Upload Notes
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 2, fontFamily: 'var(--font-body)' }}>
            Share your knowledge with classmates
          </p>
        </div>
      </div>

      <div className="scroll-y" style={{ flex: 1, padding: '16px 16px 24px' }}>

        {/* Drop zone */}
        <div
          className={`upload-zone ${file ? 'has-file' : ''}`}
          style={{ marginBottom: 20 }}
          onClick={() => document.getElementById('fInput').click()}
        >
          <input
            id="fInput" type="file" style={{ display: 'none' }}
            onChange={e => setFile(e.target.files[0])}
          />
          <div style={{ fontSize: 42, marginBottom: 10 }}>{file ? '📄' : '☁️'}</div>
          <p style={{
            color: file ? 'var(--accent-primary)' : 'var(--text-dim)',
            fontSize: 14, fontWeight: file ? 700 : 400, margin: 0,
            fontFamily: 'var(--font-body)',
          }}>
            {file ? file.name : 'Tap to select file'}
          </p>
          <p style={{ color: 'var(--text-dim)', fontSize: 12, marginTop: 6, fontFamily: 'var(--font-body)' }}>
            PDF · PPT · DOC · Images supported
          </p>
        </div>

        {/* File type selector */}
        <div style={{ marginBottom: 18 }}>
          <label className="label">File Type</label>
          <div style={{ display: 'flex', gap: 8 }}>
            {FILE_TYPES.map(t => (
              <button
                key={t}
                onClick={() => setFtype(t)}
                style={{
                  flex: 1, padding: '11px 0', borderRadius: 10,
                  border: ftype === t
                    ? '1px solid rgba(212,160,23,0.5)'
                    : '1px solid var(--glass-border)',
                  background: ftype === t
                    ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))'
                    : 'rgba(255,248,230,0.03)',
                  color: ftype === t ? '#080a07' : 'var(--text-secondary)',
                  fontSize: 12, fontWeight: 700,
                  fontFamily: 'var(--font-body)',
                  transition: 'var(--transition)',
                  boxShadow: ftype === t ? '0 0 16px rgba(212,160,23,0.3)' : 'none',
                  cursor: 'pointer',
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Title */}
        <div style={{ marginBottom: 14 }}>
          <label className="label">Title *</label>
          <input
            className={`input ${errors.title ? 'error' : ''}`}
            value={title}
            onChange={e => { setTitle(e.target.value); setErrors(p => ({ ...p, title: '' })) }}
            placeholder="e.g. Data Structures – Chapter 5"
          />
          {errors.title && <p className="field-error">{errors.title}</p>}
        </div>

        {/* Subject */}
        <div style={{ marginBottom: 14 }}>
          <label className="label">Subject Code *</label>
          <input
            className={`input ${errors.subject ? 'error' : ''}`}
            value={subject}
            onChange={e => { setSubject(e.target.value); setErrors(p => ({ ...p, subject: '' })) }}
            placeholder="e.g. CS301"
          />
          {errors.subject && <p className="field-error">{errors.subject}</p>}
        </div>

        {/* Description */}
        <div style={{ marginBottom: 22 }}>
          <label className="label">Description</label>
          <textarea
            className="input"
            value={desc}
            onChange={e => setDesc(e.target.value)}
            placeholder="What topics are covered? Any tips for students?"
            rows={4}
          />
        </div>

        {/* Progress bar */}
        {loading && (
          <div style={{ marginBottom: 16 }}>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <p style={{
              color: 'var(--text-dim)', fontSize: 12,
              textAlign: 'center', marginTop: 6,
              fontFamily: 'var(--font-body)',
            }}>
              Uploading… {progress}%
            </p>
          </div>
        )}

        <button className="btn-primary" onClick={submit} disabled={loading} style={{ fontSize: 16 }}>
          {loading ? 'Uploading…' : '⬆️ Upload Notes'}
        </button>
      </div>
    </div>
  )
}
