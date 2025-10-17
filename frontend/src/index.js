export default {
  async fetch(request, env) {
    // Serve static assets from Next.js build
    const url = new URL(request.url);

    // Try to serve from static assets
    if (url.pathname.startsWith('/_next/')) {
      return env.ASSETS.fetch(request);
    }

    // For all other routes, serve index.html (client-side routing)
    return env.ASSETS.fetch(new URL('/index.html', request.url));
  }
};
