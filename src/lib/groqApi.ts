// Simple Groq API proxy for browser fetch
console.log("PUBLIC_GROQ_API_KEY (build):", import.meta.env.PUBLIC_GROQ_API_KEY);
if (typeof window !== "undefined") {
  console.log("PUBLIC_GROQ_API_KEY (client):", import.meta.env.PUBLIC_GROQ_API_KEY);
}
export async function getGroqInterpretation(prompt: string): Promise<string> {
  const apiKey = import.meta.env.PUBLIC_GROQ_API_KEY;
  if (!apiKey) throw new Error('GROQ API anahtarı tanımlı değil.');
  const url = 'https://api.groq.com/openai/v1/chat/completions';
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama3-70b-8192',
      messages: [
        { role: 'system', content: 'Sen profesyonel bir astrologsun. Yorumun detaylı, özgün ve Türkçe olmalı.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.8
    })
  });
  if (!res.ok) throw new Error('Groq API hatası: ' + res.statusText);
  const data = await res.json();
  return data.choices?.[0]?.message?.content || 'Yorum alınamadı.';
}
