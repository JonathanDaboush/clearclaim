/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // ── Spec palette (font-end specs.txt) ──────────────────────────────
        bg:        '#F4F6F7',
        card:      '#FFFFFF',
        section:   '#EEF2F4',
        border:    '#D9E0E5',
        // Text
        primary:   '#1F2A33',    // primary text
        secondary: '#5C6B75',    // secondary text
        meta:      '#7B8A94',    // metadata / timestamps
        // Accent (primary)
        accent: {
          DEFAULT: '#3A5A78',
          hover:   '#2F4B63',
          light:   '#D8E4ED',
        },
        // Accent (secondary / teal)
        teal: {
          DEFAULT: '#6F8A87',
          light:   '#E4ECEB',
        },
        // Status
        confirmed: '#4F8A6F',
        pending:   '#C89B3C',
        disputed:  '#C05656',
        info:      '#5B7FA6',
      },
      fontFamily: {
        sans: ['"Inter"', '"Roboto"', '"Source Sans 3"', 'ui-sans-serif', 'system-ui'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'ui-monospace'],
      },
      fontSize: {
        // Enforce spec minimums
        xs:   ['0.75rem',  { lineHeight: '1.2' }],   // 12px metadata
        sm:   ['0.875rem', { lineHeight: '1.4' }],   // 14px metadata
        base: ['1rem',     { lineHeight: '1.6' }],   // 16px body minimum
        lg:   ['1.125rem', { lineHeight: '1.5' }],
        xl:   ['1.25rem',  { lineHeight: '1.4' }],   // 20px
        '2xl':['1.5rem',   { lineHeight: '1.3' }],   // 24px
        '3xl':['1.75rem',  { lineHeight: '1.25' }],  // 28px
      },
      boxShadow: {
        card:    '0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        'card-md':'0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06)',
        'card-lg':'0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.05)',
      },
      borderColor: {
        DEFAULT: '#D9E0E5',
      },
    },
  },
  plugins: [],
}
