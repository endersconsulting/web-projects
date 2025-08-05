/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ensure proper asset prefix handling
  assetPrefix: '',
  
  // Disable SWC minification if there are issues
  swcMinify: false,
  
  // Configure output for standalone deployment
  output: 'standalone',
  
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