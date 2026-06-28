/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["Georgia", "Cambria", "\"Times New Roman\"", "serif"],
        sans: ["\"Segoe UI\"", "Tahoma", "Geneva", "Verdana", "sans-serif"],
      },
      boxShadow: {
        halo: "0 30px 80px rgba(148, 163, 184, 0.18)",
      },
    },
  },
  plugins: [],
};
