import { createTheme } from "@mui/material/styles";

export const AppTheme = createTheme({
  palette: {
    mode: "dark", // Default to dark mode
    primary: {
      main: "#646cff",
    },
    background: {
      default: "#242424",
    },
    text: {
      primary: "rgba(255, 255, 255, 0.87)",
    },
  },
  typography: {
    fontFamily: "Inter, system-ui, Avenir, Helvetica, Arial, sans-serif",
    fontWeightRegular: 400,
    h1: {
      fontSize: "3.2em",
      lineHeight: 1.1,
    },
    button: {
      fontSize: "1em",
      fontWeight: 500,
      textTransform: "none",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "8px",
          border: "1px solid transparent",
          padding: "0.6em 1.2em",
          backgroundColor: "#1a1a1a",
          cursor: "pointer",
          transition: "border-color 0.25s",
          "&:hover": {
            borderColor: "#646cff",
          },
          "&:focus, &:focus-visible": {
            outline: "4px auto -webkit-focus-ring-color",
          },
        },
      },
    },
    MuiLink: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          color: "#646cff",
          textDecoration: "inherit",
          "&:hover": {
            color: "#535bf2",
          },
        },
      },
    },
  },
});