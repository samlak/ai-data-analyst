/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
  safelist: [
    'prose',
    'max-w-none',
    {
      pattern: /bg-(gray|blue)-(50|100|200|500|600|700|800)/,
    },
  ],
};