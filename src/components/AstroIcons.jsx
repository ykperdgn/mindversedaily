import React from 'react';

export const ZodiacIcons = ({ sign, size = 20, color = '#333' }) => {
  const paths = {
    Aries: 'M10 5L5 10L10 15M15 5L20 10L15 15M5 10H20',
    Taurus: 'M7 7H17V17H7V7ZM12 7V17',
    Gemini: 'M7 5H17M7 12H17M7 19H17',
    Cancer: 'M18 10C18 14-6 16 6 22M6 10C6 14 18 16 18 22',
    Leo: 'M5 12H19M8 7L12 12L8 17M16 7L12 12L16 17',
    Virgo: 'M5 20L12 5L19 20M12 5V20',
    Libra: 'M5 12H19M12 5V19M8 9L12 5L16 9M8 15L12 19L16 15',
    Scorpio: 'M5 5H19V19H5V5ZM12 5V19',
    Sagittarius: 'M5 19L12 5L19 19M12 5V19',
    Capricorn: 'M5 19L12 5L19 19M5 12H19',
    Aquarius: 'M5 7H19M5 12H19M5 17H19',
    Pisces: 'M5 12H19M8 7L5 12L8 17M16 7L19 12L16 17'
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}>
      <path d={paths[sign]} strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
};

export const PlanetIcons = ({ planet, size = 24, color = '#333' }) => {
  const icons = {
    Sun: <>
      <circle cx="12" cy="12" r="6" stroke={color} strokeWidth="1.5" fill="none"/>
      <path d="M12 3V1M12 23V21M21 12H23M1 12H3M19 5L20 4M4 20L5 19M19 19L20 20M4 4L5 5" stroke={color} strokeWidth="1.2"/>
    </>,
    Moon: <>
      <path d="M20 12C20 15-15 17 3 22C5 15 5 9 3 2C15 7 20 9 20 12Z" stroke={color} strokeWidth="1.5" fill="none"/>
    </>,
    Mercury: <>
      <circle cx="12" cy="9" r="5" stroke={color} strokeWidth="1.5" fill="none"/>
      <path d="M12 14V21M9 18H15" stroke={color} strokeWidth="1.5"/>
    </>,
    Venus: <>
      <circle cx="12" cy="12" r="7" stroke={color} strokeWidth="1.5" fill="none"/>
      <path d="M5 5L19 19" stroke={color} strokeWidth="1.2"/>
    </>,
    Mars: <>
      <path d="M5 5H19V19H5V5ZM12 5L19 12L12 19L5 12L12 5Z" stroke={color} strokeWidth="1.5" fill="none"/>
    </>,
    Jupiter: <>
      <circle cx="12" cy="12" r="8" stroke={color} strokeWidth="1.5" fill="none"/>
      <circle cx="12" cy="12" r="4" stroke={color} strokeWidth="1.2"/>
    </>,
    Saturn: <>
      <circle cx="12" cy="12" r="6" stroke={color} strokeWidth="1.5" fill="none"/>
      <path d="M3 12H21M12 3V21" stroke={color} strokeWidth="1.2"/>
      <circle cx="12" cy="12" r="9" stroke={color} strokeWidth="1" fill="none"/>
    </>,
    NorthNode: <path d="M12 3L20 21L12 18L4 21L12 3Z" stroke={color} strokeWidth="1.5" fill="none"/>,
    SouthNode: <path d="M12 21L4 3L12 6L20 3L12 21Z" stroke={color} strokeWidth="1.5" fill="none"/>
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      {icons[planet]}
    </svg>
  );
};
