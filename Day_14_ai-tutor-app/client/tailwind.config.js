/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // "Blush rose" palette — light, airy pink vellum with a soft
        // rose → blush → white ramp, taken from the reference swatch
        // (dusty rose / blush pink / white with a mauve border).
        codex: {
          bg: '#FFFFFF',         // clean white page background
          panel: '#FDF1F3',      // soft blush pink — sidebar, cards, bubbles
          panelAlt: '#FCE3E8',   // slightly deeper pink — inputs, hovers
          border: '#F0C9D3',     // soft rose border
          text: '#4A2333',       // deep rose-plum, for readable body text
          muted: '#AD7986',      // dusty rose-mauve, for secondary text
        },
        gold: {
          leaf: '#D9567E',       // vivid rose pink — signature companion accent
          dim: '#B23F63',
        },
        rubric: {
          red: '#E0808C',        // soft coral-rose — for the reader's turn
          dim: '#C4606C',
        },
        // Extra swatch tokens, taken directly from the reference palette,
        // available for accents, badges, chips, tags, etc.
        clay: '#D9567E',         // vivid rose pink
        tan: '#E0A5A5',          // mid dusty rose
        khaki: '#FCE3E8',        // light blush pink
        sage: '#D9567E',         // companion accent (reuses vivid rose)
        dusty: '#F5D6DC',        // light accent
      },
      fontFamily: {
        display: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        body: ['"Spectral"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        illuminate: '0 0 24px rgba(217, 86, 126, 0.14)',     // rose glow
        rubric: '0 0 20px rgba(224, 128, 140, 0.14)',        // coral-rose glow
      },
      backgroundImage: {
        vignette: 'radial-gradient(ellipse at top, rgba(217,86,126,0.05), transparent 55%), radial-gradient(ellipse at bottom, rgba(245,214,220,0.5), transparent 50%)',
      },
    },
  },
  plugins: [],
}
