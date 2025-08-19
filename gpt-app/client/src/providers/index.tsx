import { PropsWithChildren } from 'react';
import { BrowserRouter } from 'react-router';

import { QueryProvider } from './query-provider';
import { ThemeProvider } from './theme-provider';
import { CityProvider } from './city-provider';
import { ErrorBoundaryProvider } from './error-boundary';
import { AuthProvider } from './auth-provider';
import { TokenProvider } from './token-provider';

export const AppProviders = ({ children }: PropsWithChildren) => (
  <BrowserRouter>
    <QueryProvider>
        <ThemeProvider>
          <ErrorBoundaryProvider>
            <TokenProvider>
              <AuthProvider>
                <CityProvider> {/* TODO-city: move this to a more specific place */}
                  {children}
                </CityProvider>
              </AuthProvider>
            </TokenProvider>
          </ErrorBoundaryProvider>
        </ThemeProvider>
    </QueryProvider>
  </BrowserRouter>
);