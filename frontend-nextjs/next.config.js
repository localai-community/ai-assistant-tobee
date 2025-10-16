/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ['axios'],
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  }
}

module.exports = nextConfig
