import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#2E75B6",
          600: "#1B3A5C",
          700: "#153050",
          900: "#0f1d33",
        },
      },
    },
  },
  plugins: [],
};
export default config;
