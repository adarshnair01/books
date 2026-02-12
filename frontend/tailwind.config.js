/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#1173d4",
                "background-light": "#f6f7f8",
                "background-dark": "#101922",
                "paper-cream": "#fdfaf1",
                "paper-sepia": "#f4ecd8",
                "paper-ink": "#1a1a1a"
            },
            fontFamily: {
                "display": ["Newsreader", "serif"],
                "sans": ["Inter", "sans-serif"]
            },
        },
    },
    plugins: [],
}
