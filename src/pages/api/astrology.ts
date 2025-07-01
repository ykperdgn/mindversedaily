// Astrology API route for horoscope generation
// Astroloji bot ile entegre horoskop üretimi

import type { APIRoute } from 'astro';

// Server-side rendering için prerender'ı false yap
export const prerender = false;

// Astroloji bot'u çağırmak için Python script çalıştırma
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

interface HoroscopeRequest {
  sign: string;
  type: 'daily' | 'weekly' | 'monthly';
  language?: string;
}

interface CompatibilityRequest {
  sign1: string;
  sign2: string;
  language?: string;
}

const zodiacSigns = [
  'koc', 'boga', 'ikizler', 'yengec', 'aslan', 'basak',
  'terazi', 'akrep', 'yay', 'oglak', 'kova', 'balik'
];

export const GET: APIRoute = async ({ url }) => {
  const action = url.searchParams.get('action');

  try {
    switch (action) {
      case 'signs':
        return new Response(JSON.stringify({
          success: true,
          signs: zodiacSigns,
          zodiac_info: {
            'koc': { name: 'Koç', emoji: '♈', element: 'Ateş' },
            'boga': { name: 'Boğa', emoji: '♉', element: 'Toprak' },
            'ikizler': { name: 'İkizler', emoji: '♊', element: 'Hava' },
            'yengec': { name: 'Yengeç', emoji: '♋', element: 'Su' },
            'aslan': { name: 'Aslan', emoji: '♌', element: 'Ateş' },
            'basak': { name: 'Başak', emoji: '♍', element: 'Toprak' },
            'terazi': { name: 'Terazi', emoji: '♎', element: 'Hava' },
            'akrep': { name: 'Akrep', emoji: '♏', element: 'Su' },
            'yay': { name: 'Yay', emoji: '♐', element: 'Ateş' },
            'oglak': { name: 'Oğlak', emoji: '♑', element: 'Toprak' },
            'kova': { name: 'Kova', emoji: '♒', element: 'Hava' },
            'balik': { name: 'Balık', emoji: '♓', element: 'Su' }
          }
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });

      case 'cosmic-forecast':
        const period = url.searchParams.get('period') || 'week';
        const forecastResult = await generateCosmicForecast(period);
        return new Response(JSON.stringify(forecastResult), {
          status: forecastResult.success ? 200 : 500,
          headers: { 'Content-Type': 'application/json' }
        });

      default:
        return new Response(JSON.stringify({
          error: 'Geçersiz action parametresi'
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
    }
  } catch (error) {
    return new Response(JSON.stringify({
      error: 'Internal server error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const action = body.action;

    switch (action) {
      case 'generate-horoscope':
        const horoscopeReq = body as HoroscopeRequest & { action: string };
        const horoscopeResult = await generateHoroscope(
          horoscopeReq.sign,
          horoscopeReq.type,
          horoscopeReq.language || 'tr'
        );
        return new Response(JSON.stringify(horoscopeResult), {
          status: horoscopeResult.success ? 200 : 500,
          headers: { 'Content-Type': 'application/json' }
        });

      case 'compatibility-analysis':
        const compatReq = body as CompatibilityRequest & { action: string };
        const compatResult = await generateCompatibility(
          compatReq.sign1,
          compatReq.sign2,
          compatReq.language || 'tr'
        );
        return new Response(JSON.stringify(compatResult), {
          status: compatResult.success ? 200 : 500,
          headers: { 'Content-Type': 'application/json' }
        });

      case 'birth-chart':
        const birthInfo = body.birthInfo;
        const chartResult = await generateBirthChart(birthInfo);
        return new Response(JSON.stringify(chartResult), {
          status: chartResult.success ? 200 : 500,
          headers: { 'Content-Type': 'application/json' }
        });

      default:
        return new Response(JSON.stringify({
          error: 'Geçersiz action'
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
    }
  } catch (error) {
    return new Response(JSON.stringify({
      error: 'Request parsing error'
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

async function generateHoroscope(sign: string, type: string, language: string) {
  try {
    if (!zodiacSigns.includes(sign.toLowerCase())) {
      return { success: false, error: 'Geçersiz burç' };
    }

    const scriptPath = path.join(process.cwd(), 'scripts', 'astrology_bot.py');
    const command = `python "${scriptPath}" --action=horoscope --sign=${sign} --type=${type} --language=${language}`;    console.log('Executing command:', command);
    const { stdout, stderr } = await execAsync(command);

    console.log('Command stdout:', stdout);
    console.log('Command stderr:', stderr);

    if (stderr) {
      console.error('Python script error:', stderr);
      return { success: false, error: 'Horoscope generation failed', details: stderr };
    }

    if (!stdout || stdout.trim() === '') {
      console.error('No output from Python script');
      return { success: false, error: 'No output from horoscope script' };
    }

    try {
      const result = JSON.parse(stdout);
      console.log('Parsed result:', result);
      return { success: true, ...result };
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      console.error('Raw stdout:', stdout);
      return { success: true, content: stdout };
    }} catch (error) {
    console.error('Horoscope generation error:', error);
    return { success: false, error: 'Internal error', details: String(error) };
  }
}

async function generateCompatibility(sign1: string, sign2: string, language: string) {
  try {
    if (!zodiacSigns.includes(sign1.toLowerCase()) || !zodiacSigns.includes(sign2.toLowerCase())) {
      return { success: false, error: 'Geçersiz burç' };
    }

    const scriptPath = path.join(process.cwd(), 'scripts', 'astrology_bot.py');
    const command = `python "${scriptPath}" --action=compatibility --sign1=${sign1} --sign2=${sign2} --language=${language}`;

    const { stdout, stderr } = await execAsync(command);

    if (stderr) {
      console.error('Python script error:', stderr);
      return { success: false, error: 'Compatibility analysis failed' };
    }

    try {
      const result = JSON.parse(stdout);
      return { success: true, ...result };
    } catch (parseError) {
      return { success: true, content: stdout };
    }
  } catch (error) {
    console.error('Compatibility analysis error:', error);
    return { success: false, error: 'Internal error' };
  }
}

async function generateBirthChart(birthInfo: any) {
  try {
    const scriptPath = path.join(process.cwd(), 'scripts', 'astrology_bot.py');
    const command = `python "${scriptPath}" --action=birth-chart --birth-info='${JSON.stringify(birthInfo)}'`;

    const { stdout, stderr } = await execAsync(command);

    if (stderr) {
      console.error('Python script error:', stderr);
      return { success: false, error: 'Birth chart analysis failed' };
    }

    try {
      const result = JSON.parse(stdout);
      return { success: true, ...result };
    } catch (parseError) {
      return { success: true, content: stdout };
    }
  } catch (error) {
    console.error('Birth chart analysis error:', error);
    return { success: false, error: 'Internal error' };
  }
}

async function generateCosmicForecast(period: string) {
  try {
    const scriptPath = path.join(process.cwd(), 'scripts', 'astrology_bot.py');
    const command = `python "${scriptPath}" --action=cosmic-forecast --period=${period}`;

    console.log('Executing cosmic forecast command:', command);
    const { stdout, stderr } = await execAsync(command);

    if (stderr) {
      console.error('Python script error:', stderr);
      return { success: false, error: 'Cosmic forecast failed', details: stderr };
    }

    try {
      const result = JSON.parse(stdout);
      return { success: true, ...result };
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      return { success: true, content: stdout };
    }
  } catch (error) {
    console.error('Cosmic forecast error:', error);
    return { success: false, error: 'Internal error', details: String(error) };
  }
}

// OPTIONS for CORS
export const OPTIONS: APIRoute = async () => {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    }
  });
};
