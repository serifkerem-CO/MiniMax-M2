/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // B1Z KODLAB - 1111 Theme (Dark Mode Primary)
        'b1z': {
          'black': '#000000',
          'white': '#FFFFFF',
          'gray': {
            900: '#0A0A0A',
            800: '#1A1A1A',
            700: '#2A2A2A',
            600: '#3A3A3A',
            500: '#5A5A5A',
          },
          'accent': '#00FF00',  // Matrix green
          'highlight': '#FFD700', // Gold
        }
      },
      fontFamily: {
        'mono': ['Fira Code', 'Monaco', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': {
            'text-shadow': '0 0 5px #00FF00, 0 0 10px #00FF00',
          },
          '100%': {
            'text-shadow': '0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 30px #00FF00',
          },
        },
      },
    },
  },
  plugins: [],
}
