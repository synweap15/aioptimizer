export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    try {
      // Try to fetch the exact path from assets
      const response = await env.ASSETS.fetch(request);

      // If we get a 404, try to serve index.html for client-side routing
      if (response.status === 404) {
        // For HTML routes, serve index.html
        if (!url.pathname.includes('.') && !url.pathname.startsWith('/_next/')) {
          return env.ASSETS.fetch(new URL('/index.html', request.url));
        }
      }

      return response;
    } catch (error) {
      // Fallback to index.html
      return env.ASSETS.fetch(new URL('/index.html', request.url));
    }
  }
};
