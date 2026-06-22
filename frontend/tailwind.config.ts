/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B1220",
        panel: "#111827",
        border: "#1F2937",
        primary: "#22C55E",
        warning: "#F59E0B",
        critical: "#EF4444",
        accent: "#8B5CF6",
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(34, 197, 94, 0.3)",
      },
    },
  },
  plugins: [],
}
