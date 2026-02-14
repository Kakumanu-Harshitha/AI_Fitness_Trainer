/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#B4FF39",
        secondary: "#18181b",
        accent: "#27272a",
        background: "#000000",
        card: "rgba(24, 24, 27, 0.8)",
        border: "rgba(39, 39, 42, 1)",
        text: "#ffffff",
        textSecondary: "#a1a1aa",
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
