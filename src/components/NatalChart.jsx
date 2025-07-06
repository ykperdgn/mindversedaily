import React, { useState, useCallback, useMemo } from 'react';
import { ZodiacIcons, PlanetIcons } from './AstroIcons.jsx';

const zodiacSigns = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
];

// Aspect renkleri: basit ve pastel tonlarda
const aspectColors = {
  0: '#E63946',      // Conjunction (kırmızı)
  60: '#457B9D',     // Sextile (mavi)
  90: '#F1FAEE',     // Square (açık bej)
  120: '#2A9D8F',    // Trine (turkuaz)
  180: '#1D3557',    // Opposition (koyu mavi)
};

const degreeToPosition = (cx, cy, radius, degree) => {
  const rad = (degree - 90) * (Math.PI / 180);
  return {
    x: cx + radius * Math.cos(rad),
    y: cy + radius * Math.sin(rad),
  };
};

const getAspects = (planets, orb = 6) => {
  const entries = Object.entries(planets);
  const aspects = [];
  const majorAspects = [0, 60, 90, 120, 180];

  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      const [planetA, degA] = entries[i];
      const [planetB, degB] = entries[j];
      let diff = Math.abs(degA - degB);
      if (diff > 180) diff = 360 - diff;
      const aspect = majorAspects.find(a => Math.abs(a - diff) <= orb);
      if (aspect !== undefined) {
        aspects.push({ from: planetA, to: planetB, angle: diff, aspect });
      }
    }
  }
  return aspects;
};

const getZodiac = (deg) => {
  const index = Math.floor(deg / 30) % 12;
  return zodiacSigns[index];
};

export default function NatalChart({ planets }) {
  const size = 480;
  const center = size / 2;
  const radius = 180;

  const aspects = useMemo(() => getAspects(planets), [planets]);

  const [tooltip, setTooltip] = useState(null);
  const onPlanetHover = useCallback((planet, deg) => {
    setTooltip({ planet, deg });
  }, []);
  const onMouseLeave = useCallback(() => setTooltip(null), []);

  const renderPlanets = () =>
    Object.entries(planets).map(([planet, deg]) => {
      const { x, y } = degreeToPosition(center, center, radius - 40, deg);
      return (
        <g key={planet} transform={`translate(${x - 12},${y - 12})`}>
          <PlanetIcons planet={planet} size={24} color="#222" />
        </g>
      );
    });

  return (
    <div
      style={{
        position: 'relative',
        width: size,
        margin: '0 auto',
        background: '#fff', // gridin arka planı tamamen beyaz
        borderRadius: 20,
        padding: 20,
        boxShadow: '0 6px 12px rgba(0,0,0,0.1)',
        fontFamily: "'Inter', sans-serif",
        userSelect: 'none',
      }}
      onMouseLeave={onMouseLeave}
      onBlur={onMouseLeave}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        role="img"
        aria-label="Natal astrology chart"
        style={{ display: 'block', background: '#fff' }} // SVG arka planı da beyaz
      >
        {/* Dış çember */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="#f5f7fa" // chartın yuvarlağı için farklı bir renk (açık gri/mavi ton)
          stroke="#4f8cff" // belirgin bir mavi ton
          strokeWidth={3}
        />

        {/* Burç dilimleri */}
        {zodiacSigns.map((sign, idx) => {
          const startAngle = idx * 30 - 90;
          const endAngle = startAngle + 30;
          const largeArcFlag = 0;

          const pathData = `
            M ${center} ${center}
            L ${center + radius * Math.cos((startAngle * Math.PI) / 180)} ${center + radius * Math.sin((startAngle * Math.PI) / 180)}
            A ${radius} ${radius} 0 ${largeArcFlag} 1 ${center + radius * Math.cos((endAngle * Math.PI) / 180)} ${center + radius * Math.sin((endAngle * Math.PI) / 180)}
            Z
          `;

          return (
            <g key={sign}>
              {/* Burç dilimi */}
              <path
                d={pathData}
                fill="none"
                stroke="#eee"
                strokeWidth={1}
              />

              {/* Burç simgesi */}
              <foreignObject
                x={center + (radius - 30) * Math.cos(((startAngle + 15) * Math.PI) / 180) - 15}
                y={center + (radius - 30) * Math.sin(((startAngle + 15) * Math.PI) / 180) - 15}
                width={30}
                height={30}
                pointerEvents="none"
              >
                <div style={{ pointerEvents: 'none' }}>
                  <ZodiacIcons sign={sign} size={26} color="#666" />
                </div>
              </foreignObject>
            </g>
          );
        })}

        {/* Açı çizgileri */}
        {aspects.map(({ from, to, aspect }, i) => {
          const posA = degreeToPosition(center, center, radius - 40, planets[from]);
          const posB = degreeToPosition(center, center, radius - 40, planets[to]);
          return (
            <line
              key={`aspect-${i}`}
              x1={posA.x}
              y1={posA.y}
              x2={posB.x}
              y2={posB.y}
              stroke={aspectColors[aspect] || '#999'}
              strokeWidth={aspect === 0 ? 2 : 1}
              opacity={0.7}
              strokeDasharray={aspect === 180 ? '4 3' : aspect === 90 ? '2 2' : 'none'}
              aria-label={`Aspect between ${from} and ${to} (${aspect} degrees)`}
            />
          );
        })}

        {/* Gezegenler */}
        {renderPlanets()}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          role="tooltip"
          style={{
            position: 'absolute',
            left: 16,
            top: 16,
            background: '#fff',
            border: '1px solid #ccc',
            padding: 10,
            borderRadius: 8,
            fontSize: 14,
            color: '#222',
            boxShadow: '0 2px 6px rgba(0,0,0,0.12)',
            pointerEvents: 'none',
            userSelect: 'none',
            minWidth: 140,
            fontWeight: '600',
            fontFamily: "'Inter', sans-serif",
          }}
        >
          {tooltip.planet}: {tooltip.deg.toFixed(2)}° ({getZodiac(tooltip.deg)})
        </div>
      )}
    </div>
  );
}
