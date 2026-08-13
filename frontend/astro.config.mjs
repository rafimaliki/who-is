// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  devToolbar: {
    enabled: false
  },
  vite: {
    plugins: [tailwindcss()],
    // Lets the dev server respond behind a Cloudflare quick tunnel (*.trycloudflare.com), which
    // Vite's Host-header check otherwise blocks with 403 — dev convenience only, not used in prod.
    server: {
      allowedHosts: ['.trycloudflare.com']
    }
  }
});
