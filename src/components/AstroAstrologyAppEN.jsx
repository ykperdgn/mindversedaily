import React, { useState, useCallback, useRef } from 'react';
import { getGroqInterpretationEN } from '../lib/groqApiEN.ts';

// --- English Tarot Meanings ---
const WILDWOOD_TAROT_EN = {
  "The Wanderer": "New beginnings, freedom, stepping into the unknown with courage.",
  "The Shaman": "Willpower, strength, potential, using inner resources.",
  "The Seer": "Intuition, insight, spiritual guidance, vision.",
  "The Green Woman": "Fertility, creativity, harmony with nature.",
  "The Green Man": "Growth, vitality, unity with nature.",
  "The Archer": "Focus, determination, aiming for goals.",
  "The Stag": "Justice, responsibility, leadership.",
  "The Hooded Man": "Solitude, wisdom, inner search.",
  "The Wheel": "Cycles, change, fate.",
  "The Woodward": "Courage, balance, inner strength.",
  "The Mirror": "Reflection, patience, subconscious.",
  "The World Tree": "Completion, wholeness, end of a cycle.",
  "The Blasted Oak": "Sudden change, unexpected events.",
  "The Pole Star": "Hope, guidance, inspiration.",
  "The Moon on Water": "Subconscious, intuition, uncertainty.",
  "The Sun of Life": "Happiness, vitality, success.",
  "The Great Bear": "Rebirth, judgment, awakening.",
  "King of Arrows * Kingfisher": "Intellect, communication, justice, keen vision.",
  "Queen of Arrows * Swan": "Emotional balance, grace, intuition.",
  "Knight of Arrows * Hawk": "Speed, clarity, decisiveness.",
  "Page of Arrows * Wren": "Curiosity, new ideas, learning.",
  "Ace of Vessels * The Waters of Life": "Beginning of emotions, new relationships.",
  "Two of Vessels * Attraction": "Attraction, partnership, harmony.",
  "Three of Vessels * Joy": "Joy, celebration, friendship.",
  "Four of Vessels * Boredom": "Boredom, dissatisfaction, stagnation.",
  "Five of Vessels * Ecstasy": "Ecstasy, emotional intensity, excess.",
  "Six of Vessels * Reunion": "Reunion, facing the past, nostalgia.",
  "Seven of Vessels * Mourning": "Mourning, loss, emotional hardship.",
  "Eight of Vessels * Rebirth": "Rebirth, transformation, progress.",
  "Nine of Vessels * Generosity": "Generosity, sharing, abundance.",
  "Ten of Vessels * Happiness": "Happiness, family, peace.",
  "King of Vessels * Heron": "Wisdom, calm, emotional maturity.",
  "Queen of Vessels * Salmon": "Intuition, emotional depth, devotion.",
  "Knight of Vessels * Eel": "Adaptation, flow, flexibility.",
  "Page of Vessels * Otter": "Joy, playfulness, emotional openness.",
  "Ace of Stones * The Foundation of Life": "Foundation, security, new beginnings.",
  "Two of Stones * Challenge": "Challenge, search for balance, difficulty.",
  "Three of Stones * Creativity": "Creativity, collaboration, productivity.",
  "Four of Stones * Protection": "Protection, defense, safety.",
  "Five of Stones * Endurance": "Endurance, patience, facing difficulties.",
  "Six of Stones * Exploitation": "Exploitation, imbalance, injustice.",
  "Seven of Stones * Healing": "Healing, recovery, restoration.",
  "Eight of Stones * Skill": "Skill, mastery, development.",
  "Nine of Stones * Tradition": "Tradition, roots, continuity.",
  "Ten of Stones * Home": "Home, family, safe haven.",
  "Queen of Stones * Bear": "Strength, protection, motherhood.",
  "Knight of Stones * Horse": "Diligence, perseverance, progress.",
  "Page of Stones * Lynx": "Secrecy, observation, new knowledge."
};

const PLANET_INFO_EN = {
  Sun: 'Sun: Identity, ego, life energy',
  Moon: 'Moon: Emotions, inner world, habits',
  Mercury: 'Mercury: Mind, communication, learning',
  Venus: 'Venus: Love, values, aesthetics',
  Mars: 'Mars: Energy, motivation, drive',
  Jupiter: 'Jupiter: Luck, growth, philosophy',
  Saturn: 'Saturn: Responsibility, discipline, boundaries',
  Uranus: 'Uranus: Innovation, freedom, change',
  Neptune: 'Neptune: Imagination, intuition, inspiration',
  Pluto: 'Pluto: Transformation, power, crisis',
};

function getTarotMeaning(card) {
  return WILDWOOD_TAROT_EN[card] || '';
}
function getTarotLoadingText() {
  return 'Preparing your card...';
}

function PlanetTableEN({ positions }) {
  if (!positions || Object.keys(positions).length === 0) {
    return <div style={{color:'#f87171', fontSize:15, margin:'1rem 0'}}>Your information is incomplete or incorrect. Please enter your birth date, time, and coordinates correctly.</div>;
  }
  return (
    <div style={{display:'flex', justifyContent:'center', margin:'1.5rem 0'}}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
        gap: '1.2rem',
        width: '100%',
        maxWidth: 700,
        background: 'rgba(24,24,37,0.95)',
        borderRadius: 18,
        padding: '1.5rem',
        boxShadow: '0 2px 16px #a78bfa22',
        border: '2px solid #23234a',
      }}>
        {Object.entries(positions).map(([planet, pos]) => (
          <div key={planet} style={{
            background: '#181825',
            borderRadius: 12,
            padding: '1rem 0.5rem',
            textAlign: 'center',
            color: '#fff',
            boxShadow: '0 1px 6px #0002',
            border: '1.5px solid #a78bfa33',
            minWidth: 0,
          }}>
            <div style={{fontWeight:'bold', fontSize:18, color:'#a78bfa', marginBottom:4}}>{planet}</div>
            <div style={{fontSize:15, color:'#ffd700', marginBottom:2}}>{pos.sign}</div>
            <div style={{fontSize:14, color:'#38bdf8'}}>{pos.degree.toFixed(2)}°</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatDateForInputEN(date) {
  const pad = n => n.toString().padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

// --- City to Coordinates (OpenStreetMap Nominatim, EN) ---
async function fetchCoordsFromCityEN(city, country) {
  if (!city) return null;
  const q = encodeURIComponent(`${city}${country ? ', ' + country : ''}`);
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${q}`;
  try {
    const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
    const data = await res.json();
    if (data && data[0]) {
      return { lat: data[0].lat, lon: data[0].lon };
    }
    return null;
  } catch {
    return null;
  }
}

// --- English Tarot Card Draw ---
function TarotCardGenerativeEN() {
  const CARDS = React.useMemo(
    () => Object.entries(WILDWOOD_TAROT_EN).map(([title, meaning]) => {
      const base = title.includes(' * ') ? title.split(' * ')[0] : title;
      const file = base.replace(/\s+/g, '_') + '.png';
      // Support for future reversed meanings: if meaning is an object, {upright, reversed}
      return { title, meaning, file };
    }),
    []
  );
  const [cards, setCards] = React.useState([]); // [{card, reversed}]
  const [loadingCard, setLoadingCard] = React.useState(false);

  const handleDraw = () => {
    setLoadingCard(true);
    setCards([]);
    setTimeout(() => {
      // Draw 3 unique cards, each upright or reversed
      let indices = [];
      while (indices.length < 3) {
        let idx = Math.floor(Math.random() * CARDS.length);
        if (!indices.includes(idx)) indices.push(idx);
      }
      const drawn = indices.map(idx => {
        const reversed = Math.random() < 0.5;
        return { ...CARDS[idx], reversed };
      });
      setCards(drawn);
      setLoadingCard(false);
    }, 2000);
  };

  if (loadingCard) return (
    <div style={{border:'2px solid #ffd700', borderRadius:16, padding:16, width:'100%', background:'#222', color:'#ffd700', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', margin:'1rem auto', boxSizing:'border-box'}}>
      <div>Preparing your cards... 🔮</div>
    </div>
  );

  return (
    <div style={{border:'2px solid #ffd700', borderRadius:16, padding:16, width:'100%', background:'#222', color:'#ffd700', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', margin:'1rem auto', boxSizing:'border-box'}}>
      <div style={{display:'flex', flexDirection:'row', gap:18, justifyContent:'center', marginBottom:12}}>
        {cards.length === 0 ? (
          <div style={{color:'#888', fontSize:16, textAlign:'center', minWidth:180}}>No cards drawn yet.</div>
        ) : cards.map((card, i) => (
          <div key={i} style={{display:'flex', flexDirection:'column', alignItems:'center', minWidth:180}}>
            <div style={{fontWeight:'bold', marginBottom:6, fontSize:17, color:'#ffd700', textAlign:'center'}}>{card.title}</div>
            <img src={`/assets/tarot/${card.file}`} alt={card.title} style={{width:120, height:186, objectFit:'cover', borderRadius:8, marginBottom:8, boxShadow:'0 2px 8px #0007', transform: card.reversed ? 'rotate(180deg)' : 'none', transition:'transform 0.3s'}} />
            <div style={{marginTop:4, color:'#fff', fontSize:14, textAlign:'center'}}>
              <b>{card.reversed ? 'Reversed Meaning:' : 'Meaning:'}</b><br/>
              {/* If meaning is an object, use .reversed or .upright, else fallback */}
              {typeof card.meaning === 'object' ? (card.reversed ? (card.meaning.reversed || card.meaning.upright) : card.meaning.upright) : card.meaning}
            </div>
          </div>
        ))}
      </div>
      <button onClick={handleDraw} style={{marginTop:12, padding:'10px 28px', borderRadius:8, background:'#ffd700', color:'#181825', fontWeight:'bold', border:'none', fontSize:18}}>
        {cards.length === 0 ? 'Draw 3 Cards 🔮' : 'Draw Again 🔮'}
      </button>
    </div>
  );
}

// --- Tarot Grid EN ---
function TarotGridEN() {
  return (
    <div style={{width:'100%', display:'flex', flexDirection:'column', alignItems:'center', margin:'2rem 0 0 0'}}>
      <div style={{width:'100%', display:'flex', justifyContent:'center'}}>
        <TarotCardGenerativeEN />
      </div>
    </div>
  );
}

// --- Sinastri partner date/format helpers ---
function formatDateInput(val) {
  // Accepts 19970826 or 1997-08-26 or 1997/08/26, returns 1997-08-26
  if (!val) return '';
  let v = val.replace(/[^0-9]/g, '');
  if (v.length === 8) return `${v.slice(0,4)}-${v.slice(4,6)}-${v.slice(6,8)}`;
  return val;
}

function parseDateTimeInput(val) {
  // Accepts 19970826, 1997-08-26, 1997/08/26, 1997-08-26T12:30, 199708261230, etc.
  if (!val) return { date: '', time: '' };
  let v = val.replace(/[^0-9]/g, '');
  if (v.length === 8) {
    // Only date
    return { date: `${v.slice(0,4)}-${v.slice(4,6)}-${v.slice(6,8)}`, time: '' };
  }
  if (v.length === 12) {
    // Date + time
    return { date: `${v.slice(0,4)}-${v.slice(4,6)}-${v.slice(6,8)}`, time: `${v.slice(8,10)}:${v.slice(10,12)}` };
  }
  return { date: val, time: '' };
}

// --- Main App Component ---
export default function AstroAstrologyAppEN(props) {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showTarot, setShowTarot] = useState(false);
  const [birth, setBirth] = useState({
    date: '',
    lat: '',
    lon: '',
    city: '',
    country: ''
  });
  const [planetPositions, setPlanetPositions] = useState(null);
  const [userInfo, setUserInfo] = useState({ name: '', gender: '' });
  const [shareUrl, setShareUrl] = useState('');
  const [transitResult, setTransitResult] = useState('');
  const [sinastriResult, setSinastriResult] = useState('');
  const [qaInput, setQaInput] = useState('');
  const [qaResult, setQaResult] = useState('');
  const [partner, setPartner] = useState({ date: '', time: '', lat: '', lon: '', city: '', country: '' });
  const [partnerPositions, setPartnerPositions] = useState(null);
  const [horaryInput, setHoraryInput] = useState('');
  const [horaryResult, setHoraryResult] = useState('');
  const [horaryLocation, setHoraryLocation] = useState({ city: '', country: '', lat: '', lon: '' });
  const [sinastriLoading, setSinastriLoading] = useState(false);
  const [citySearchLoading, setCitySearchLoading] = useState(false);
  const [partnerCitySearchLoading, setPartnerCitySearchLoading] = useState(false);

  const handleBirthChange = e => {
    const { name, value } = e.target;
    setBirth(b => ({ ...b, [name]: value }));
  };

  const handleUserInfoChange = e => {
    const { name, value } = e.target;
    setUserInfo(u => ({ ...u, [name]: value }));
  };

  const handleCityBlurEN = async () => {
    if (birth.city) {
      setCitySearchLoading(true);
      const coords = await fetchCoordsFromCityEN(birth.city, birth.country);
      setCitySearchLoading(false);
      if (coords) {
        setBirth(b => ({ ...b, lat: coords.lat, lon: coords.lon }));
        setError('');
      } else {
        setError('City not found. Please enter coordinates manually.');
      }
    }
  };

  const handlePartnerCityBlurEN = async () => {
    if (partner.city) {
      setPartnerCitySearchLoading(true);
      const coords = await fetchCoordsFromCityEN(partner.city, partner.country);
      setPartnerCitySearchLoading(false);
      if (coords) {
        setPartner(p => ({ ...p, lat: coords.lat, lon: coords.lon }));
      }
    }
  };

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult('');
    const prompt = `User's question or request: ${input}`;
    const res = await getGroqInterpretationEN(prompt);
    setResult(res);
    setTimeout(() => {
      const el = document.getElementById('general-interpretation-result');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
    setLoading(false);
  }, [input]);

  const handleTransit = async () => {
    if (!planetPositions) return;
    setLoading(true);
    setTransitResult('');
    const today = new Date();
    const todayStr = today.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) + ' ' + today.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const transitPositions = {}; // Replace with actual transit calculation
    const natalStr = Object.entries(planetPositions).map(([p, pos]) => `${p}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ');
    const transitStr = Object.entries(transitPositions).map(([p, pos]) => `${p}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ');
    const prompt = `Based on the following natal chart and today's transit positions, provide a detailed and professional English interpretation.\n\nNatal chart planets: ${natalStr}\nToday's transit planets: ${transitStr}\nToday's date: ${todayStr}`;
    const res = await getGroqInterpretationEN(prompt);
    setTransitResult(res);
    setLoading(false);
  };

  const handleHorary = async (e) => {
    e.preventDefault();
    setLoading(true);
    setHoraryResult('');
    // Use current date/time and user's ACTUAL current location (not birth location)
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-GB');
    const timeStr = now.toTimeString().slice(0,5);
    const city = horaryLocation.city || '-';
    const country = horaryLocation.country || '-';
    const lat = horaryLocation.lat || '-';
    const lon = horaryLocation.lon || '-';
    const prompt = `You are a professional horary astrologer. Provide a detailed, professional, and friendly English horary astrology interpretation for the following question. Use the chart of the moment the question is asked (date, time, and current location below). Do NOT use the natal chart or birth location. Base your answer on horary/transit principles only.\n\nQuestion: ${horaryInput}\nAsked on: ${dateStr} at ${timeStr}\nLocation: ${city}, ${country} (lat: ${lat}, lon: ${lon})`;
    const res = await getGroqInterpretationEN(prompt);
    setHoraryResult(res);
    setLoading(false);
    setTimeout(() => {
      const el = document.getElementById('horary-interpretation-result');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  };

  const handleTarotButton = () => {
    window.__drawTarotCardEN = true;
    setShowTarot(v => !v);
  };

  // --- SEO: AstroAstrologyAppEN component meta for better search visibility ---
  // If using Astro, you can set <title>, <meta> etc. in the page, but for React SPA, add structured data and meta tags dynamically if needed.
  // For Astro/Next.js, prefer static head tags. For React SPA, you can use react-helmet or similar.
  // Here, we add a JSON-LD structured data script for the main app:
  if (typeof window !== 'undefined' && document) {
    // Remove old if exists
    const old = document.getElementById('astro-astrology-app-en-ld');
    if (old) old.remove();
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.id = 'astro-astrology-app-en-ld';
    script.innerHTML = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebApplication',
      'name': 'Astrology AI Premium (English)',
      'description': 'AI-powered astrology, tarot, synastry, horary, and more. Draw 3 tarot cards, get natal chart, synastry, and horary interpretations instantly. English-only, modern, mobile-friendly.',
      'applicationCategory': 'LifestyleApplication',
      'operatingSystem': 'All',
      'url': window.location.href,
      'inLanguage': 'en',
      'offers': {
        '@type': 'Offer',
        'price': '0',
        'priceCurrency': 'USD',
        'availability': 'https://schema.org/InStock'
      },
      'aggregateRating': {
        '@type': 'AggregateRating',
        'ratingValue': '4.9',
        'reviewCount': '1200'
      }
    });
    document.head.appendChild(script);
  }

  return (
    <div style={{ width: '100%', maxWidth: '1400px', margin: '2rem auto', background: '#0f172a', borderRadius: 24, boxShadow: '0 4px 32px #0002', padding: '2.5vw', color: '#fff', boxSizing: 'border-box' }}>
      <h1 style={{ fontSize: 32, fontWeight: 'bold', textAlign: 'center', marginBottom: 24, letterSpacing: 1 }}>Astrology AI Premium (English)</h1>
      <form onSubmit={async e => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult('');
        setPlanetPositions(null);
        try {
          if (!birth.date || !birth.lat || !birth.lon) throw new Error('Please fill in all fields.');
          const dateObj = new Date(birth.date);
          const lat = parseFloat(birth.lat);
          const lon = parseFloat(birth.lon);
          if (isNaN(lat) || isNaN(lon)) throw new Error('Enter valid coordinates.');
          // Prepare a prompt for the English interpretation (no chart visual)
          const prompt = `Please provide a detailed, professional, and friendly English natal chart interpretation for the following birth data.\n\nName: ${userInfo.name || '-'}\nGender: ${userInfo.gender || '-'}\nBirth date & time: ${birth.date}${birth.date && birth.date.includes('T') ? '' : ''}\nLatitude: ${birth.lat}\nLongitude: ${birth.lon}\nCity: ${birth.city || '-'}\nCountry: ${birth.country || '-'}`;
          const res = await getGroqInterpretationEN(prompt);
          setResult(res);
          setTimeout(() => {
            const el = document.getElementById('natal-interpretation-result');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 100);
        } catch (e) {
          setError(e.message);
        }
        setLoading(false);
      }} style={{display:'flex', flexDirection:'column', gap:14, marginBottom:28, background:'#181825', borderRadius:14, padding:20, boxShadow:'0 2px 12px #0001'}}>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Name</label>
            <input type="text" name="name" value={userInfo.name} onChange={handleUserInfoChange} placeholder="Your name (optional)" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} autoComplete="off" />
          </div>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Gender</label>
            <select name="gender" value={userInfo.gender} onChange={handleUserInfoChange} style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}}>
              <option value="">Prefer not to say</option>
              <option value="Female">Female</option>
              <option value="Male">Male</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>City</label>
            <input type="text" name="city" value={birth.city} onChange={handleBirthChange} onBlur={handleCityBlurEN} placeholder="London" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} autoComplete="off" />
            {citySearchLoading && <div style={{color:'#a78bfa', fontSize:13}}>Searching city...</div>}
          </div>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Country</label>
            <input type="text" name="country" value={birth.country} onChange={handleBirthChange} placeholder="UK" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} autoComplete="off" />
          </div>
        </div>
        <div style={{display:'flex', flexDirection:'column', gap:6}}>
          <label>Birth Date & Time</label>
          <input type="datetime-local" name="date" value={birth.date} onChange={handleBirthChange} style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} required />
        </div>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', flexDirection:'column', gap:6}}>
            <label>Latitude (lat)</label>
            <input type="number" step="0.0001" name="lat" value={birth.lat} onChange={handleBirthChange} placeholder="51.5074" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} required />
          </div>
          <div style={{flex:1, display:'flex', flexDirection:'column', gap:6}}>
            <label>Longitude (lon)</label>
            <input type="number" step="0.0001" name="lon" value={birth.lon} onChange={handleBirthChange} placeholder="-0.1278" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} required />
          </div>
        </div>
        <button type="submit" style={{padding:'12px 0', borderRadius:9, background:'#a78bfa', color:'#181825', fontWeight:'bold', border:'none', fontSize:17, marginTop:6, boxShadow:'0 1px 4px #a78bfa33'}} disabled={loading}>
          {loading ? 'Calculating...' : 'Get Natal Chart Interpretation'}
        </button>
      </form>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 0 }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Examples: 'What advice do you have for me today?', 'How will my love life be?', 'Draw a tarot card', 'Palm reading interpretation', 'What do you foresee for my career?'"
          rows={3}
          style={{ padding: 12, borderRadius: 8, border: '1px solid #a78bfa', fontSize: 16, resize: 'vertical' }}
        />
        <button type="submit" style={{ padding: '10px 0', borderRadius: 8, background: '#a78bfa', color: '#181825', fontWeight: 'bold', border: 'none', fontSize: 16, marginBottom: 0 }} disabled={loading || !input}>
          {loading ? 'Fetching interpretation...' : 'Get Interpretation'}
        </button>
      </form>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16, margin: '18px 0 24px 0' }}>
        <button onClick={handleTarotButton} style={{ padding: '8px 16px', borderRadius: 8, background: '#ffd700', color: '#181825', fontWeight: 'bold', border: 'none' }}>Tarot Card</button>
        <button onClick={handleTransit} style={{ padding: '8px 16px', borderRadius: 8, background: '#38bdf8', color: '#181825', fontWeight: 'bold', border: 'none' }} disabled={!planetPositions}>Transit Analysis</button>
      </div>
      {/* --- Always visible: Sinastri, Horary sections --- */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 24, marginBottom: 32 }}>
        <div style={{ minWidth: 320, flex: 1, maxWidth: 420, order: 1 }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, color: '#38bdf8', marginBottom: 8 }}>Sinastri</h2>
          <form onSubmit={async e => {
            e.preventDefault();
            setSinastriLoading(true);
            setSinastriResult('');
            const prompt = `For the following two natal charts, provide a detailed and professional English synastry (relationship compatibility) interpretation.\n\nUser 1: ${JSON.stringify(birth)}\nUser 2: ${JSON.stringify(partner)}`;
            const res = await getGroqInterpretationEN(prompt);
            setSinastriResult(res);
            setSinastriLoading(false);
          }} style={{ display: 'flex', flexDirection: 'column', gap: 8, background: '#181825', borderRadius: 10, padding: 14, marginBottom: 8 }}>
            <input type="text" placeholder="Partner's name (optional)" value={partner.name || ''} name="name" onChange={e => setPartner(p => ({ ...p, name: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="datetime-local" placeholder="Partner's birth date & time" value={partner.date ? `${partner.date}${partner.time ? 'T'+partner.time : ''}` : ''}
              name="date"
              onChange={e => {
                let v = e.target.value;
                let [date, time] = v.split('T');
                setPartner(p => ({ ...p, date, time: time || '' }));
              }}
              style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }}
            />
            <input type="text" placeholder="Partner's city" value={partner.city} name="city" onChange={e => setPartner(p => ({ ...p, city: e.target.value }))} onBlur={handlePartnerCityBlurEN} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            {partnerCitySearchLoading && <div style={{color:'#a78bfa', fontSize:13}}>Searching city...</div>}
            <input type="text" placeholder="Partner's country" value={partner.country} name="country" onChange={e => setPartner(p => ({ ...p, country: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Partner's latitude" value={partner.lat} name="lat" onChange={e => setPartner(p => ({ ...p, lat: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Partner's longitude" value={partner.lon} name="lon" onChange={e => setPartner(p => ({ ...p, lon: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <button type="submit" style={{ padding: '8px 0', borderRadius: 7, background: '#38bdf8', color: '#181825', fontWeight: 'bold', border: 'none', fontSize: 16, marginTop: 4 }} disabled={sinastriLoading}>{sinastriLoading ? 'Calculating...' : 'Get Synastry Interpretation'}</button>
          </form>
          {sinastriResult && <div style={{ background: '#23234a', borderRadius: 8, padding: 12, color: '#fff', whiteSpace: 'pre-line', marginTop: 8 }}>{sinastriResult}</div>}
        </div>
        <div style={{ minWidth: 320, flex: 1, maxWidth: 420, order: 3 }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, color: '#a78bfa', marginBottom: 8 }}>Horary</h2>
          <form onSubmit={handleHorary} style={{ display: 'flex', flexDirection: 'column', gap: 8, background: '#181825', borderRadius: 10, padding: 14, marginBottom: 8 }}>
            <input type="text" placeholder="Your horary question (English)" value={horaryInput} onChange={e => setHoraryInput(e.target.value)} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="text" placeholder="Current city (for horary)" value={horaryLocation.city} onChange={async e => {
              const city = e.target.value;
              setHoraryLocation(l => ({ ...l, city }));
              if (city && horaryLocation.country) {
                const coords = await fetchCoordsFromCityEN(city, horaryLocation.country);
                if (coords) setHoraryLocation(l => ({ ...l, lat: coords.lat, lon: coords.lon }));
              }
            }} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="text" placeholder="Current country (for horary)" value={horaryLocation.country} onChange={async e => {
              const country = e.target.value;
              setHoraryLocation(l => ({ ...l, country }));
              if (horaryLocation.city && country) {
                const coords = await fetchCoordsFromCityEN(horaryLocation.city, country);
                if (coords) setHoraryLocation(l => ({ ...l, lat: coords.lat, lon: coords.lon }));
              }
            }} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Current latitude (for horary)" value={horaryLocation.lat} onChange={e => setHoraryLocation(l => ({ ...l, lat: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Current longitude (for horary)" value={horaryLocation.lon} onChange={e => setHoraryLocation(l => ({ ...l, lon: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <button type="submit" style={{ padding: '8px 0', borderRadius: 7, background: '#a78bfa', color: '#181825', fontWeight: 'bold', border: 'none', fontSize: 16, marginTop: 4 }} disabled={loading}>{loading ? 'Calculating...' : 'Get Horary Interpretation'}</button>
          </form>
          {horaryResult && (
            <div id="horary-interpretation-result" style={{ background: '#0f172a', borderRadius: 10, padding: 12, color: '#38bdf8', marginTop: 10, whiteSpace: 'pre-line', width: '100%', boxSizing: 'border-box', overflowWrap: 'break-word' }}>
              <b>Horary Interpretation:</b><br />{horaryResult}
            </div>
          )}
        </div>
      </div>
      {/* Tarot section moved below Sinastri and Horary */}
      <div style={{ width: '100%', maxWidth: 420, margin: '0 auto 32px auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, color: '#ffd700', marginBottom: 8, textAlign: 'center' }}>Tarot</h2>
        <TarotGridEN />
      </div>
      {result && (
        <div id={result && result.startsWith('Please provide a detailed, professional, and friendly English natal chart interpretation') ? 'natal-interpretation-result' : 'general-interpretation-result'} style={{ background: '#181825', borderRadius: 12, padding: 16, color: '#fff', whiteSpace: 'pre-line', marginTop: 16, position: 'relative', width: '100%', boxSizing: 'border-box', overflowWrap: 'break-word' }}>
          <div style={{ paddingTop: 32 }}>{result}</div>
        </div>
      )}
      <div style={{ color: '#888', textAlign: 'center', marginTop: 32 }}>
        <b>Astrology AI Premium (English)</b><br />
        <i>All features and interpretations are in English for the English homepage.</i>
      </div>
    </div>
  );
}
