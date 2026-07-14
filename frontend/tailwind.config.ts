import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "var(--canvas)",
        surface: "var(--surface)",
        "surface-raised": "var(--surface-raised)",
        hairline: "var(--hairline)",
        ink: "var(--ink)",
        "ink-muted": "var(--ink-muted)",
        "ink-faint": "var(--ink-faint)",
        signal: {
          DEFAULT: "var(--signal)",
          soft: "var(--signal-soft)",
          strong: "var(--signal-strong)",
        },
        tab: {
          DEFAULT: "var(--tab)",
          soft: "var(--tab-soft)",
        },
        danger: "var(--danger)",
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "ui-serif", "Georgia", "serif"],
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        card: "14px",
        tab: "6px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.24), 0 8px 24px -12px rgba(0,0,0,0.35)",
        "card-hover": "0 1px 2px rgba(0,0,0,0.3), 0 16px 40px -14px rgba(0,0,0,0.5)",
        "signal-glow": "0 0 0 1px var(--signal-soft), 0 8px 30px -10px var(--signal-soft)",
      },
      keyframes: {
        "card-flip-in": {
          "0%": { opacity: "0", transform: "rotateX(8deg) translateY(10px)" },
          "100%": { opacity: "1", transform: "rotateX(0deg) translateY(0)" },
        },
        "fade-slide-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
      },
      animation: {
        "card-flip-in": "card-flip-in 0.5s cubic-bezier(0.16,1,0.3,1) both",
        "fade-slide-up": "fade-slide-up 0.4s cubic-bezier(0.16,1,0.3,1) both",
        shimmer: "shimmer 1.6s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
