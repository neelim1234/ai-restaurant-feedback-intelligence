/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0f172a", // slate-900
        darkCard: "#1e293b", // slate-800
        accent: "#6366f1", // indigo-500
      }
    },
  },
  plugins: [],
}
