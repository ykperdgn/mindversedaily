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
  "The Wanderer": "Yeni başlangıçlar, özgürlük, bilinmeyene cesaretle adım atmak.",
  "The Shaman": "İrade, güç, potansiyel, içsel kaynakları kullanmak.",
  "The Seer": "Sezgi, içgörü, ruhsal rehberlik, vizyon.",
  "The Green Woman": "Doğurganlık, yaratıcılık, doğayla uyum.",
  "The Green Man": "Büyüme, canlılık, doğayla bütünleşme.",
  "The Ancestor": "Gelenek, kökler, geçmişten gelen rehberlik.",
  "The Forest Lovers": "Aşk, birlik, uyum, ortaklık.",
  "The Archer": "Odaklanma, kararlılık, hedefe yönelmek.",
  "The Stag": "Adalet, sorumluluk, liderlik.",
  "The Hooded Man": "İçsel arayış, yalnızlık, bilgelik.",
  "The Wheel": "Kader, değişim, döngüler.",
  "The Woodward": "Denge, güç, sabır.",
  "The Mirror": "Kendini keşfetme, yansımalar, içsel derinlik.",
  "The Journey": "Dönüşüm, sonlar ve yeni başlangıçlar.",
  "Balance": "Denge, uyum, ölçülülük.",
  "The Guardian": "Korkularla yüzleşme, koruma, sınırlar.",
  "The Blasted Oak": "Ani değişim, beklenmedik olaylar.",
  "The Pole Star": "Umut, rehberlik, ilham.",
  "The Moon on Water": "Bilinçaltı, sezgi, belirsizlik.",
  "The Sun of Life": "Mutluluk, canlılık, başarı.",
  "The Great Bear": "Yeniden doğuş, yargı, uyanış.",
  "The World Tree": "Tamamlanma, bütünlük, döngünün sonu.",
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
      // Extract base name before any ' * ' suffix and use for file name
      const base = title.includes(' * ') ? title.split(' * ')[0] : title;
      const file = base.replace(/\s+/g, '_') + '.png';
      return { title, meaning, file };
    }),
    []
  );
  const [card, setCard] = React.useState(null);
  const [loadingCard, setLoadingCard] = React.useState(false);

  const handleDraw = () => {
    setLoadingCard(true);
    setCard(null);
    setTimeout(() => {
      const randomCard = CARDS[Math.floor(Math.random() * CARDS.length)];
      setCard(randomCard);
      setLoadingCard(false);
    }, 3000); // 3 saniye bekleme
  };

  React.useEffect(() => {
    handleDraw();
  }, []);

  if (loadingCard) return (
    <div style={{border:'2px solid #ffd700', borderRadius:16, padding:16, width:'100%', background:'#222', color:'#ffd700', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', margin:'1rem auto', boxSizing:'border-box'}}>
      <div>Kart hazırlanıyor... 🔮</div>
    </div>
  );
  if (!card) return null;

  return (
    <div style={{border:'2px solid #ffd700', borderRadius:16, padding:16, width:'100%', background:'#222', color:'#ffd700', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', margin:'1rem auto', boxSizing:'border-box'}}>
      <div style={{fontWeight:'bold', marginBottom:8, fontSize:20}}>{card.title}</div>
      <img src={`/assets/tarot/${card.file}`} alt={card.title} style={{width:180, height:280, objectFit:'cover', borderRadius:8, marginBottom:8, boxShadow:'0 2px 8px #0007'}} />
      <div style={{marginTop:14, color:'#fff', fontSize:15, textAlign:'center'}}>
        <b>Anlam:</b><br/>{card.meaning}
      </div>
      <button onClick={handleDraw} style={{marginTop:12, padding:'6px 16px', borderRadius:8, background:'#ffd700', color:'#181825', fontWeight:'bold', border:'none'}}>
        Yeni Kart Çek 🔮
      </button>
    </div>
  );
}

// --- Ayrı Tarot Grid Bileşeni ---
function TarotGrid() {
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
  if (!result) return null;
  if (hasForbiddenWords(result)) {
    return <div style={{background:'#181825', borderRadius:12, padding:16, color:'#f87171', marginTop:16, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>⚠️ Yanıt beklenenden farklı, İngilizce veya hatalı terimler içeriyor. Lütfen tekrar deneyin.</div>;
  }
  if (isEnglishOrMixed(result)) {
    return <div style={{background:'#181825', borderRadius:12, padding:16, color:'#f87171', marginTop:16, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>⚠️ Yanıt beklenenden farklı dilde geldi. Lütfen daha açık bir soru sorun veya tekrar deneyin.</div>;
  }
  return (
    <div style={{background:'#181825', borderRadius:12, padding:16, color:'#fff', whiteSpace:'pre-line', marginTop:16, position:'relative', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>
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
      <div style={{paddingTop:32}}>{result}</div>
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
  const [sinastriLoading, setSinastriLoading] = useState(false);
  // Sesli Oku: Oynat/Durdur
  const [speechState, setSpeechState] = React.useState('idle'); // 'idle' | 'playing' | 'paused'
  const [speechUtter, setSpeechUtter] = React.useState(null);
  // Scroll/odak için ref'ler
  const transitRef = useRef(null);
  const sinastriRef = useRef(null);

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
    const prompt = `Aşağıda verilen soru için, klasik horary (soru astrolojisi) prensiplerine uygun, detaylı ve profesyonel bir Türkçe astroloji yorumu yaz. ${TURKISH_FORCE}\n\nSoru: ${horaryInput}`;
    const res = await ensureTurkishAIResponse(prompt);
    setHoraryResult(res);
    setLoading(false);
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
      {/* Gezegen tablosu: yalnızca pozisyonlar doluysa göster */}
      {planetPositions && Object.keys(planetPositions).length > 0 && <PlanetTable positions={planetPositions} />}
      {error && !result && <div style={{color:'#f87171', marginBottom:16}}>{error}</div>}
      {result && <ResultBox result={result} shareUrl={shareUrl} containerStyle={{width:'100%',boxSizing:'border-box',overflowWrap:'break-word'}} />}
      <form onSubmit={handleSubmit} style={{display:'flex', flexDirection:'column', gap:12, marginBottom:24}}>
        <textarea
          value={input}
          onChange={e=>setInput(e.target.value)}
          placeholder="Örnekler: 'Bugün bana ne tavsiye edersin?', 'Aşk hayatım nasıl olacak?', 'Bir tarot kartı çek', 'El falı yorumu al', 'Kariyerimle ilgili ne öngörüyorsun?'"
          rows={3}
          style={{padding:12, borderRadius:8, border:'1px solid #a78bfa', fontSize:16, resize:'vertical'}}
        />
        <button type="submit" style={{padding:'10px 0', borderRadius:8, background:'#a78bfa', color:'#181825', fontWeight:'bold', border:'none', fontSize:16}} disabled={loading || !input}>
          {loading ? 'Yorum alınıyor...' : 'Yorum Al'}
        </button>
      </form>
      <div style={{display:'flex', justifyContent:'center', gap:16, marginBottom:24}}>
        <button onClick={()=>setShowTarot(v=>!v)} style={{padding:'8px 16px', borderRadius:8, background:'#ffd700', color:'#181825', fontWeight:'bold', border:'none'}}>Tarot Kartı</button>
        <button onClick={handleTransit} style={{padding:'8px 16px', borderRadius:8, background:'#38bdf8', color:'#181825', fontWeight:'bold', border:'none'}} disabled={!planetPositions}>Transit Analizi</button>
      </div>
      {showTarot && <TarotGrid />}
      {planetPositions && (
        <div style={{background:'#23234a', borderRadius:14, padding:16, margin:'1rem 0 1.5rem 0', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>
          <div style={{fontWeight:'bold', color:'#38bdf8', marginBottom:8}}>Soru Astrolojisi (Horary)</div>
          <form onSubmit={handleHorary} style={{display:'flex', gap:8, marginBottom:8}}>
            <input type="text" value={horaryInput} onChange={e=>setHoraryInput(e.target.value)} placeholder="Bir soru yazın... (örn: Bu işte başarılı olur muyum?)" style={{flex:1, padding:8, borderRadius:8, border:'1px solid #38bdf8', fontSize:15}} />
            <button type="submit" style={{padding:'8px 16px', borderRadius:8, background:'#38bdf8', color:'#181825', fontWeight:'bold', border:'none'}} disabled={!horaryInput || loading}>Sor</button>
          </form>
          {horaryResult && !isEnglishOrMixed(horaryResult) && <div style={{background:'#0f172a', borderRadius:10, padding:12, color:'#38bdf8', marginTop:10, whiteSpace:'pre-line', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}><b>Horary Yorumu:</b><br/>{horaryResult}</div>}
          {horaryResult && isEnglishOrMixed(horaryResult) && <div style={{background:'#0f172a', borderRadius:10, padding:12, color:'#f87171', marginTop:10, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>⚠️ AI yanıtı Türkçe değil veya karışık dilde geldi. Lütfen tekrar deneyin veya farklı bir soru sorun.</div>}
        </div>
      )}
      {/* Natal chart only when positions available */}
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
      {planetPositions && (
        <div ref={sinastriRef} style={{background:'#23234a',borderRadius:14,padding:16,margin:'1rem 0 0.5rem 0',width:'100%',boxSizing:'border-box',overflowWrap:'break-word'}}>
          <div style={{fontWeight:'bold', color:'#f472b6', marginBottom:8}}>Partner Bilgileri (Sinastri / İlişki Uyumu):</div>
          <div style={{display:'flex', gap:8, marginBottom:8, flexWrap:'wrap'}}>
            <input type="datetime-local" name="date" value={partner.date} onChange={handlePartnerChange} onBlur={handlePartnerCityBlur} placeholder="Doğum Tarihi & Saat" style={{flex:2, padding:8, borderRadius:6, border:'1px solid #fbbf24', fontSize:15}} />
            <input type="text" name="city" value={partner.city} onChange={handlePartnerChange} placeholder="Şehir" style={{flex:1, padding:8, borderRadius:6, border:'1px solid #fbbf24', fontSize:15}} />
            <input type="text" name="country" value={partner.country} onChange={handlePartnerChange} placeholder="Ülke" style={{flex:1, padding:8, borderRadius:6, border:'1px solid #fbbf24', fontSize:15}} />
            <input type="number" step="0.0001" name="lat" value={partner.lat} onChange={handlePartnerChange} placeholder="Enlem (örn: 39.9334)" style={{flex:1, padding:8, borderRadius:6, border:'1px solid #fbbf24', fontSize:15}} />
            <input type="number" step="0.0001" name="lon" value={partner.lon} onChange={handlePartnerChange} placeholder="Boylam (örn: 32.8597)" style={{flex:1, padding:8, borderRadius:6, border:'1px solid #fbbf24', fontSize:15}} />
          </div>
          <div style={{color:'#fbbf24', fontSize:12, marginBottom:6}}>
            Ankara için örnek: Enlem 39.9334, Boylam 32.8597. Şehir/ülke girince otomatik dolmazsa elle girin.
          </div>
          <button onClick={handlePartnerCalc} style={{padding:'8px 16px', borderRadius:8, background:'#fbbf24', color:'#181825', fontWeight:'bold', border:'none', marginBottom:8}}>Partner Haritasını Hesapla</button>
          {partnerPositions && <div style={{color:'#fbbf24', fontSize:13, marginBottom:4}}>Partner haritası hesaplandı.</div>}
          <button onClick={handleSinastri} style={{padding:'8px 16px', borderRadius:8, background:'#f472b6', color:'#181825', fontWeight:'bold', border:'none', marginTop:8}} disabled={!partnerPositions || sinastriLoading}>{sinastriLoading ? 'Sinastri Analizi Alınıyor...' : 'Sinastri Analizi Al'}</button>
          {!partnerPositions && <div style={{color:'#f87171', fontSize:13, marginTop:8}}>Önce partner bilgilerini eksiksiz girip haritasını hesaplayın.</div>}
          {partnerPositions && sinastriResult && hasForbiddenWords(sinastriResult) && (
            <div style={{background:'#0f172a', borderRadius:10, padding:12, color:'#f87171', marginTop:10, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>⚠️ Yanıt beklenenden farklı veya hatalı terimler içeriyor. Lütfen tekrar deneyin.</div>
          )}
          {partnerPositions && sinastriResult && isEnglishOrMixed(sinastriResult) && (
            <div style={{background:'#0f172a', borderRadius:10, padding:12, color:'#f87171', marginTop:10, fontWeight:'bold', width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>⚠️ AI yanıtı Türkçe değil veya karışık dilde geldi. Lütfen tekrar deneyin veya farklı bir partner bilgisi girin.</div>
          )}
          {partnerPositions && sinastriResult && !hasForbiddenWords(sinastriResult) && !isEnglishOrMixed(sinastriResult) && (
            <div style={{position:'relative', marginTop:10, width:'100%', boxSizing:'border-box', overflowWrap:'break-word'}}>
              <div style={{background:'#0f172a',borderRadius:10,padding:12,color:'#f472b6',whiteSpace:'pre-line',width:'100%',boxSizing:'border-box',overflowWrap:'break-word'}}>
                <b>Sinastri Yorumu:</b><br/>{sinastriResult}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
