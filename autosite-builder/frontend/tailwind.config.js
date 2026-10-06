/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        arabic: ["Tajawal", "sans-serif"],
      },
      colors: {
        primary: "#1D4ED8",
        secondary: "#F97316",
      },
    },
  },
  plugins: [],
};
