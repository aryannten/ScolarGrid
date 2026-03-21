import { useState } from 'react'

export default function Stars({ rating, size = 15, interactive = false, onRate }) {
  const [hover, setHover] = useState(0)
  const active = hover || Math.round(rating)

  return (
    <div className="stars">
      {[1, 2, 3, 4, 5].map((s) => (
        <span
          key={s}
          className={`star ${s <= active ? 'filled' : ''} ${interactive ? 'interactive' : ''} ${interactive && s <= hover ? 'hovered' : ''}`}
          style={{ fontSize: size }}
          onClick={() => interactive && onRate?.(s)}
          onMouseEnter={() => interactive && setHover(s)}
          onMouseLeave={() => interactive && setHover(0)}
        >★</span>
      ))}
    </div>
  )
}
