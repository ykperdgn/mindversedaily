import React, { useState, useCallback, useRef } from 'react';
import { planetposition, julian } from 'astronomia';
import jsPDF from 'jspdf';
import { getGroqInterpretation } from '../lib/groqApi.ts';

// --- Yüksek Kalite Türkçe Çeviri Kuralları (Groq mantığı) ---
const TURKISH_FORCE = `
KURALLAR:
- Doğal ve akıcı Türkçe kullan
- Teknik terimleri Türkçeleştir
- Orijinal anlamı ve tonu koru
- Sadece verilen bilgiyi aktar, açıklama veya selamlama yapma
- İngilizce kelime kullanma
- Uydurma veya hatalı terim kullanma
- Sadece aşağıdaki gezegen ve burç isimlerini kullanabilirsin: Gezegenler: Güneş, Ay, Merkür, Venüs, Mars, Jüpiter, Satürn, Uranüs, Neptün, Plüton, Kuzey Düğümü, Güney Düğümü. Burçlar: Koç, Boğa, İkizler, Yengeç, Aslan, Başak, Terazi, Akrep, Yay, Oğlak, Kova, Balık.
`;

// --- Türkçe burç ve gezegen isimleri referansı ---
const VALID_SIGNS = ['Koç','Boğa','İkizler','Yengeç','Aslan','Başak','Terazi','Akrep','Yay','Oğlak','Kova','Balık'];
const VALID_PLANETS = ['Güneş','Ay','Merkür','Venüs','Mars','Jüpiter','Satürn','Uranüs','Neptün','Plüton','Kuzey Düğümü','Güney Düğümü'];
const FORBIDDEN_WORDS = [
  'Koperno','Najsilili','mezhesinde','Nöbetçi','Berbat','Kanat','Kırmızı Dünya','pessoa','siyaset','ihtimalce','olasılık','Kovaluşta','Leo mezhesinde','Akrep mezhesinde','Başak mezhesinde','Yay mezhesinde','Balık mezhesinde','Oğlak mezhesinde','Koç mezhesinde','Kova mezhesinde','Terazi mezhesinde','İkizler mezhesinde','Boğa mezhesinde','Yengeç mezhesinde','Venüs mezhesinde','Saturn mezhesinde','Uranüs mezhesinde','Neptün mezhesinde','Plüton mezhesinde','Merkür mezhesinde','Güneş mezhesinde','Ay mezhesinde','Nöbetçi','Kütleşimi'
];
function hasForbiddenWords(text) {
  if (!text) return false;
  for (const word of FORBIDDEN_WORDS) {
    if (text.toLowerCase().includes(word.toLowerCase())) return true;
  }
  // Ayrıca, gezegen/burç isimleri dışında bir kelimeyle başlıyorsa da uyarı ver
  const planetSignRegex = new RegExp(`(${VALID_PLANETS.concat(VALID_SIGNS).join('|')})`, 'i');
  if (!planetSignRegex.test(text)) return true;
  return false;
}

// --- İngilizce veya karışık dil kontrol fonksiyonu ---
function isEnglishOrMixed(text) {
  if (!text) return false;
  // Türkçe karakter oranı düşükse veya metnin %30'dan fazlası İngilizce ise uyarı ver, ama birkaç İngilizce kelimeye izin ver
  const turkishChars = (text.match(/[çğıöşüÇĞİÖŞÜ]/g) || []).length;
  const totalChars = text.length;
  const trRatio = turkishChars / totalChars;
  // İngilizce kelime sayısı
  const enWordsArr = text.match(/\b(the|and|with|for|you|your|summary|compatibility|person|sign|overall|analysis|connection|potential|growth|development|relationship|trust|understanding|experience|leader|justice|finance|commerce|management|analytical|feedback|success|balance|exploration|adventure|freedom|discipline|responsibility|spiritual|commitment|revolution|innovation|transcendence|illusion|power|control|intense|transformational|curiosity|analytical|mind|passion|intensity|independent|progressive|ideas|compassion|empathy|emotional|needs|security|comfort|balance|harmony|nurturing|caring|nature|precision|attention|detail|curiosity|versatility|dynamic|adventurous|action|discipline|responsibility|freedom|exploration|stability|structure|excitement|adventure|growth|expansion|depth|intensity|intellectual|exploration|humanitarian|pursuits|progressive|innovative|ideas|passion|intensity|commitment|responsibility|independence|humanitarianism|spirituality|compassion|empathetic|compassionate|nature|restless|curious|balance|harmony|spiritual|philosophical|transcendence|illusion|expansion|exploration|spiritual|connection|surrender|restless|exploratory|spirit|intense|transformational|power|control|intensity|depth|intellectual|revolution|upheaval|curiosity|analytical|mind|passionate|intense|nature|complementary|energies|approaches|enhance|strengths|weaknesses|mutual|respect|trust|understanding|relationship|powerful|profound|experience)\b/gi) || [];
  const enWordCount = enWordsArr.length;
  const wordCount = text.split(/\s+/).length;
  // Eğer Türkçe karakter oranı çok düşükse veya İngilizce kelime oranı %30'dan fazlaysa uyarı ver
  if (trRatio < 0.01 || (enWordCount / wordCount) > 0.3) return true;
  return false;
}

// --- Türkçe AI yanıtı için güvenli fonksiyon ---
async function ensureTurkishAIResponse(prompt) {
  let response = await fetchGroqInterpretation(prompt);
  // Burada isterseniz Türkçe kontrolü ve retry ekleyebilirsiniz
  return response;
}

// Türkçe AI yanıtı için Groq API çağrısı
async function fetchGroqInterpretation(prompt) {
  try {
    return await getGroqInterpretation(prompt);
  } catch (e) {
    return 'Groq API hatası: ' + (e?.message || e);
  }
}

// --- Astronomia ile gezegen pozisyonu hesaplama ---
// Güneş, Ay, Merkür, Venüs, Mars, Jüpiter, Satürn, Uranüs, Neptün, Plüton
const PLANETS = [
  { name: 'Sun', key: 'sun' },
  { name: 'Moon', key: 'moon' },
  { name: 'Mercury', key: 'mercury' },
  { name: 'Venus', key: 'venus' },
  { name: 'Mars', key: 'mars' },
  { name: 'Jupiter', key: 'jupiter' },
  { name: 'Saturn', key: 'saturn' },
  { name: 'Uranus', key: 'uranus' },
  { name: 'Neptune', key: 'neptune' },
  { name: 'Pluto', key: 'pluto' },
];

// --- Türkçe burç isimleri eşlemesi ---
const TURKISH_SIGNS = ['Koç','Boğa','İkizler','Yengeç','Aslan','Başak','Terazi','Akrep','Yay','Oğlak','Kova','Balık'];
const PLANET_TR = {
  Sun: 'Güneş', Moon: 'Ay', Mercury: 'Merkür', Venus: 'Venüs', Mars: 'Mars', Jupiter: 'Jüpiter', Saturn: 'Satürn', Uranus: 'Uranüs', Neptune: 'Neptün', Pluto: 'Plüton'
};

async function getPlanetPositions({ date, latitude, longitude }) {
  // date: JS Date objesi
  // latitude, longitude: float
  const jd = julian.CalendarGregorianToJD(date.getFullYear(), date.getMonth()+1, date.getDate() + (date.getHours()/24 + date.getMinutes()/1440));
  const positions = {};
  for (const planet of PLANETS) {
    try {
      const eph = planetposition[planet.key] ? new planetposition[planet.key](planetposition[planet.key].data) : null;
      if (!eph) continue;
      // Güneş ve Ay için farklı, diğerleri için farklı fonksiyonlar var
      let eclLon = 0;
      if (planet.key === 'sun') {
        eclLon = planetposition.sun.trueLongitude(jd);
      } else if (planet.key === 'moon') {
        eclLon = planetposition.moon.position(jd).lon;
      } else {
        eclLon = eph ? eph.position2000(jd).lon : 0;
      }
      // Burç ve derece hesapla
      const signIndex = Math.floor((eclLon % 360) / 30);
      const sign = TURKISH_SIGNS[signIndex];
      const degree = (eclLon % 30);
      positions[planet.name] = { sign, signIndex, degree, lon: eclLon };
    } catch (e) {
      // Hata olursa gezegen atlanır
    }
  }
  return positions;
}

// --- Bugünkü gezegen konumlarını hesapla (transit için) ---
async function getCurrentTransitPositions() {
  const now = new Date();
  // İstanbul merkez alınır, istenirse kullanıcıdan alınabilir
  const latitude = 41.0082;
  const longitude = 28.9784;
  return await getPlanetPositions({ date: now, latitude, longitude });
}

// --- Tarih formatlama fonksiyonu ---
function formatDateForInput(date) {
  // YYYY-MM-DDTHH:MM için
  const pad = n => n.toString().padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

// --- Şehirden koordinat bulma fonksiyonu (OpenStreetMap Nominatim) ---
async function fetchCoordsFromCity(city, country) {
  if (!city) return null;
  const q = encodeURIComponent(`${city}${country ? ', ' + country : ''}`);
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${q}`;
  try {
    const res = await fetch(url, { headers: { 'Accept-Language': 'tr' } });
    const data = await res.json();
    if (data && data[0]) {
      return { lat: data[0].lat, lon: data[0].lon };
    }
    return null;
  } catch {
    return null;
  }
}

// --- Gezegen Tablosu (Premium, tooltip ve responsive) ---
const PLANET_INFO = {
  Sun: 'Güneş: Kimlik, ego, yaşam enerjisi',
  Moon: 'Ay: Duygular, iç dünya, alışkanlıklar',
  Mercury: 'Merkür: Zihin, iletişim, öğrenme',
  Venus: 'Venüs: Aşk, değerler, estetik',
  Mars: 'Mars: Enerji, motivasyon, mücadele',
  Jupiter: 'Jüpiter: Şans, büyüme, felsefe',
  Saturn: 'Satürn: Sorumluluk, disiplin, sınırlar',
  Uranus: 'Uranüs: Yenilik, özgürlük, değişim',
  Neptune: 'Neptün: Hayal gücü, sezgi, ilham',
  Pluto: 'Plüton: Dönüşüm, güç, kriz',
};
function PlanetTable({ positions }) {
  if (!positions || Object.keys(positions).length === 0) {
    return <div style={{color:'#f87171', fontSize:15, margin:'1rem 0'}}>Bilgileriniz eksik veya hatalı. Lütfen doğum tarihi, saat ve koordinatları eksiksiz ve doğru girin.</div>;
  }
  return (
    <div style={{overflowX:'auto'}}>
      <table style={{minWidth:340, width:'100%', background:'#181825', color:'#a78bfa', borderRadius:10, margin:'1rem 0', fontSize:15, boxShadow:'0 2px 12px #a78bfa22'}}>
        <thead>
          <tr style={{background:'#312e81'}}>
            <th style={{padding:'8px 6px'}}>Gezegen</th>
            <th style={{padding:'8px 6px'}}>Burç</th>
            <th style={{padding:'8px 6px'}}>Derece</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(positions).map(([planet, pos]) => (
            <tr key={planet} style={{borderBottom:'1px solid #312e81'}}>
              <td style={{position:'relative', padding:'8px 6px', cursor:'help'}} title={PLANET_INFO[planet] || ''}>
                <span style={{fontWeight:'bold'}}>{PLANET_TR[planet] || planet}</span>
                {PLANET_INFO[planet] && (
                  <span style={{marginLeft:6, fontSize:13, color:'#fbbf24', opacity:0.7}} title={PLANET_INFO[planet]}>ⓘ</span>
                )}
              </td>
              <td style={{padding:'8px 6px'}}>{pos.sign}</td>
              <td style={{padding:'8px 6px'}}>{pos.degree.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{fontSize:12, color:'#a78bfa', opacity:0.7, marginTop:-8, marginBottom:8}}>Gezegen adının üstüne gelerek anlamını görebilirsiniz.</div>
    </div>
  );
}

// --- Premium: Gezegen Detay Modalı ---
function PlanetDetailModal({ planet, pos, open, onClose }) {
  if (!open) return null;
  return (
    <div style={{position:'fixed', top:0, left:0, width:'100vw', height:'100vh', background:'#000a', zIndex:1000, display:'flex', alignItems:'center', justifyContent:'center'}} onClick={onClose}>
      <div style={{background:'#181825', borderRadius:16, padding:32, minWidth:320, color:'#fff', boxShadow:'0 4px 32px #0008', position:'relative'}} onClick={e=>e.stopPropagation()}>
        <button onClick={onClose} style={{position:'absolute', top:12, right:16, background:'none', border:'none', color:'#a78bfa', fontSize:22, cursor:'pointer'}}>✖</button>
        <div style={{fontSize:32, textAlign:'center', marginBottom:8}}>{planet}</div>
        <div style={{fontSize:18, color:'#fbbf24', textAlign:'center', marginBottom:16}}>{pos.sign} ({pos.degree.toFixed(2)}°)</div>
        <div style={{fontSize:15, marginBottom:16}}>{PLANET_INFO[planet] || ''}</div>
        <div style={{fontSize:13, color:'#a78bfa', opacity:0.8}}>Burç: {pos.sign}, Derece: {pos.degree.toFixed(2)}</div>
      </div>
    </div>
  );
}

// --- Premium: SVG Doğum Haritası (Natal Chart) ---
function ChartWheelV2({ positions }) {
  if (!positions || Object.keys(positions).length === 0) {
    return <div style={{color:'#f87171', fontSize:15, margin:'1rem 0'}}>Yıldız haritası için geçerli gezegen pozisyonu bulunamadı.</div>;
  }
  const [modalPlanet, setModalPlanet] = React.useState(null);
  const [modalPos, setModalPos] = React.useState(null);
  // Modern ve profesyonel harita için parametreler
  const size = 360;
  const rOuter = 150;
  const rInner = 110;
  const cx = size/2, cy = size/2;
  const zodiac = [
    { name: 'Koç', symbol: '\u2648', color: '#FF6B6B' },
    { name: 'Boğa', symbol: '\u2649', color: '#FFD166' },
    { name: 'İkizler', symbol: '\u264A', color: '#06D6A0' },
    { name: 'Yengeç', symbol: '\u264B', color: '#118AB2' },
    { name: 'Aslan', symbol: '\u264C', color: '#F9C74F' },
    { name: 'Başak', symbol: '\u264D', color: '#43AA8B' },
    { name: 'Terazi', symbol: '\u264E', color: '#577590' },
    { name: 'Akrep', symbol: '\u264F', color: '#B5838D' },
    { name: 'Yay', symbol: '\u2650', color: '#FFB4A2' },
    { name: 'Oğlak', symbol: '\u2651', color: '#A3A380' },
    { name: 'Kova', symbol: '\u2652', color: '#4D908E' },
    { name: 'Balık', symbol: '\u2653', color: '#577590' }
  ];
  const PLANET_SYMBOLS = {
    Sun: '\u2609', Moon: '\u263D', Mercury: '\u263F', Venus: '\u2640', Mars: '\u2642', Jupiter: '\u2643', Saturn: '\u2644', Uranus: '\u2645', Neptune: '\u2646', Pluto: '\u2647'
  };
  // Burç dilimleri
  const zodiacSectors = zodiac.map((sign, i) => {
    const start = (i*30-90)*Math.PI/180, end = ((i+1)*30-90)*Math.PI/180;
    const x1 = cx + rOuter*Math.cos(start), y1 = cy + rOuter*Math.sin(start);
    const x2 = cx + rOuter*Math.cos(end), y2 = cy + rOuter*Math.sin(end);
    const x3 = cx + rInner*Math.cos(end), y3 = cy + rInner*Math.sin(end);
    const x4 = cx + rInner*Math.cos(start), y4 = cy + rInner*Math.sin(start);
    return (
      <g key={sign.name}>
        <path d={`M${x1},${y1} A${rOuter},${rOuter} 0 0,1 ${x2},${y2} L${x3},${y3} A${rInner},${rInner} 0 0,0 ${x4},${y4} Z`} fill={sign.color} opacity={0.13} stroke="#fff" strokeWidth={0.5}/>
        <text x={cx + (rOuter+18)*Math.cos((start+end)/2)} y={cy + (rOuter+18)*Math.sin((start+end)/2)+6} textAnchor="middle" fontSize={20} fill={sign.color} style={{fontWeight:'bold'}}>{String.fromCharCode(parseInt(sign.symbol.replace('\\u',''),16))}</text>
        <text x={cx + (rInner-24)*Math.cos((start+end)/2)} y={cy + (rInner-24)*Math.sin((start+end)/2)+6} textAnchor="middle" fontSize={13} fill="#fff">{sign.name}</text>
      </g>
    );
  });
  // Gezegenler
  const planetNodes = positions ? Object.entries(positions).map(([planet, pos], i) => {
    const deg = pos.signIndex * 30 + pos.degree;
    const rad = (deg-90) * Math.PI/180;
    const px = cx + (rInner-36) * Math.cos(rad);
    const py = cy + (rInner-36) * Math.sin(rad);
    return (
      <g key={planet}>
        <circle cx={px} cy={py} r={15} fill="#fff" opacity="0.9" stroke="#a78bfa" strokeWidth={2} />
        <text x={px} y={py+7} textAnchor="middle" fontSize={22} fill="#a78bfa" style={{fontWeight:'bold',cursor:'pointer'}} title={PLANET_INFO[planet]||planet}
          onClick={()=>{setModalPlanet(planet);setModalPos(pos);}}>
          {String.fromCharCode(parseInt(PLANET_SYMBOLS[planet].replace('\\u',''),16))}
        </text>
      </g>
    );
  }) : null;
  return (
    <div style={{textAlign:'center', margin:'2rem 0'}}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{background:'#10101a', borderRadius:'50%', boxShadow:'0 2px 16px #a78bfa22', border:'2px solid #23234a'}}>
        {/* Burç dilimleri */}
        {zodiacSectors}
        {/* Gezegenler */}
        {planetNodes}
        {/* Dış çember */}
        <circle cx={cx} cy={cy} r={rOuter} fill="none" stroke="#a78bfa" strokeWidth={2}/>
        {/* İç çember */}
        <circle cx={cx} cy={cy} r={rInner} fill="none" stroke="#a78bfa" strokeWidth={1}/>
      </svg>
      <div style={{fontSize:14, color:'#a78bfa', marginTop:8}}>Doğum haritası: Burçlar, gezegenler ve modern profesyonel görünüm</div>
      <PlanetDetailModal planet={modalPlanet} pos={modalPos} open={!!modalPlanet} onClose={()=>setModalPlanet(null)} />
    </div>
  );
}

// --- Wildwood Tarot Kartları Türkçe Anlamlar ---
const WILDWOOD_TAROT_TR = {
  // Majör Arkana
  "The Wanderer": "Deli (The Fool)",
  "The Shaman": "Büyücü (The Magician)",
  "The Seer": "Azize (The High Priestess)",
  "The Green Woman": "İmparatoriçe (The Empress)",
  "The Green Man": "İmparator (The Emperor)",
  "The Ancestor": "Başrahibe (The Hierophant)",
  "The Forest Lovers": "Aşıklar (The Lovers)",
  "The Archer": "Savaş Arabası (The Chariot)",
  "The Stag": "Güç (Strength)",
  "The Hooded Man": "Ermiş (The Hermit)",
  "The Wheel": "Kader Çarkı (Wheel of Fortune)",
  "The Woodward": "Adalet (Justice)",
  "The Mirror": "Asılan Adam (The Hanged Man)",
  "The Journey": "Ölüm (Death)",
  "Balance": "Denge (Temperance)",
  "The Guardian": "Şeytan (The Devil)",
  "The Blasted Oak": "Kule (The Tower)",
  "The Pole Star": "Yıldız (The Star)",
  "The Moon on Water": "Ay (The Moon)",
  "The Sun of Life": "Güneş (The Sun)",
  "The Great Bear": "Mahkeme (Judgement)",
  "The World Tree": "Dünya (The World)",
  // Minör Arkana kartları
  "King of Arrows * Kingfisher": "Zeka, iletişim, adalet, keskin görüş.",
  "Queen of Arrows * Swan": "Duygusal denge, zarafet, sezgi.",
  "Knight of Arrows * Hawk": "Hız, netlik, kararlılık.",
  "Page of Arrows * Wren": "Merak, yeni fikirler, öğrenme.",
  "Ace of Arrows * The Breath of Life": "Yeni başlangıçlar, ilham, fikir.",
  "Two of Arrows * Injustice": "Kararsızlık, adaletsizlik, içsel çatışma.",
  "Three of Arrows * Jealousy": "Kıskançlık, kalp kırıklığı, üzüntü.",
  "Four of Arrows * Rest": "Dinlenme, iyileşme, içe dönüş.",
  "Five of Arrows * Frustration": "Hayal kırıklığı, engeller, mücadele.",
  "Six of Arrows * Transition": "Geçiş, değişim, yolculuk.",
  "Seven of Arrows * Insecurity": "Güvensizlik, şüphe, endişe.",
  "Eight of Arrows * Struggle": "Zorluk, mücadele, engeller.",
  "Nine of Arrows * Dedication": "Adanmışlık, özveri, çaba.",
  "Ten of Arrows * Instruction": "Öğrenme, öğretme, bilgi aktarımı.",
  "King of Bows * Adder": "Liderlik, karizma, dönüşüm.",
  "Queen of Bows * Hare": "Yaratıcılık, sezgi, zarafet.",
  "Knight of Bows * Fox": "Kurnazlık, çeviklik, fırsatçılık.",
  "Page of Bows * Stoat": "Merak, enerji, yeni başlangıçlar.",
  "Ace of Bows * Spark of Life": "Hayat kıvılcımı, yeni enerji, motivasyon.",
  "Two of Bows * Decision": "Karar verme, seçenekler, planlama.",
  "Three of Bows * Fulfilment": "Tatmin, başarı, ilerleme.",
  "Four of Bows * Celebration": "Kutlama, mutluluk, birlik.",
  "Five of Bows * Empowerment": "Güçlenme, rekabet, mücadele.",
  "Six of Bows * Abundance": "Bolluk, bereket, paylaşım.",
  "Seven of Bows * Clearance": "Temizlik, arınma, engelleri aşma.",
  "Eight of Bows * Hearthfire": "Aile, sıcaklık, topluluk.",
  "Nine of Bows * Respect": "Saygı, direnç, tecrübe.",
  "Ten of Bows * Responsibility": "Sorumluluk, yük, görev.",
  "King of Vessels * Heron": "Duygusal denge, bilgelik, sabır.",
  "Queen of Vessels * Salmon": "Sezgi, duygusal derinlik, bağlılık.",
  "Knight of Vessels * Eel": "Uyum sağlama, akış, esneklik.",
  "Page of Vessels * Otter": "Neşe, oyun, duygusal açıklık.",
  "Ace of Vessels * The Waters of Life": "Duyguların başlangıcı, yeni ilişkiler.",
  "Two of Vessels * Attraction": "Çekim, ortaklık, uyum.",
  "Three of Vessels * Joy": "Sevinç, kutlama, dostluk.",
  "Four of Vessels * Boredom": "Sıkılma, tatminsizlik, durağanlık.",
  "Five of Vessels * Ecstasy": "Coşku, duygusal yoğunluk, aşırılık.",
  "Six of Vessels * Reunion": "Buluşma, geçmişle yüzleşme, nostalji.",
  "Seven of Vessels * Mourning": "Yas, kayıp, duygusal zorluk.",
  "Eight of Vessels * Rebirth": "Yeniden doğuş, değişim, ilerleme.",
  "Nine of Vessels * Generosity": "Cömertlik, paylaşım, bolluk.",
  "Ten of Vessels * Happiness": "Mutluluk, aile, huzur.",
  "King of Vessels * Wolf": "Koruma, liderlik, sadakat.",
  "Queen of Stones * Bear": "Güç, koruyuculuk, annelik.",
  "Knight of Stones * Horse": "Çalışkanlık, azim, ilerleme.",
  "Page of Stones * Lynx": "Gizlilik, gözlem, yeni bilgiler.",
  "Ace of Stones * The Foundation of Life": "Temel, güvenlik, yeni başlangıç.",
  "Two of Stones * Challenge": "Mücadele, denge arayışı, zorluk.",
  "Three of Stones * Creativity": "Yaratıcılık, işbirliği, üretkenlik.",
  "Four of Stones * Protection": "Koruma, savunma, güvenlik.",
  "Five of Stones * Endurance": "Dayanıklılık, sabır, zorluklara göğüs germe.",
  "Six of Stones * Exploitation": "Sömürü, dengesizlik, adaletsizlik.",
  "Seven of Stones * Healing": "Şifa, iyileşme, toparlanma.",
  "Eight of Stones * Skill": "Beceri, ustalık, gelişim.",
  "Nine of Stones * Tradition": "Gelenek, kökler, süreklilik.",
  "Ten of Stones * Home": "Ev, aile, güvenli liman."
};

// Tarot Card Component: uses local /assets/tarot images and provided Turkish meanings
function TarotCardGenerative() {
  const CARDS = React.useMemo(
    () => Object.entries(WILDWOOD_TAROT_TR).map(([title, meaning]) => {
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

  // Responsive: stack cards vertically on mobile, shrink card size
  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 600;
  const cardContainerStyle = isMobile
    ? { flexDirection: 'column', gap: 12, alignItems: 'center', width: '100%' }
    : { flexDirection: 'row', gap: 18, justifyContent: 'center', width: '100%' };
  const cardStyle = isMobile
    ? { minWidth: 0, width: 120, maxWidth: '90vw', margin: '0 auto', alignItems: 'center' }
    : { minWidth: 180, alignItems: 'center' };
  const imgStyle = isMobile
    ? { width: 90, height: 140, objectFit: 'cover', borderRadius: 8, marginBottom: 8, boxShadow: '0 2px 8px #0007', transform: undefined, transition: 'transform 0.3s' }
    : { width: 120, height: 186, objectFit: 'cover', borderRadius: 8, marginBottom: 8, boxShadow: '0 2px 8px #0007', transform: undefined, transition: 'transform 0.3s' };

  if (loadingCard) return (
    <div style={{border:'2px solid #ffd700', borderRadius:16, padding:16, width:'100%', background:'#222', color:'#ffd700', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', margin:'1rem auto', boxSizing:'border-box'}}>
      <div>Kartlar hazırlanıyor... 🔮</div>
    </div>
  );

  return (
    <div style={{border:'2px solid #ffd700', borderRadius:16, padding:16, width:'100%', background:'#222', color:'#ffd700', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', margin:'1rem auto', boxSizing:'border-box'}}>
      <div style={{display:'flex', ...cardContainerStyle, marginBottom:12}}>
        {cards.length === 0 ? (
          <div style={{color:'#888', fontSize:16, textAlign:'center', minWidth: isMobile ? 0 : 180}}>Henüz kart çekilmedi.</div>
        ) : cards.map((card, i) => (
          <div key={i} style={{display:'flex', flexDirection:'column', ...cardStyle}}>
            <div style={{fontWeight:'bold', marginBottom:6, fontSize:17, color:'#ffd700', textAlign:'center'}}>{card.title}</div>
            <img src={`/assets/tarot/${card.file}`} alt={card.title} style={{...imgStyle, transform: card.reversed ? 'rotate(180deg)' : 'none'}} />
            <div style={{marginTop:4, color:'#fff', fontSize:14, textAlign:'center'}}>
              <b>{card.reversed ? 'Ters Anlam:' : 'Anlam:'}</b><br/>
              {typeof card.meaning === 'object' ? (card.reversed ? (card.meaning.reversed || card.meaning.upright) : card.meaning.upright) : card.meaning}
            </div>
          </div>
        ))}
      </div>
      <button onClick={handleDraw} style={{marginTop:12, padding:'10px 28px', borderRadius:8, background:'#ffd700', color:'#181825', fontWeight:'bold', border:'none', fontSize:18, width: isMobile ? '100%' : undefined}}>
        {cards.length === 0 ? '3 Kart Çek 🔮' : 'Tekrar Çek 🔮'}
      </button>
    </div>
  );
}

// --- Ayrı Tarot Grid Bileşeni ---
function TarotGrid({ trigger }) {
  React.useEffect(() => {
    if (trigger > 0) {
      const drawButton = document.querySelector('button[onClick]');
      if (drawButton) drawButton.click();
    }
  }, [trigger]);

  return (
    <div style={{display:'flex', justifyContent:'center', alignItems:'flex-start', margin:'2rem 0'}}>
      <div style={{width:'100%'}}>
        <TarotCardGenerative />
      </div>
    </div>
  );
}

// --- Premium: Yorum kutusu kopyala, paylaş ve PDF olarak indir butonları ---
function ResultBox({ result, shareUrl }) {
  const [copied, setCopied] = React.useState(false);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result);
      setCopied(true);
      setTimeout(()=>setCopied(false), 1200);
    } catch {}
  };
  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({ text: result });
      } catch {}
    } else {
      handleCopy();
    }
  };
  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 600;
  if (!result) return null;
  if (hasForbiddenWords(result)) {
    return <div style={{background:'#181825', borderRadius:12, padding: isMobile ? 10 : 16, color:'#f87171', marginTop:16, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word', fontSize: isMobile ? 14 : 16}}>⚠️ Yanıt beklenenden farklı, İngilizce veya hatalı terimler içeriyor. Lütfen tekrar deneyin.</div>;
  }
  if (isEnglishOrMixed(result)) {
    return <div style={{background:'#181825', borderRadius:12, padding: isMobile ? 10 : 16, color:'#f87171', marginTop:16, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word', fontSize: isMobile ? 14 : 16}}>⚠️ Yanıt beklenenden farklı dilde geldi. Lütfen daha açık bir soru sorun veya tekrar deneyin.</div>;
  }
  return (
    <div style={{background:'#181825', borderRadius:12, padding: isMobile ? 10 : 16, color:'#fff', whiteSpace:'pre-line', marginTop:16, position:'relative', width:'100%', boxSizing:'border-box', overflowWrap:'break-word', fontSize: isMobile ? 14 : 16}}>
      <div style={{display:'flex', flexDirection:'row', gap:12, position:'absolute', top:10, right:16, zIndex:2}}>
        <button onClick={handleCopy} title="Kopyala" style={{background:'none', border:'none', color:'#a78bfa', fontSize:18, cursor:'pointer', padding:4}}>
          {copied ? '✔️' : '📋'}
        </button>
        <button onClick={handleShare} title="Paylaş" style={{background:'none', border:'none', color:'#38bdf8', fontSize:18, cursor:'pointer', padding:4}}>
          🔗
        </button>
        {shareUrl && (
          <button onClick={()=>{navigator.clipboard.writeText(shareUrl);}} title="Paylaşılabilir linki kopyala" style={{background:'none', border:'none', color:'#34d399', fontSize:18, cursor:'pointer', padding:4}}>
            🔗 Link
          </button>
        )}
      </div>
      <div style={{paddingTop: isMobile ? 20 : 32}}>{result}</div>
      {shareUrl && <div style={{fontSize:12, color:'#34d399', marginTop:12, wordBreak:'break-all'}}>Paylaşılabilir link: <a href={shareUrl} target="_blank" rel="noopener noreferrer" style={{color:'#34d399', textDecoration:'underline'}}>{shareUrl}</a></div>}
    </div>
  );
}

// --- Main App Component ---
function App() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showTarot, setShowTarot] = useState(false);
  const [birth, setBirth] = useState({
    date: formatDateForInput(new Date(1990,0,1,12,0)),
    lat: '',
    lon: '',
    city: '',
    country: ''
  });
  const [planetPositions, setPlanetPositions] = useState(null);
  const [citySearchLoading, setCitySearchLoading] = useState(false);
  const [partnerCitySearchLoading, setPartnerCitySearchLoading] = useState(false);
  const [userInfo, setUserInfo] = useState({ name: '', gender: '' });
  const [shareUrl, setShareUrl] = useState('');
  const [transitResult, setTransitResult] = useState('');
  const [sinastriResult, setSinastriResult] = useState('');
  const [ttsActive, setTtsActive] = useState(false);
  const [qaInput, setQaInput] = useState('');
  const [qaResult, setQaResult] = useState('');
  const [partner, setPartner] = useState({ date: '', lat: '', lon: '', city: '', country: '' });
  const [partnerPositions, setPartnerPositions] = useState(null);
  const [horaryInput, setHoraryInput] = useState('');
  const [horaryResult, setHoraryResult] = useState('');
  const [horaryLocation, setHoraryLocation] = useState({ city: '', country: '', lat: '', lon: '' });
  const [sinastriLoading, setSinastriLoading] = useState(false);
  // Sesli Oku: Oynat/Durdur
  const [speechState, setSpeechState] = React.useState('idle'); // 'idle' | 'playing' | 'paused'
  const [speechUtter, setSpeechUtter] = React.useState(null);
  // Scroll/odak için ref'ler
  const transitRef = useRef(null);
  const sinastriRef = useRef(null);
  const tarotSectionRef = React.useRef(null);

  const handleBirthChange = e => {
    const { name, value } = e.target;
    setBirth(b => ({ ...b, [name]: value }));
  };

  const handleUserInfoChange = e => {
    const { name, value } = e.target;
    setUserInfo(u => ({ ...u, [name]: value }));
  };

  const handleCityBlur = async () => {
    if (birth.city) {
      setCitySearchLoading(true);
      const coords = await fetchCoordsFromCity(birth.city, birth.country);
      setCitySearchLoading(false);
      if (coords) {
        setBirth(b => ({ ...b, lat: coords.lat, lon: coords.lon }));
        setError('');
      } else {
        setError('Şehir bulunamadı. Lütfen elle koordinat girin.');
      }
    }
  };

  const handlePartnerCityBlur = async () => {
    if (partner.city) {
      setCitySearchLoading(true);
      const coords = await fetchCoordsFromCity(partner.city, partner.country);
      setCitySearchLoading(false);
      if (coords) {
        lat = coords.lat;
        lon = coords.lon;
      }
    }
    if (!date || !lat || !lon) return; // Hala eksikse hesaplama
    const dateObj = new Date(date);
    if (isNaN(parseFloat(lat)) || isNaN(parseFloat(lon))) return;
    const pos = await getPlanetPositions({ date: dateObj, latitude: parseFloat(lat), longitude: parseFloat(lon) });
    setPartnerPositions(pos);
    setPartner(p => ({ ...p, lat, lon })); // Otomatik doldurulanları da inputa yaz
  };

  const handleCalcPlanets = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult('');
    setPlanetPositions(null);
    try {
      // Girdi kontrolleri
      if (!birth.date || !birth.lat || !birth.lon) throw new Error('Tüm alanları eksiksiz doldurun.');
      const dateObj = new Date(birth.date);
      const lat = parseFloat(birth.lat);
      const lon = parseFloat(birth.lon);
      if (isNaN(lat) || isNaN(lon)) throw new Error('Geçerli koordinat girin.');
      let positions;
      const [dateStr, timeStr] = birth.date.split('T');
      try {
        const res = await fetch(`/api/chart?date=${dateStr}&time=${timeStr}&lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'API hatası');
        // map server data
        positions = {};
        data.planets.forEach(p => {
          const signIndex = Math.floor(p.lon / 30);
          const degree = p.lon % 30;
          positions[p.name] = { sign: p.sign, signIndex, degree };
        });
      } catch (apiErr) {
        // Fallback to local astronomia calculation
        console.warn('API chart fetch failed, using local calculation:', apiErr);
        positions = await getPlanetPositions({ date: dateObj, latitude: lat, longitude: lon });
      }
      setPlanetPositions(positions);
      const planetStr = Object.entries(positions).map(([p, pos]) => `${PLANET_TR[p]}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ');
      const prompt = `Aşağıdaki doğum haritası bilgilerine göre, kullanıcının güçlü ve zayıf yönlerini, kariyer ve kişisel tavsiyelerini, sade, akıcı ve profesyonel Türkçe ile özetle. ${TURKISH_FORCE}\n\nDoğum tarihi: ${birth.date}\nŞehir: ${birth.city || '-'}\nÜlke: ${birth.country || '-'}\nEnlem: ${lat}, Boylam: ${lon}\nGezegenler: ${planetStr}`;
      const resAI = await ensureTurkishAIResponse(prompt);
      setResult(resAI);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  const handlePartnerChange = e => {
    const { name, value } = e.target;
    setPartner(p => ({ ...p, [name]: value }));
  };

  const handlePartnerCalc = async () => {
    // Eğer enlem ve boylam girilmişse onları kullan, yoksa şehir/ülke ile otomatik al
    let lat = partner.lat;
    let lon = partner.lon;
    let date = partner.date;
    // Eğer enlem/boylam boşsa şehir/ülke ile doldur
    if ((!lat || !lon) && partner.city) {
      const coords = await fetchCoordsFromCity(partner.city, partner.country);
      if (coords) {
        lat = coords.lat;
        lon = coords.lon;
      }
    }
    if (!date || !lat || !lon) return; // Hala eksikse hesaplama
    const dateObj = new Date(date);
    if (isNaN(parseFloat(lat)) || isNaN(parseFloat(lon))) return;
    const pos = await getPlanetPositions({ date: dateObj, latitude: parseFloat(lat), longitude: parseFloat(lon) });
    setPartnerPositions(pos);
    setPartner(p => ({ ...p, lat, lon })); // Otomatik doldurulanları da inputa yaz
  };

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    const lc = input.trim().toLowerCase();
    // Only trigger tarot draw UI for explicit draw commands
    if (lc === 'tarot kartı' || lc.includes('kart çek')) {
      setShowTarot(true);
      return;
    }
    setLoading(true);
    setError('');
    setResult('');
    const prompt = `Kullanıcıdan gelen soru veya istek: ${input}\n${TURKISH_FORCE}`;
    const res = await ensureTurkishAIResponse(prompt);
    setResult(res);
    setLoading(false);
  }, [input, setShowTarot]);

  const handleTransit = async () => {
    if (!planetPositions) return;
    setLoading(true);
    setTransitResult('');
    // Bugünkü gerçek gezegen konumlarını da hesapla
    const today = new Date();
    const todayStr = today.toLocaleDateString('tr-TR', { year: 'numeric', month: 'long', day: 'numeric' }) + ' ' + today.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    const transitPositions = await getCurrentTransitPositions();
    const natalStr = Object.entries(planetPositions).map(([p, pos]) => `${PLANET_TR[p]}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ');
    const transitStr = Object.entries(transitPositions).map(([p, pos]) => `${PLANET_TR[p]}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ');
    const prompt = `Aşağıda verilen doğum haritası gezegen konumları ve bugünkü gökyüzü (transit) gezegen konumlarına göre, transit etkilerini detaylı, profesyonel ve akıcı Türkçe ile açıkla. ${TURKISH_FORCE}\n\nDoğum haritası gezegenleri: ${natalStr}\nBugünkü transit gezegenler: ${transitStr}\nBugünkü tarih: ${todayStr}`;
    const res = await ensureTurkishAIResponse(prompt);
    setTransitResult(res);
    // Clear result if empty response
    if (!res) setTransitResult('Güncel transit analizi alınamadı. Lütfen tekrar deneyin.');
    setLoading(false);
    // Sonuç gridine scroll
    setTimeout(() => {
      if (transitRef.current) {
        transitRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 300);
  };

  async function handleSinastri() {
    if (!planetPositions || !partnerPositions) return;
    setSinastriLoading(true);
    setSinastriResult('');
    const prompt = `Aşağıda verilen iki kişinin doğum haritası gezegen konumlarına göre, sinastri (ilişki uyumu) analizini detaylı, profesyonel ve akıcı TÜRKÇE ile açıkla. ${TURKISH_FORCE}\n\nKişi 1 gezegenleri: ${Object.entries(planetPositions).map(([p, pos]) => `${PLANET_TR[p] || p}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ')}\nKişi 2 gezegenleri: ${Object.entries(partnerPositions).map(([p, pos]) => `${PLANET_TR[p] || p}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ')}\n`;
    const res = await ensureTurkishAIResponse(prompt);
    setSinastriResult(res);
    setSinastriLoading(false);
    // Sonuç gridine scroll
    setTimeout(() => {
      if (sinastriRef.current) {
        sinastriRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 300);
  }

  const handleTTS = (text) => {
    if (!window.speechSynthesis) return;
    if (speechState === 'playing') {
      window.speechSynthesis.cancel();
      setSpeechState('idle');
      return;
    }
    setTtsActive(true);
    const utter = new window.SpeechSynthesisUtterance(text);
    utter.lang = 'tr-TR';
    utter.voice = (window.speechSynthesis.getVoices().find(v=>v.lang==='tr-TR') || null);
    utter.onend = () => { setTtsActive(false); setSpeechState('idle'); };
    setSpeechUtter(utter);
    setSpeechState('playing');
    window.speechSynthesis.speak(utter);
  };

  const handleQA = async (e) => {
    e.preventDefault();
    setLoading(true);
    setQaResult('');
    const prompt = `Aşağıda verilen doğum haritası gezegen konumlarına göre, kullanıcının sorduğu soruya detaylı, profesyonel ve akıcı Türkçe ile cevap ver. ${TURKISH_FORCE}\n\nGezegenler: ${Object.entries(planetPositions).map(([p, pos]) => `${PLANET_TR[p]}: ${pos.sign} (${pos.degree.toFixed(2)})`).join(', ')}\nSoru: ${qaInput}`;
    const res = await ensureTurkishAIResponse(prompt);
    setQaResult(res);
    setLoading(false);
  };

  const handleHorary = async (e) => {
    e.preventDefault();
    setLoading(true);
    setHoraryResult('');
    // Gerçek tarih/saat ve kullanıcının GÜNCEL konumunu al
    const now = new Date();
    const tarihSaat = now.toLocaleString('tr-TR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    const city = horaryLocation.city || '-';
    const country = horaryLocation.country || '-';
    const lat = horaryLocation.lat || '-';
    const lon = horaryLocation.lon || '-';
    const prompt = `Aşağıda verilen soru için, klasik horary (soru astrolojisi) prensiplerine uygun, detaylı ve profesyonel bir Türkçe astroloji yorumu yaz. Doğum haritası veya doğum yeri kullanılmayacak. Yalnızca sorunun sorulduğu anın tarihi, saati ve aşağıdaki güncel konum kullanılacak. Transit/horary mantığıyla yanıtla. ${TURKISH_FORCE}\n\nSoru: ${horaryInput}\nSoru tarihi ve saati: ${tarihSaat}\nŞehir: ${city}\nÜlke: ${country}\nEnlem: ${lat}\nBoylam: ${lon}`;
    const res = await ensureTurkishAIResponse(prompt);
    setHoraryResult(res);
    setLoading(false);
    setTimeout(() => {
      const el = document.getElementById('horary-interpretation-result');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  };

  const handleTarotButton = () => {
    setShowTarot(true);
    setTimeout(() => {
      if (tarotSectionRef.current) {
        tarotSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
    // Eğer kartlar otomatik çekilmiyorsa, TarotCardGenerative'a prop ile tetikleyici gönderilebilir
    if (typeof window !== 'undefined') {
      window.__drawTarotCardTR = (window.__drawTarotCardTR || 0) + 1;
    }
  };

  React.useEffect(() => {
    if (result) {
      // Sadece temel bilgileri encode et, yorumu encode etme
      const data = {
        name: userInfo.name,
        gender: userInfo.gender,
        city: birth.city,
        country: birth.country,
        date: birth.date,
        lat: birth.lat,
        lon: birth.lon
      };
      const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(data))));
      setShareUrl(window.location.origin + window.location.pathname + '?astro=' + encoded);
    } else {
      setShareUrl('');
    }
  // eslint-disable-next-line
  }, [result]);

  return (
    <div style={{width:'100%',maxWidth:'1400px',margin:'2rem auto',background:'#0f172a',borderRadius:24,boxShadow:'0 4px 32px #0002',padding:'2.5vw',color:'#fff',boxSizing:'border-box'}}>
      <h1 style={{fontSize:32,fontWeight:'bold',textAlign:'center',marginBottom:24,letterSpacing:1}}>Astroloji AI Premium</h1>
      <form onSubmit={handleCalcPlanets} style={{display:'flex', flexDirection:'column', gap:14, marginBottom:28, background:'#181825', borderRadius:14, padding:20, boxShadow:'0 2px 12px #0001'}}>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Adınız</label>
            <input type="text" name="name" value={userInfo.name} onChange={handleUserInfoChange} placeholder="Adınız (isteğe bağlı)" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} autoComplete="off" />
          </div>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Cinsiyet</label>
            <select name="gender" value={userInfo.gender} onChange={handleUserInfoChange} style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}}>
              <option value="">Belirtmek istemiyorum</option>
              <option value="Kadın">Kadın</option>
              <option value="Erkek">Erkek</option>
              <option value="Diğer">Diğer</option>
            </select>
          </div>
        </div>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Şehir</label>
            <input type="text" name="city" value={birth.city} onChange={handleBirthChange} onBlur={handleCityBlur} placeholder="İstanbul" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} autoComplete="off" />
          </div>
          <div style={{flex:2, display:'flex', flexDirection:'column', gap:6}}>
            <label>Ülke</label>
            <input type="text" name="country" value={birth.country} onChange={handleBirthChange} placeholder="Türkiye" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} autoComplete="off" />
          </div>
        </div>
        <div style={{display:'flex', flexDirection:'column', gap:6}}>
          <label>Doğum Tarihi & Saat</label>
          <input type="datetime-local" name="date" value={birth.date} onChange={handleBirthChange} style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} required />
        </div>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:1, display:'flex', flexDirection:'column', gap:6}}>
            <label>Enlem (lat)</label>
            <input type="number" step="0.0001" name="lat" value={birth.lat} onChange={handleBirthChange} placeholder="41.0082" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} required />
          </div>
          <div style={{flex:1, display:'flex', flexDirection:'column', gap:6}}>
            <label>Boylam (lon)</label>
            <input type="number" step="0.0001" name="lon" value={birth.lon} onChange={handleBirthChange} placeholder="28.9784" style={{padding:8, borderRadius:6, border:'1px solid #a78bfa', fontSize:15}} required />
          </div>
        </div>
        {citySearchLoading && <div style={{color:'#a78bfa', fontSize:13}}>Şehir aranıyor...</div>}
        <button type="submit" style={{padding:'12px 0', borderRadius:9, background:'#a78bfa', color:'#181825', fontWeight:'bold', border:'none', fontSize:17, marginTop:6, boxShadow:'0 1px 4px #a78bfa33'}} disabled={loading}>
          {loading ? 'Hesaplanıyor...' : 'Doğum Haritası Yorumu Al'}
        </button>
      </form>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 0 }}>
        <textarea
          value={input}
          onChange={e=>setInput(e.target.value)}
          placeholder="Örnekler: 'Bugün bana ne tavsiye edersin?', 'Aşk hayatım nasıl olacak?', 'Bir tarot kartı çek', 'El falı yorumu al', 'Kariyerimle ilgili ne öngörüyorsun?'"
          rows={3}
          style={{ padding: 12, borderRadius: 8, border: '1px solid #a78bfa', fontSize: 16, resize: 'vertical' }}
        />
        <button type="submit" style={{ padding: '10px 0', borderRadius: 8, background: '#a78bfa', color: '#181825', fontWeight: 'bold', border: 'none', fontSize: 16, marginBottom: 0 }} disabled={loading || !input}>
          {loading ? 'Yorum alınıyor...' : 'Yorum Al'}
        </button>
      </form>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16, margin: '18px 0 24px 0' }}>
        <button onClick={handleTarotButton} style={{ padding: '8px 16px', borderRadius: 8, background: '#ffd700', color: '#181825', fontWeight: 'bold', border: 'none' }}>Tarot Kartı</button>
        <button onClick={handleTransit} style={{ padding: '8px 16px', borderRadius: 8, background: '#38bdf8', color: '#181825', fontWeight: 'bold', border: 'none' }} disabled={!planetPositions}>Transit Analizi</button>
      </div>
      {/* Gezegen tablosu: yalnızca pozisyonlar doluysa göster */}
      {planetPositions && Object.keys(planetPositions).length > 0 && <PlanetTable positions={planetPositions} />}
      {error && !result && <div style={{color:'#f87171', marginBottom:16}}>{error}</div>}
      {result && <ResultBox result={result} shareUrl={shareUrl} containerStyle={{width:'100%',boxSizing:'border-box',overflowWrap:'break-word'}} />}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 24, marginBottom: 32 }}>
        <div style={{ minWidth: 320, flex: 1, maxWidth: 420, order: 1 }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, color: '#38bdf8', marginBottom: 8 }}>Sinastri</h2>
          <form onSubmit={async e => {
            e.preventDefault();
            setSinastriLoading(true);
            setSinastriResult('');
            const prompt = `Aşağıda verilen iki kişinin doğum haritası bilgilerine göre, detaylı ve profesyonel bir sinastri (ilişki uyumu) yorumu yaz.\n\nKullanıcı 1: ${JSON.stringify(birth)}\nKullanıcı 2: ${JSON.stringify(partner)}`;
            const res = await ensureTurkishAIResponse(prompt);
            setSinastriResult(res);
            setSinastriLoading(false);
          }} style={{ display: 'flex', flexDirection: 'column', gap: 8, background: '#181825', borderRadius: 10, padding: 14, marginBottom: 8 }}>
            <input type="text" placeholder="Partner adı (isteğe bağlı)" value={partner.name || ''} name="name" onChange={e => setPartner(p => ({ ...p, name: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="datetime-local" placeholder="Partner doğum tarihi & saati" value={partner.date ? `${partner.date}${partner.time ? 'T'+partner.time : ''}` : ''}
              name="date"
              onChange={e => {
                let v = e.target.value;
                let [date, time] = v.split('T');
                setPartner(p => ({ ...p, date, time: time || '' }));
              }}
              style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }}
            />
            <input type="text" placeholder="Partner şehir" value={partner.city} name="city" onChange={e => setPartner(p => ({ ...p, city: e.target.value }))} onBlur={handlePartnerCityBlur} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            {partnerCitySearchLoading && <div style={{color:'#a78bfa', fontSize:13}}>Şehir aranıyor...</div>}
            <input type="text" placeholder="Partner ülke" value={partner.country} name="country" onChange={e => setPartner(p => ({ ...p, country: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Partner enlem" value={partner.lat} name="lat" onChange={e => setPartner(p => ({ ...p, lat: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Partner boylam" value={partner.lon} name="lon" onChange={e => setPartner(p => ({ ...p, lon: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <button type="submit" style={{ padding: '8px 0', borderRadius: 7, background: '#38bdf8', color: '#181825', fontWeight: 'bold', border: 'none', fontSize: 16, marginTop: 4 }} disabled={sinastriLoading}>{sinastriLoading ? 'Hesaplanıyor...' : 'Sinastri Yorumu Al'}</button>
          </form>
          {sinastriResult && <div style={{ background: '#23234a', borderRadius: 8, padding: 12, color: '#fff', whiteSpace: 'pre-line', marginTop: 8 }}>{sinastriResult}</div>}
        </div>
        <div style={{ minWidth: 320, flex: 1, maxWidth: 420, order: 3 }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, color: '#a78bfa', marginBottom: 8 }}>Soru Astrolojisi (Horary)</h2>
          <form onSubmit={handleHorary} style={{ display: 'flex', flexDirection: 'column', gap: 8, background: '#181825', borderRadius: 10, padding: 14, marginBottom: 8 }}>
            <input type="text" placeholder="Sorunuzu yazın (Türkçe)" value={horaryInput} onChange={e => setHoraryInput(e.target.value)} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="text" placeholder="Güncel şehir (soru için)" value={horaryLocation.city} onChange={async e => {
              const city = e.target.value;
              setHoraryLocation(l => ({ ...l, city }));
              if (city && horaryLocation.country) {
                const coords = await fetchCoordsFromCity(city, horaryLocation.country);
                if (coords) setHoraryLocation(l => ({ ...l, lat: coords.lat, lon: coords.lon }));
              }
            }} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="text" placeholder="Güncel ülke (soru için)" value={horaryLocation.country} onChange={async e => {
              const country = e.target.value;
              setHoraryLocation(l => ({ ...l, country }));
              if (horaryLocation.city && country) {
                const coords = await fetchCoordsFromCity(horaryLocation.city, country);
                if (coords) setHoraryLocation(l => ({ ...l, lat: coords.lat, lon: coords.lon }));
              }
            }} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Güncel enlem (soru için)" value={horaryLocation.lat} onChange={e => setHoraryLocation(l => ({ ...l, lat: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <input type="number" step="0.0001" placeholder="Güncel boylam (soru için)" value={horaryLocation.lon} onChange={e => setHoraryLocation(l => ({ ...l, lon: e.target.value }))} style={{ padding: 8, borderRadius: 6, border:'1px solid #a78bfa', fontSize: 15 }} />
            <button type="submit" style={{ padding: '8px 0', borderRadius: 7, background: '#a78bfa', color: '#181825', fontWeight: 'bold', border: 'none', fontSize: 16, marginTop: 4 }} disabled={loading}>{loading ? 'Hesaplanıyor...' : 'Horary Yorumu Al'}</button>
          </form>
          {horaryResult && (
            <div id="horary-interpretation-result" style={{ background: '#0f172a', borderRadius: 10, padding: 12, color: '#38bdf8', marginTop: 10, whiteSpace: 'pre-line', width: '100%', boxSizing: 'border-box', overflowWrap: 'break-word' }}>
              <b>Horary Yorumu:</b><br />{horaryResult}
            </div>
          )}
        </div>
      </div>
      <div ref={tarotSectionRef} style={{ width: '100%', maxWidth: 420, margin: '0 auto 32px auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, color: '#ffd700', marginBottom: 8, textAlign: 'center' }}>Tarot</h2>
        <TarotGrid trigger={typeof window !== 'undefined' ? window.__drawTarotCardTR : 0} />
      </div>
      {planetPositions && Object.keys(planetPositions).length > 0 && <ChartWheelV2 positions={planetPositions} />}
      {transitResult && !isEnglishOrMixed(transitResult) && (
        <div ref={transitRef} style={{position:'relative',marginTop:16,width:'100%',boxSizing:'border-box',overflowWrap:'break-word'}}>
          <div style={{background:'#0f172a',borderRadius:10,padding:12,color:'#38bdf8',whiteSpace:'pre-line',width:'100%',boxSizing:'border-box',overflowWrap:'break-word'}}>
            <b>Transit Yorumu:</b><br/>{transitResult}
          </div>
        </div>
      )}
      {transitResult && isEnglishOrMixed(transitResult) && (
        <div ref={transitRef} style={{background:'#0f172a', borderRadius:10, padding:12, color:'#f87171', marginTop:16, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>
          ⚠️ AI yanıtı Türkçe değil veya karışık dilde geldi. Lütfen tekrar deneyin.
        </div>
      )}
    </div>
  );
}

export default App;
