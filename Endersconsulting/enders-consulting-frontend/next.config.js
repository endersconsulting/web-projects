/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ensure proper trailing slash handling
  trailingSlash: false,
  
  // Configure headers for proper proxying
  async headers() {
    return [
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig