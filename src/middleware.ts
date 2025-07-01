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
  }

  // Sadece Vercel production'da çalışsın
  const country = req.headers.get("x-vercel-ip-country") || "US";

  // Language prefix'leri ve static dosyaları atla
  const skipPrefixes = ["/tr/", "/en/", "/tr", "/en"];
  const skipExts = [".png", ".jpg", ".jpeg", ".svg", ".ico", ".css", ".js", ".json"];
  if (
    skipPrefixes.some(p => pathname.startsWith(p)) ||
    skipExts.some(ext => pathname.endsWith(ext))
  ) {
    return next();
  }

  // Sadece root path (/) için redirect yap
  if (pathname === "/") {
    const langPrefix = country === "TR" ? "/tr" : "/en";
    const redirectTo = new URL(`${langPrefix}${pathname}${search}`, origin).toString();
    return Response.redirect(redirectTo, 302);
  }

  return next();
});
