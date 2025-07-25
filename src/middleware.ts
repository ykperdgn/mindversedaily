import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const req = context.request;
  const url = new URL(req.url);
  const { pathname, search, origin } = url;

  // Development ortamında veya localhost'ta middleware'i devre dışı bırak
  if (
    import.meta.env.DEV ||
    origin.includes('localhost') ||
    origin.includes('127.0.0.1') ||
    origin.includes('192.168.') ||
    !process.env.VERCEL
  ) {
    return next();
  }  // Static dosyaları ve API rotalarını atla
  const skipPrefixes = ["/tr/", "/en/", "/tr", "/en", "/blog/", "/about", "/api/", "/_astro/"];
  const skipExts = [".png", ".jpg", ".jpeg", ".svg", ".ico", ".css", ".js", ".json", ".txt", ".xml", ".woff", ".woff2"];
  if (
    skipPrefixes.some(p => pathname.startsWith(p)) ||
    skipExts.some(ext => pathname.endsWith(ext)) ||
    pathname.startsWith("/_astro/") ||
    pathname.includes("/assets/")
  ) {
    return next();
  }

  // SEO bot'ları ve crawler'ları tespit et - bunlar için redirect yapma
  const userAgent = req.headers.get("user-agent") || "";
  const isBot = /bot|crawler|spider|crawling|googlebot|bingbot|facebookexternalhit|twitterbot|whatsapp|telegram/i.test(userAgent);

  if (isBot) {
    return next(); // Bot'lar için redirect yapma, direkt içeriği sun
  }

  // Sadece root path (/) için dil yönlendirme mantığı
  if (pathname === "/") {
    // Vercel IP country ve accept-language headers'ı al
    const country = req.headers.get("x-vercel-ip-country") || "TR";
    const acceptLanguage = req.headers.get("accept-language") || "";

    // Dil tercihi algılama
    const hasEnglish = acceptLanguage.toLowerCase().includes("en");
    const hasTurkish = acceptLanguage.toLowerCase().includes("tr");

    // Türkiye IP'si veya Türkçe tarayıcı dili VARSA => Ana sayfada kal (varsayılan Türkçe)
    if (country === "TR" || hasTurkish) {
      return next(); // Ana sayfada kal, redirect yapma
    }

    // Sadece açıkça İngilizce isteyenler için /en/ sayfasına yönlendir
    if (hasEnglish && !hasTurkish) {
      const redirectTo = new URL(`/en${search}`, origin).toString();
      return Response.redirect(redirectTo, 302);
    }

    // Belirsiz durumlar için ana sayfada kal (Türkçe varsayılan)
    return next();
  }

  return next();
});
