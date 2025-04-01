import { PropsWithChildren } from "react";
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material'

import { AppTheme } from "../theme";

export const ThemeProvider = ({ children }: PropsWithChildren) => {
  return (
    <MuiThemeProvider theme={AppTheme}>
      { children }
      <CssBaseline />
    </MuiThemeProvider>
  );
};