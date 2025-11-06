/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  safelist: [
    'bg-blue-50',
    'bg-green-50',
    'bg-red-50',
    'bg-purple-50',
    'text-blue-600',
    'text-green-600',
    'text-red-600',
    'text-purple-600',
    'border-blue-200',
    'border-green-200',
    'border-red-200',
    'border-purple-200'
  ]
}