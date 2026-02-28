/** @type {import('postcss').Config} */
// Tailwind CSS v4 is handled via the @tailwindcss/vite Vite plugin.
// Only autoprefixer is needed here for vendor-prefix compatibility.
export default {
  plugins: {
    autoprefixer: {},
  },
}
