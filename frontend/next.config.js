/** @type {import('next').NextConfig} */
const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: backendUrl,
  },
  // Proxy /api/* to backend so browser same-origin = no CORS (avoids Render cold-start / preflight issues)
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${backendUrl}/:path*` }];
  },
}

module.exports = nextConfig
