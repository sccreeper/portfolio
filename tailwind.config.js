/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/templates/*.{html,j2}"],
  safelist: [
    "MathJax"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

