import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  // In development, do not apply redirects
  if (import.meta.env.DEV) return next();

  const req = context.request;
  const country = req.headers.get("x-vercel-ip-country") || "US";
  const url = new URL(req.url);
  const { pathname, search, origin } = url;

  // Do not redirect requests for language prefixes or static assets
  const skipPrefixes = ["/tr/", "/en/", "/tr", "/en"];
  const skipExts = [".png", ".jpg", ".jpeg", ".svg", ".ico", ".css", ".js", ".json"];
  if (
    skipPrefixes.some(p => pathname.startsWith(p)) ||
    skipExts.some(ext => pathname.endsWith(ext))
  ) {
    return next();
  }

  const langPrefix = country === "TR" ? "/tr" : "/en";
  const redirectTo = new URL(`${langPrefix}${pathname}${search}`, origin).toString();
  return Response.redirect(redirectTo, 302);
});
