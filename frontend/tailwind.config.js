/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // DevOps 深色科技基调：Slate/Zinc 为底，Indigo/Cyan 为强调
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
        },
        cyber: {
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
        },
      },
      boxShadow: {
        glow: '0 0 12px rgba(34, 211, 238, 0.35)',
        'glow-indigo': '0 0 14px rgba(99, 102, 241, 0.35)',
      },
    },
  },
  plugins: [],
}
