/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          bg:        '#020617',
          surface:   '#0f172a',
          card:      '#1e293b',
          border:    '#334155',
          text:      '#e2e8f0',
          muted:     '#94a3b8',
          primary:   '#06b6d4',
          secondary: '#6366f1',
        },
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #6366f1, #10b981)',
        'brand-logo':     'linear-gradient(135deg, #06b6d4, #6366f1, #a855f7)',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
