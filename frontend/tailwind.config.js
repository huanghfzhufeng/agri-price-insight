/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        soft: "0 20px 45px rgba(31, 23, 54, 0.08)",
      },
    },
  },
  plugins: [],
};
