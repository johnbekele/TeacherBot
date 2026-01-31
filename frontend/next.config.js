/** @type {import('next').NextConfig} */

// Backend URL for the rewrite proxy (set NEXT_PUBLIC_API_URL env var on Vercel)
const backendUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const nextConfig = {
  reactStrictMode: true,
  // Proxy /api/* to backend - browser calls /api/*, Vercel forwards to Render
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${backendUrl}/:path*` }];
  },
}

module.exports = nextConfig
