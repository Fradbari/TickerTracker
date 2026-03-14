// vite.config.ts
import { defineConfig } from "file:///C:/Users/francesco.dilecce/OneDrive%20-%20LUTECH%20SPA/Documenti/2.%20PERSONALI/3.%20Altro/Ticker%20Tracker/AI%20Studio/Standalone-app-v1/frontend/node_modules/vite/dist/node/index.js";
import react from "file:///C:/Users/francesco.dilecce/OneDrive%20-%20LUTECH%20SPA/Documenti/2.%20PERSONALI/3.%20Altro/Ticker%20Tracker/AI%20Studio/Standalone-app-v1/frontend/node_modules/@vitejs/plugin-react/dist/index.js";
import tailwindcss from "file:///C:/Users/francesco.dilecce/OneDrive%20-%20LUTECH%20SPA/Documenti/2.%20PERSONALI/3.%20Altro/Ticker%20Tracker/AI%20Studio/Standalone-app-v1/frontend/node_modules/@tailwindcss/vite/dist/index.mjs";
import path from "path";
var __vite_injected_original_dirname = "C:\\Users\\francesco.dilecce\\OneDrive - LUTECH SPA\\Documenti\\2. PERSONALI\\3. Altro\\Ticker Tracker\\AI Studio\\Standalone-app-v1\\frontend";
var vite_config_default = defineConfig({
  plugins: [tailwindcss(), react()],
  server: {
    host: "0.0.0.0",
    port: 3e3,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path2) => path2.replace(/^\/api/, "")
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src"),
      "@/shared": path.resolve(__vite_injected_original_dirname, "./src/shared"),
      "@/features": path.resolve(__vite_injected_original_dirname, "./src/features"),
      "@/app": path.resolve(__vite_injected_original_dirname, "./src/app"),
      "@/styles": path.resolve(__vite_injected_original_dirname, "./src/styles")
    }
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: [],
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src"),
      "@/shared": path.resolve(__vite_injected_original_dirname, "./src/shared"),
      "@/features": path.resolve(__vite_injected_original_dirname, "./src/features")
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxmcmFuY2VzY28uZGlsZWNjZVxcXFxPbmVEcml2ZSAtIExVVEVDSCBTUEFcXFxcRG9jdW1lbnRpXFxcXDIuIFBFUlNPTkFMSVxcXFwzLiBBbHRyb1xcXFxUaWNrZXIgVHJhY2tlclxcXFxBSSBTdHVkaW9cXFxcU3RhbmRhbG9uZS1hcHAtdjFcXFxcZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkM6XFxcXFVzZXJzXFxcXGZyYW5jZXNjby5kaWxlY2NlXFxcXE9uZURyaXZlIC0gTFVURUNIIFNQQVxcXFxEb2N1bWVudGlcXFxcMi4gUEVSU09OQUxJXFxcXDMuIEFsdHJvXFxcXFRpY2tlciBUcmFja2VyXFxcXEFJIFN0dWRpb1xcXFxTdGFuZGFsb25lLWFwcC12MVxcXFxmcm9udGVuZFxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vQzovVXNlcnMvZnJhbmNlc2NvLmRpbGVjY2UvT25lRHJpdmUlMjAtJTIwTFVURUNIJTIwU1BBL0RvY3VtZW50aS8yLiUyMFBFUlNPTkFMSS8zLiUyMEFsdHJvL1RpY2tlciUyMFRyYWNrZXIvQUklMjBTdHVkaW8vU3RhbmRhbG9uZS1hcHAtdjEvZnJvbnRlbmQvdml0ZS5jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJ1xyXG5pbXBvcnQgcmVhY3QgZnJvbSAnQHZpdGVqcy9wbHVnaW4tcmVhY3QnXHJcbmltcG9ydCB0YWlsd2luZGNzcyBmcm9tICdAdGFpbHdpbmRjc3Mvdml0ZSdcclxuaW1wb3J0IHBhdGggZnJvbSAncGF0aCdcclxuXHJcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XHJcbiAgcGx1Z2luczogW3RhaWx3aW5kY3NzKCksIHJlYWN0KCldLFxyXG4gIHNlcnZlcjoge1xyXG4gICAgaG9zdDogJzAuMC4wLjAnLFxyXG4gICAgcG9ydDogMzAwMCxcclxuICAgIHByb3h5OiB7XHJcbiAgICAgICcvYXBpJzoge1xyXG4gICAgICAgIHRhcmdldDogcHJvY2Vzcy5lbnYuVklURV9BUElfVEFSR0VUID8/ICdodHRwOi8vbG9jYWxob3N0OjgwMDAnLFxyXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcclxuICAgICAgICByZXdyaXRlOiAocGF0aCkgPT4gcGF0aC5yZXBsYWNlKC9eXFwvYXBpLywgJycpXHJcbiAgICAgIH1cclxuICAgIH1cclxuICB9LFxyXG4gIHJlc29sdmU6IHtcclxuICAgIGFsaWFzOiB7XHJcbiAgICAgICdAJzogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vc3JjJyksXHJcbiAgICAgICdAL3NoYXJlZCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYy9zaGFyZWQnKSxcclxuICAgICAgJ0AvZmVhdHVyZXMnOiBwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi9zcmMvZmVhdHVyZXMnKSxcclxuICAgICAgJ0AvYXBwJzogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vc3JjL2FwcCcpLFxyXG4gICAgICAnQC9zdHlsZXMnOiBwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi9zcmMvc3R5bGVzJyksXHJcbiAgICB9XHJcbiAgfSxcclxuICB0ZXN0OiB7XHJcbiAgICBnbG9iYWxzOiB0cnVlLFxyXG4gICAgZW52aXJvbm1lbnQ6ICdqc2RvbScsXHJcbiAgICBzZXR1cEZpbGVzOiBbXSxcclxuICAgIGFsaWFzOiB7XHJcbiAgICAgICdAJzogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vc3JjJyksXHJcbiAgICAgICdAL3NoYXJlZCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYy9zaGFyZWQnKSxcclxuICAgICAgJ0AvZmVhdHVyZXMnOiBwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi9zcmMvZmVhdHVyZXMnKSxcclxuICAgIH0sXHJcbiAgfSxcclxufSlcclxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUFrbUIsU0FBUyxvQkFBb0I7QUFDL25CLE9BQU8sV0FBVztBQUNsQixPQUFPLGlCQUFpQjtBQUN4QixPQUFPLFVBQVU7QUFIakIsSUFBTSxtQ0FBbUM7QUFLekMsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUyxDQUFDLFlBQVksR0FBRyxNQUFNLENBQUM7QUFBQSxFQUNoQyxRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCxRQUFRO0FBQUEsUUFDTixRQUFRLFFBQVEsSUFBSSxtQkFBbUI7QUFBQSxRQUN2QyxjQUFjO0FBQUEsUUFDZCxTQUFTLENBQUNBLFVBQVNBLE1BQUssUUFBUSxVQUFVLEVBQUU7QUFBQSxNQUM5QztBQUFBLElBQ0Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLEtBQUssUUFBUSxrQ0FBVyxPQUFPO0FBQUEsTUFDcEMsWUFBWSxLQUFLLFFBQVEsa0NBQVcsY0FBYztBQUFBLE1BQ2xELGNBQWMsS0FBSyxRQUFRLGtDQUFXLGdCQUFnQjtBQUFBLE1BQ3RELFNBQVMsS0FBSyxRQUFRLGtDQUFXLFdBQVc7QUFBQSxNQUM1QyxZQUFZLEtBQUssUUFBUSxrQ0FBVyxjQUFjO0FBQUEsSUFDcEQ7QUFBQSxFQUNGO0FBQUEsRUFDQSxNQUFNO0FBQUEsSUFDSixTQUFTO0FBQUEsSUFDVCxhQUFhO0FBQUEsSUFDYixZQUFZLENBQUM7QUFBQSxJQUNiLE9BQU87QUFBQSxNQUNMLEtBQUssS0FBSyxRQUFRLGtDQUFXLE9BQU87QUFBQSxNQUNwQyxZQUFZLEtBQUssUUFBUSxrQ0FBVyxjQUFjO0FBQUEsTUFDbEQsY0FBYyxLQUFLLFFBQVEsa0NBQVcsZ0JBQWdCO0FBQUEsSUFDeEQ7QUFBQSxFQUNGO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFsicGF0aCJdCn0K
