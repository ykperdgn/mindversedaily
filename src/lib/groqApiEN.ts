// English Groq API proxy for browser fetch
export async function getGroqInterpretationEN(prompt: string): Promise<string> {
  const apiKey = import.meta.env.PUBLIC_GROQ_API_KEY;
  if (!apiKey) throw new Error('GROQ API key is not defined.');
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
        { role: 'system', content: 'You are a professional astrologer. Your interpretation must be detailed, original, and in English.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.8
    })
  });
  if (!res.ok) throw new Error('Groq API error: ' + res.statusText);
  const data = await res.json();
  return data.choices?.[0]?.message?.content || 'No interpretation received.';
}
