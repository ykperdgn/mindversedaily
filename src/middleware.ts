import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const req = context.request;
  const country = req.headers.get("x-vercel-ip-country") || "US";
  const url = new URL(req.url);
  const { pathname, search, origin } = url;

  // Do not redirect requests already under language prefix or for static assets
  const skipPrefixes = ["/tr/", "/en/"];
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
