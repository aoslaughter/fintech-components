import { defineConfig } from 'vite'
import { resolve } from 'path';

export default defineConfig({
    base: "/static/",
    build: {
      manifest: "manifest.json",
      outDir: resolve("./assets"),
      assetsDir: "django-assets",
      rollupOptions: {
        input: {
          test: resolve("./static/primary/main.js")
        },
      }
    }
  })
  