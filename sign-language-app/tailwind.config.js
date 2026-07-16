/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans Thai"', 'sans-serif'],
        display: ['"Prompt"', 'sans-serif'],
      },
      colors: {
        'brand-teal': '#00F2FE',
        'brand-purple': '#4FACFE',
      }
    },
  },
  plugins: [],
}
