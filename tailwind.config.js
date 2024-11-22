/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',  // Django templates
    './static/js/**/*.js',    // JavaScript files
    './**/*.html',            // Any additional HTML files
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

