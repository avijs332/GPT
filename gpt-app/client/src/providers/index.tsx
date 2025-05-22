import { PropsWithChildren } from 'react';
import { BrowserRouter } from 'react-router';

import { QueryProvider } from './query-provider';
import { ThemeProvider } from './theme-provider';
import { CityProvider } from './city-provider';
import { ErrorBoundaryProvider } from './error-boundary';

export const AppProviders = ({ children }: PropsWithChildren) => (
  <BrowserRouter>
    <QueryProvider>
      <CityProvider>
        <ThemeProvider>
          <ErrorBoundaryProvider>
            {children}
          </ErrorBoundaryProvider>
        </ThemeProvider>
      </CityProvider>
    </QueryProvider>
  </BrowserRouter>
);