/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './templates/**/*.html',     // Adjust path as needed
      './**/templates/**/*.html',  // For multiple Django apps
  ],
  theme: {
      extend: {},
  },
  plugins: [],
}
