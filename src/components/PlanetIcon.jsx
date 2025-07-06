import React from 'react';

// Minimalist SVG paths for each planet
const planetSvgs = {
  Sun: (
    <circle cx="12" cy="12" r="8" stroke="#fbbf24" strokeWidth="2" fill="#fffde7" />
  ),
  Moon: (
    <path d="M16 12A6 6 0 1 1 8 6.5A7 7 0 1 0 16 12Z" fill="#e0e7ef" stroke="#a3a3a3" strokeWidth="1.5" />
  ),
  Mercury: (
    <g>
      <circle cx="12" cy="14" r="5" fill="#fff" stroke="#a3a3a3" strokeWidth="1.5" />
      <path d="M12 4V8" stroke="#a3a3a3" strokeWidth="1.5" />
      <path d="M9 6C10 4 14 4 15 6" stroke="#a3a3a3" strokeWidth="1.2" fill="none" />
    </g>
  ),
  Venus: (
    <g>
      <circle cx="12" cy="12" r="5" fill="#fff" stroke="#e879f9" strokeWidth="1.5" />
      <path d="M12 17V21" stroke="#e879f9" strokeWidth="1.5" />
      <path d="M9.5 19H14.5" stroke="#e879f9" strokeWidth="1.5" />
    </g>
  ),
  Mars: (
    <g>
      <circle cx="12" cy="12" r="5" fill="#fff" stroke="#f87171" strokeWidth="1.5" />
      <path d="M16 8L20 4" stroke="#f87171" strokeWidth="1.5" />
      <path d="M18 4H20V6" stroke="#f87171" strokeWidth="1.5" />
    </g>
  ),
  Jupiter: (
    <g>
      <circle cx="12" cy="12" r="6" fill="#fff" stroke="#fbbf24" strokeWidth="1.5" />
      <path d="M9 10C13 10 13 16 9 16" stroke="#fbbf24" strokeWidth="1.2" fill="none" />
      <path d="M15 8H17" stroke="#fbbf24" strokeWidth="1.2" />
    </g>
  ),
  Saturn: (
    <g>
      <ellipse cx="12" cy="13" rx="6" ry="4" fill="#fff" stroke="#a3a3a3" strokeWidth="1.5" />
      <path d="M12 7V19" stroke="#a3a3a3" strokeWidth="1.2" />
    </g>
  ),
};

export default function PlanetIcon({ planet, size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-label={planet}>
      {planetSvgs[planet] || null}
    </svg>
  );
}
