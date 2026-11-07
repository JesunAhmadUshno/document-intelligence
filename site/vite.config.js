import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads the level results and the exported document texts at build time,
// so every number on the page is generated or computed, never typed.
export default defineConfig({
  base: '/document-intelligence/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
});
