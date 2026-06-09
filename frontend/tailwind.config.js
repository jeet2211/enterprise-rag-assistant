/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Trebuchet MS"', '"Avenir Next"', 'ui-sans-serif', 'system-ui'],
        body: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(255,255,255,0.08), 0 24px 80px rgba(0,0,0,0.45)',
      },
      backgroundImage: {
        'grid-radial':
          'radial-gradient(circle at top left, rgba(77, 197, 255, 0.14), transparent 28%), radial-gradient(circle at bottom right, rgba(255, 175, 77, 0.12), transparent 24%)',
      },
    },
  },
  plugins: [],
}
