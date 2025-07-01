import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  // Vercel veya edge ortamında ülke kodunu header'dan al
  const country = context.request.headers.get("x-vercel-ip-country") || "US";
  const url = new URL(context.request.url);

  // Eğer zaten /tr veya /en ile başlıyorsa yönlendirme yapma
  if (url.pathname.startsWith("/tr/") || url.pathname.startsWith("/en/")) {
    return next();
  }

  // Türkiye'den gelenler için Türkçe, diğerleri için İngilizceye yönlendir
  if (country === "TR") {
    return Response.redirect(`/tr${url.pathname}${url.search}`, 302);
  } else {
    return Response.redirect(`/en${url.pathname}${url.search}`, 302);
  }
});
