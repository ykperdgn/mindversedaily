import React from 'react';

const zodiacPaths = {
  Aries: "M12 2l2 7 7 2-7 2-2 7-2-7-7-2 7-2z",
  Taurus: "M12 2c1 0 3 1 3 4s-2 3-3 3-3-1-3-3 2-4 3-4z M8 12c2 2 8 2 10 0",
  Gemini: "M8 4h8v2H8zm0 4h8v2H8zm0 4h8v2H8z",
  Cancer: "M9 4a4 4 0 0 0 0 8 4 4 0 0 1 0 8",
  Leo: "M12 2c4 4 4 10 0 14-4-4-4-10 0-14z",
  Virgo: "M8 4v12c0 2 4 2 4 0v-8",
  Libra: "M6 16h12m-6-8v12",
  Scorpio: "M6 18v-8l6 4v-8",
  Sagittarius: "M8 4l8 8m-6 0h6v6",
  Capricorn: "M6 16c0-4 6-4 6-8v-2",
  Aquarius: "M6 12c2-4 6 4 8 0",
  Pisces: "M6 4c4 4 4 8 0 12"
};

export default function ZodiacIcon({ sign, size = 24, color = "black" }) {
  const path = zodiacPaths[sign] || "";
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-label={`${sign} zodiac symbol`}
      role="img"
    >
      <path d={path} />
    </svg>
  );
}
