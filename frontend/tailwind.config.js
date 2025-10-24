/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fdf2f2',
          100: '#fce4e4',
          200: '#f9cdcd',
          300: '#f5a8a8',
          400: '#ef7575',
          500: '#e74c3c',
          600: '#d73527',
          700: '#b42318',
          800: '#951b16',
          900: '#7c1d1d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
