import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@store': path.resolve(__dirname, './src/store'),
      '@lib': path.resolve(__dirname, './src/lib'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
  server: {
    port: 3000,
    // Proxy API requests to backend server when in development
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: process.env.NODE_ENV !== 'production',
    // Enable minification and tree shaking
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: process.env.NODE_ENV === 'production',
      },
    },
    // Configure code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor code into separate chunks
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // Split UI components into a separate chunk
          ui: ['@components/ui'],
          // Split chart libraries into a separate chunk
          charts: ['chart.js', 'react-chartjs-2'],
        },
        // Optimize chunk size
        chunkFileNames: (chunkInfo) => {
          const name = chunkInfo.name;
          if (name === 'vendor') {
            return 'assets/vendor.[hash].js';
          }
          return 'assets/[name].[hash].js';
        },
      },
    },
    // Optimize CSS
    cssCodeSplit: true,
    // Reduce chunk size warnings threshold
    chunkSizeWarningLimit: 1000,
  },
});