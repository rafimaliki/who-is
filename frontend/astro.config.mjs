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
      allowedHosts: ['.trycloudflare.com'],
      // Astro writes its own lock/cache state into .astro/ on every start (more often with
      // --force, used in Docker — see frontend/Dockerfile). Without this, Vite's watcher sees
      // that write as a source change and restarts the dev server, which writes the file again,
      // looping forever in a container.
      watch: {
        ignored: ['**/.astro/**']
      }
    }
  }
});
