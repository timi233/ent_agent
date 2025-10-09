export const colorTokens = {
  primary: '#1F3C88',
  primaryDark: '#0F1F4A',
  accent: '#2FBFDE',
  accentMuted: '#9EE7F2',
  neutral100: '#F5F7FA',
  neutral200: '#E4E9F2',
  neutral400: '#98A0B3',
  neutral600: '#4F566B',
  neutral800: '#1B1F2B',
  success: '#2FBF71',
  warning: '#FFC857',
  danger: '#F25F5C'
} as const

export const typographyTokens = {
  fontFamilyBase: "'Inter', 'Noto Sans SC', system-ui, -apple-system, sans-serif",
  fontFamilyMono: "'Fira Code', 'JetBrains Mono', monospace",
  lineHeightTight: 1.2,
  lineHeightNormal: 1.5,
  lineHeightRelaxed: 1.75,
  headingXL: '32px',
  headingL: '24px',
  headingM: '20px',
  headingS: '16px',
  bodyM: '14px',
  bodyS: '12px'
} as const

export const spacingTokens = {
  xxs: '4px',
  xs: '8px',
  sm: '12px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px'
} as const

export const radiusTokens = {
  sm: '6px',
  md: '12px',
  lg: '20px'
} as const

export const shadowTokens = {
  soft: '0 10px 30px rgba(31, 60, 136, 0.08)',
  medium: '0 18px 40px rgba(15, 31, 74, 0.12)'
} as const

export const themeTokens = {
  colors: colorTokens,
  typography: typographyTokens,
  spacing: spacingTokens,
  radius: radiusTokens,
  shadows: shadowTokens
}
