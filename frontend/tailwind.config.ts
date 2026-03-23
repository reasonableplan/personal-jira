import type { Config } from 'tailwindcss';
import { THEME_COLORS } from './src/theme/colors';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: THEME_COLORS.primary,
        status: THEME_COLORS.status,
        priority: THEME_COLORS.priority,
        'issue-status': THEME_COLORS.issueStatus,
      },
    },
  },
  plugins: [],
};

export default config;
