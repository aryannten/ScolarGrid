// Avatar with gold gradient background and Playfair Display initials
export default function Avatar({ user, size = 36 }) {
  // Map user colors to gold/emerald/amber palette; strip out any blues/purples
  const getColor = (color) => {
    if (!color) return 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))'
    // If the color is from the old blue/purple palette, remap it
    const lc = color.toLowerCase()
    if (lc.includes('6366f1') || lc.includes('7c3aed') || lc.includes('4f46e5') || lc.includes('93c5fd')) {
      return 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))'
    }
    if (lc.includes('f59e0b') || lc.includes('d4a017') || lc.includes('fb923c')) {
      return 'linear-gradient(135deg, var(--accent-glow), var(--accent-warm))'
    }
    return 'linear-gradient(135deg, var(--accent-primary), var(--accent-warm))'
  }

  return (
    <div
      className="avatar"
      style={{
        width: size,
        height: size,
        background: getColor(user?.color),
        fontSize: size * 0.36,
        fontFamily: 'var(--font-display)',
        color: '#080a07',
      }}
    >
      {user?.av || user?.avatar || '?'}
    </div>
  )
}
