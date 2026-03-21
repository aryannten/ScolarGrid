// ThemeToggle — repurposed as a decorative settings button in Molten Academy
// (always dark theme, so this shows a flame icon for the brand aesthetic)
export default function ThemeToggle() {
  return (
    <button
      className="theme-toggle"
      title="Molten Academy — Dark Theme"
      aria-label="Theme indicator"
      style={{ cursor: 'default' }}
    >
      🔥
    </button>
  )
}
