/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          blue: '#0088cc',
          light: '#54a9eb',
          dark: '#006bb3',
        },
        background: {
          primary: '#ffffff',
          secondary: '#f4f4f5',
        },
        text: {
          primary: '#000000',
          secondary: '#707579',
        },
        border: '#e4e4e7',
        message: {
          out: '#effdde',
          in: '#ffffff',
        },
      },
    },
  },
  plugins: [],
}; 