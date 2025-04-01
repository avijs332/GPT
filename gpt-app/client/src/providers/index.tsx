import { PropsWithChildren } from 'react';
import { BrowserRouter } from 'react-router';

import { QueryProvider } from './query-provider';
import { ThemeProvider } from './theme-provider';

export const AppProviders = ({ children }: PropsWithChildren) => (
  <BrowserRouter>
    <ThemeProvider>
      <QueryProvider>
        {children}
      </QueryProvider>
    </ThemeProvider>
  </BrowserRouter>
);