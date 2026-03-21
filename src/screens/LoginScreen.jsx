import { useState, useRef } from 'react'

function HoneycombIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 2L20.57 7V17L12 22L3.43 17V7L12 2Z" fill="#d4a017" fillOpacity="0.95" />
      <path d="M12 6.5L17.5 9.5V15.5L12 18.5L6.5 15.5V9.5L12 6.5Z" fill="#080a07" fillOpacity="0.6" />
    </svg>
  )
}

export default function LoginScreen({ onLogin }) {
  const [role,     setRole]     = useState('student')
  const [name,     setName]     = useState('')
  const [email,    setEmail]    = useState('')
  const [pass,     setPass]     = useState('')
  const [loading,  setLoading]  = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [errors,   setErrors]   = useState({})
  const cardRef = useRef(null)

  const validate = () => {
    const e = {}
    if (!name.trim())  e.name  = 'Name is required'
    if (!email.trim()) e.email = 'Email is required'
    if (!pass.trim())  e.pass  = 'Password is required'
    return e
  }

  const handleLogin = () => {
    const e = validate()
    if (Object.keys(e).length) {
      setErrors(e)
      cardRef.current?.classList.remove('anim-shake')
      void cardRef.current?.offsetWidth
      cardRef.current?.classList.add('anim-shake')
      return
    }
    setErrors({})
    setLoading(true)
    setTimeout(() => {
      const normalizedName = name.trim() || (role === 'teacher' ? 'Prof. Mehta' : 'Arjun Sharma')
      onLogin({
        id:    role === 'teacher' ? 3 : 1,
        name:  normalizedName,
        role,
        av:    normalizedName.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2),
        color: '#d4a017',
      })
    }, 1100)
  }

  return (
    <div style={{
      minHeight: '100dvh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '24px 20px', position: 'relative', zIndex: 2,
    }}>

      {/* Logo / Brand */}
      <div className="anim-fadeUp" style={{ textAlign: 'center', marginBottom: 40 }}>
        <div style={{
          width: 80, height: 80, borderRadius: 24,
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 18px',
          boxShadow: '0 0 40px rgba(212,160,23,0.4), 0 0 80px rgba(212,160,23,0.15)',
        }}>
          <HoneycombIcon />
        </div>

        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(2rem, 6vw, 2.8rem)',
          fontWeight: 800, letterSpacing: '-1px',
          background: 'linear-gradient(135deg, var(--text-primary), var(--accent-primary))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: 8,
        }}>
          ScholarGrid
        </h1>

        <p style={{
          fontFamily: 'var(--font-body)',
          color: 'var(--text-secondary)',
          fontSize: '1rem', lineHeight: 1.6,
        }}>
          Collaborate · Learn · Grow
        </p>

        {/* Live badge */}
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 12, gap: 8 }}>
          <span className="glass-badge-green">
            <span style={{
              width: 6, height: 6, borderRadius: '50%',
              background: 'var(--accent-secondary)',
              display: 'inline-block',
              boxShadow: '0 0 6px var(--accent-secondary)',
            }} />
            3 members live
          </span>
        </div>
      </div>

      {/* Card */}
      <div
        ref={cardRef}
        className="login-card anim-fadeUp delay-1"
        style={{ position: 'relative', zIndex: 2 }}
      >
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 20, fontWeight: 800,
          textAlign: 'center', marginBottom: 22,
          color: 'var(--text-primary)',
        }}>
          Welcome Back
        </h2>

        {/* Role toggle */}
        <div className="role-toggle" style={{ marginBottom: 22 }}>
          {['student', 'teacher'].map((r) => (
            <button
              key={r}
              className={`role-btn ${role === r ? 'active' : ''}`}
              onClick={() => setRole(r)}
            >
              {r === 'student' ? '🎓 Student' : '👨‍🏫 Teacher'}
            </button>
          ))}
        </div>

        {/* Name */}
        <div style={{ marginBottom: 14 }}>
          <label className="label">Name</label>
          <input
            className={`input ${errors.name ? 'error' : ''}`}
            type="text" value={name}
            onChange={e => { setName(e.target.value); setErrors(p => ({ ...p, name: '' })) }}
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            placeholder="Your full name"
          />
          {errors.name && <p className="field-error">{errors.name}</p>}
        </div>

        {/* Email */}
        <div style={{ marginBottom: 14 }}>
          <label className="label">Email</label>
          <input
            className={`input ${errors.email ? 'error' : ''}`}
            type="email" value={email}
            onChange={e => { setEmail(e.target.value); setErrors(p => ({ ...p, email: '' })) }}
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            placeholder="you@college.edu"
          />
          {errors.email && <p className="field-error">{errors.email}</p>}
        </div>

        {/* Password */}
        <div style={{ marginBottom: 26 }}>
          <label className="label">Password</label>
          <div style={{ position: 'relative' }}>
            <input
              className={`input ${errors.pass ? 'error' : ''}`}
              type={showPass ? 'text' : 'password'} value={pass}
              onChange={e => { setPass(e.target.value); setErrors(p => ({ ...p, pass: '' })) }}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              placeholder="••••••••"
              style={{ paddingRight: 48 }}
            />
            <button
              onClick={() => setShowPass(!showPass)}
              style={{
                position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)',
                background: 'none', border: 'none', fontSize: 18, color: 'var(--text-dim)',
                cursor: 'pointer',
              }}
            >
              {showPass ? '🙈' : '👁️'}
            </button>
          </div>
          {errors.pass && <p className="field-error">{errors.pass}</p>}
        </div>

        <button
          className="btn-primary"
          onClick={handleLogin}
          disabled={loading}
          style={{ marginBottom: 14, fontSize: 16 }}
        >
          {loading ? '⏳ Signing in…' : 'Sign In →'}
        </button>

        <p style={{
          color: 'var(--text-dim)', fontSize: 12,
          textAlign: 'center',
          fontFamily: 'var(--font-body)',
        }}>
          Demo: any email + password works
        </p>
      </div>

      {/* Floating study card visual */}
      <div className="anim-fadeUp delay-3" style={{
        marginTop: 28,
        width: '100%', maxWidth: 360,
        position: 'relative', zIndex: 2,
      }}>
        <div className="glass-card" style={{
          padding: '18px 20px',
          boxShadow: '0 0 120px rgba(212,160,23,0.12), var(--glass-shadow)',
        }}>
          <div style={{
            display: 'flex', justifyContent: 'space-between',
            alignItems: 'center', marginBottom: 12,
          }}>
            <span style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700, fontSize: 13,
              color: 'var(--text-primary)',
            }}>
              Study Session Stats
            </span>
            <span className="glass-badge-green">● Live</span>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            {[['📚', '5', 'Sessions Today'], ['👥', '12', 'Active Groups'], ['🔥', '8', 'Day Streak']].map(([ic, val, lbl]) => (
              <div key={lbl} style={{
                flex: 1, textAlign: 'center',
                padding: '10px 6px',
                background: 'rgba(255,248,230,0.04)',
                borderRadius: 10,
                border: '1px solid var(--glass-border)',
              }}>
                <div style={{ fontSize: 18, marginBottom: 4 }}>{ic}</div>
                <div style={{
                  fontFamily: 'var(--font-display)',
                  fontWeight: 800, fontSize: 18,
                  color: 'var(--accent-primary)',
                }}>{val}</div>
                <div style={{
                  fontSize: 9, color: 'var(--text-dim)',
                  fontFamily: 'var(--font-body)',
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                }}>{lbl}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
