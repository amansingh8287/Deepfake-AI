/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["DM Sans", "sans-serif"]
      },
      colors: {
        ink: "#06131f",
        panel: "#0d1b29",
        glow: "#00d4ff",
        danger: "#ff637d",
        success: "#5ef2b3"
      },
      boxShadow: {
        glass: "0 20px 60px rgba(0, 0, 0, 0.35)"
      },
      backgroundImage: {
        "hero-mesh":
          "radial-gradient(circle at 20% 20%, rgba(0, 212, 255, 0.18), transparent 35%), radial-gradient(circle at 80% 0%, rgba(94, 242, 179, 0.14), transparent 30%), linear-gradient(135deg, #030711 0%, #0a1625 45%, #08111d 100%)"
      }
    }
  },
  plugins: []
};

