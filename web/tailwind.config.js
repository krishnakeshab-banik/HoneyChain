/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        paper: "#F5EEE3",
        ink: "#2B211B",
        amber: "#9a6a16",
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        body: ["Source Sans 3", "sans-serif"],
      },
    },
  },
  plugins: [],
};
