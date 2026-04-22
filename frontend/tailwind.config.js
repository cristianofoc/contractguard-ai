/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#f0f4ff',
          100: '#dbe4ff',
          500: '#4361ee',
          600: '#3a0ca3',
          700: '#2d0880',
        },
        risk: {
          low:    '#198754',
          medium: '#ffc107',
          high:   '#dc3545',
        },
      },
    },
  },
  plugins: [],
}
