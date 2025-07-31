/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const config = {
  experimental: {
  },

  // ✅ La configuration des images doit être DANS cet objet
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.gog-statics.com',
        port: '',
        pathname: '/**',
      },
	  {
        protocol: 'https',
        hostname: 'images-*.gog-statics.com',
        port: '',
        pathname: '/**',
      },
      // Ajoutez d'autres domaines ici si nécessaire
    ],
  },

  turbopack: {
    // Vos optimisations Turbo ici si besoin
    // Optimisations Turbo
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
  },

  // Cache plus agressif en dev
  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  }
};

export default config;
