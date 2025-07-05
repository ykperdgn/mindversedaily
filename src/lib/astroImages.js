// Görsel yönetimi: Tarot ve Palmistry SVG'leri (Astro uyumlu, React'siz)
// Her SVG bir string olarak export edilir. Kullanım: innerHTML ile veya doğrudan HTML olarak.

export const tarotCardImages = {
  "The Fool (Joker)": `<div class="tarot-svg-card" title="The Fool"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="2" fill="none" /><path d="M50 10 V 90 M 10 50 H 90" stroke="currentColor" stroke-width="1" stroke-dasharray="4" /></svg></div>`,
  "The Magician (Büyücü)": `<div class="tarot-svg-card" title="The Magician"><svg viewBox="0 0 100 100"><path d="M50 10 L 90 90 H 10 Z" stroke="currentColor" stroke-width="2" fill="none" /><path d="M50 10 V 90" stroke="currentColor" stroke-width="1" /></svg></div>`,
  "The High Priestess (Azize)": `<div class="tarot-svg-card" title="The High Priestess"><svg viewBox="0 0 100 100"><path d="M20 20 H 80 V 80 H 20 Z" stroke="currentColor" stroke-width="2" fill="none" /><circle cx="50" cy="50" r="15" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Empress (İmparatoriçe)": `<div class="tarot-svg-card" title="The Empress"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="30" stroke="currentColor" stroke-width="2" fill="none" /><path d="M50 20 V 80 M 35 35 L 65 65 M 35 65 L 65 35" stroke="currentColor" stroke-width="1.5" /></svg></div>`,
  "The Emperor (İmparator)": `<div class="tarot-svg-card" title="The Emperor"><svg viewBox="0 0 100 100"><rect x="20" y="20" width="60" height="60" stroke="currentColor" stroke-width="2" fill="none" /><rect x="35" y="35" width="30" height="30" stroke="currentColor" stroke-width="1" fill="none" /></svg></div>`,
  "The Hierophant (Aziz)": `<div class="tarot-svg-card" title="The Hierophant"><svg viewBox="0 0 100 100"><path d="M50 10 L 50 90 M 30 30 H 70 M 30 50 H 70 M 30 70 H 70" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Lovers (Aşıklar)": `<div class="tarot-svg-card" title="The Lovers"><svg viewBox="0 0 100 100"><path d="M35 30 C 50 -10, 50 -10, 65 30 C 80 70, 20 70, 35 30 Z" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Chariot (Savaş Arabası)": `<div class="tarot-svg-card" title="The Chariot"><svg viewBox="0 0 100 100"><path d="M20 80 L 50 20 L 80 80 H 20 Z" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "Strength (Güç)": `<div class="tarot-svg-card" title="Strength"><svg viewBox="0 0 100 100"><path d="M30 50 C 30 20, 70 20, 70 50 C 70 80, 30 80, 30 50 Z" stroke="currentColor" stroke-width="2" fill="none" /><path d="M 50 30 L 50 70" stroke="currentColor" stroke-width="2" /></svg></div>`,
  "The Hermit (Ermiş)": `<div class="tarot-svg-card" title="The Hermit"><svg viewBox="0 0 100 100"><path d="M50 20 L 30 80 H 70 Z" stroke="currentColor" stroke-width="2" fill="none" /><circle cx="50" cy="45" r="5" fill="currentColor" /></svg></div>`,
  "Wheel of Fortune (Kader Çarkı)": `<div class="tarot-svg-card" title="Wheel of Fortune"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="35" stroke="currentColor" stroke-width="2" fill="none" /><path d="M50 15 V 85 M 15 50 H 85 M 25.7 25.7 L 74.3 74.3 M 25.7 74.3 L 74.3 25.7" stroke="currentColor" stroke-width="1" /></svg></div>`,
  "Justice (Adalet)": `<div class="tarot-svg-card" title="Justice"><svg viewBox="0 0 100 100"><path d="M10 50 H 90 M 50 10 V 90 M 20 30 L 50 45 L 80 30 M 20 70 L 50 55 L 80 70" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Hanged Man (Asılan Adam)": `<div class="tarot-svg-card" title="The Hanged Man"><svg viewBox="0 0 100 100"><path d="M30 20 H 70 M 50 20 V 50 L 30 80" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "Death (Ölüm)": `<div class="tarot-svg-card" title="Death"><svg viewBox="0 0 100 100"><path d="M20 80 L 80 20 M 20 20 L 80 80" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "Temperance (Denge)": `<div class="tarot-svg-card" title="Temperance"><svg viewBox="0 0 100 100"><path d="M20 30 L 80 70 M 20 70 L 80 30" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Devil (Şeytan)": `<div class="tarot-svg-card" title="The Devil"><svg viewBox="0 0 100 100"><path d="M50 80 L 20 50 L 80 50 Z" stroke="currentColor" stroke-width="2" fill="none" /><circle cx="50" cy="30" r="10" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Tower (Kule)": `<div class="tarot-svg-card" title="The Tower"><svg viewBox="0 0 100 100"><rect x="35" y="20" width="30" height="60" stroke="currentColor" stroke-width="2" fill="none" /><path d="M35 20 L 20 35 M 65 20 L 80 35" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Star (Yıldız)": `<div class="tarot-svg-card" title="The Star"><svg viewBox="0 0 100 100"><path d="M50 10 L 60 40 L 90 40 L 65 60 L 75 90 L 50 70 L 25 90 L 35 60 L 10 40 L 40 40 Z" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The Moon (Ay)": `<div class="tarot-svg-card" title="The Moon"><svg viewBox="0 0 100 100"><path d="M70 20 A 30 30 0 1 0 70 80" stroke="currentColor" stroke-width="2" fill="none" /><path d="M70 20 A 40 40 0 1 0 70 80" stroke="currentColor" stroke-width="1" stroke-dasharray="4" /></svg></div>`,
  "The Sun (Güneş)": `<div class="tarot-svg-card" title="The Sun"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="25" stroke="currentColor" stroke-width="2" fill="none" /><path d="M50 10 V 25 M 50 75 V 90 M 10 50 H 25 M 75 50 H 90 M 21 21 L 32 32 M 68 68 L 79 79 M 21 79 L 32 68 M 68 32 L 79 21" stroke="currentColor" stroke-width="2" /></svg></div>`,
  "Judgement (Yargı)": `<div class="tarot-svg-card" title="Judgement"><svg viewBox="0 0 100 100"><rect x="30" y="40" width="40" height="40" stroke="currentColor" stroke-width="2" fill="none" /><path d="M50 20 V 40" stroke="currentColor" stroke-width="2" fill="none" /></svg></div>`,
  "The World (Dünya)": `<div class="tarot-svg-card" title="The World"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="2" fill="none" /><circle cx="50" cy="50" r="20" stroke="currentColor" stroke-width="1" fill="none" /></svg></div>`
};

export const palmistryImages = {
  heart: {
    name: 'Kalp Çizgisi',
    desc: 'Duygusal dünyanızı, aşk hayatınızı ve ilişkilerinizi temsil eder.',
    img: `<div class="palmistry-svg-line" title="Kalp Çizgisi"><svg viewBox="0 0 100 100"><path d="M 20 80 C 30 40, 70 40, 90 50" stroke="#f472b6" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M 20 80 C 35 60, 60 60, 85 70" stroke="currentColor" stroke-width="1" fill="none" opacity="0.3"/><path d="M 25 75 C 40 85, 60 90, 80 85" stroke="currentColor" stroke-width="1" fill="none" opacity="0.3"/></svg></div>`
  },
  head: {
    name: 'Akıl Çizgisi',
    desc: 'Düşünce yapınızı, zekanızı ve iletişim becerilerinizi gösterir.',
    img: `<div class="palmistry-svg-line" title="Akıl Çizgisi"><svg viewBox="0 0 100 100"><path d="M 20 80 C 30 40, 70 40, 90 50" stroke="currentColor" stroke-width="1" fill="none" opacity="0.3"/><path d="M 20 80 C 35 60, 60 60, 85 70" stroke="#2dd4bf" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M 25 75 C 40 85, 60 90, 80 85" stroke="currentColor" stroke-width="1" fill="none" opacity="0.3"/></svg></div>`
  },
  life: {
    name: 'Hayat Çizgisi',
    desc: 'Fiziksel sağlığınızı, canlılığınızı ve yaşam enerjinizi temsil eder.',
    img: `<div class="palmistry-svg-line" title="Hayat Çizgisi"><svg viewBox="0 0 100 100"><path d="M 20 80 C 30 40, 70 40, 90 50" stroke="currentColor" stroke-width="1" fill="none" opacity="0.3"/><path d="M 20 80 C 35 60, 60 60, 85 70" stroke="currentColor" stroke-width="1" fill="none" opacity="0.3"/><path d="M 25 75 C 40 85, 60 90, 80 85" stroke="#f87171" stroke-width="3" fill="none" stroke-linecap="round"/></svg></div>`
  }
};
