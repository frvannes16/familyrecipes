import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs';

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    open: false,
    // Only need for localhost development. Follow instructions in README to generate files.
    https: {
      key: fs.readFileSync('../cert/CA/localhost/localhost.decrypted.key'),
      cert: fs.readFileSync('../cert/CA/localhost/localhost.crt')
    }
  },
  plugins: [vue()]
})
