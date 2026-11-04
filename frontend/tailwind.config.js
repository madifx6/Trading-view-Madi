/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0c0d10",
        surface: "#131722",
        panel: "#1e222d",
        border: "#2a2e39",
        bull: "#089981",
        bear: "#f23645",
        accent: "#2962ff"
      }
    },
  },
  plugins: [],
}
