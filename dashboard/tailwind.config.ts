import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0a",
        card: "#111111",
        border: "#222222",
        accent: "#a855f7"
      }
    }
  },
  plugins: []
};

export default config;
