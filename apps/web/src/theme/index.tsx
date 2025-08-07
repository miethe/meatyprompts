import React, { createContext, useContext, useEffect, useState } from 'react';
import light from './themes/light';
import dark from './themes/dark';
import highContrast from './themes/highContrast';

export const themes = { light, dark, highContrast } as const;
export type ThemeName = keyof typeof themes;

type ThemeContextValue = {
  theme: (typeof themes)[ThemeName];
  themeName: ThemeName;
  setThemeName: (name: ThemeName) => void;
};

const ThemeContext = createContext<ThemeContextValue>({
  theme: themes.light,
  themeName: 'light',
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  setThemeName: () => {},
});

export const ThemeProvider: React.FC<{ initialTheme?: ThemeName; children: React.ReactNode }> = ({
  initialTheme = 'light',
  children,
}) => {
  const [themeName, setThemeName] = useState<ThemeName>(initialTheme);
  const theme = themes[themeName];

  useEffect(() => {
    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value);
    });
    root.style.setProperty('--border-radius', theme.borderRadius);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, themeName, setThemeName }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
