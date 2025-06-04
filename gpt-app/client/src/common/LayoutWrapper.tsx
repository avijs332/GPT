import { createContext, PropsWithChildren, useContext, useState } from 'react';
import { Box, useTheme } from '@mui/material';
import { AnimatePresence } from 'framer-motion';

const LayoutContext = createContext<ILayoutContext>({} as ILayoutContext);

interface ILayoutContext {
  spread: Function;
  unSpread: Function;
};

export const useLayout = () => useContext(LayoutContext);

export const LayoutWrapper = ({ children }: PropsWithChildren) => {
  const theme = useTheme();

  const [shouldSpread, setShouldSpread] = useState(false);

  const spread = () => setShouldSpread(true);
  const unSpread = () => setShouldSpread(false);

  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        backgroundImage: 'url(/roads-background.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden'
      }}
    >
      <Box
        sx={{
          backgroundColor: theme.palette.background.paper,
          padding: shouldSpread ? theme.spacing(2) : theme.spacing(6),
          borderRadius: shouldSpread ? 0 : theme.shape.borderRadius * 2,
          boxShadow: theme.shadows[10],
          textAlign: 'center',
          width: shouldSpread ? '90%' : '600px',
          height: shouldSpread ? '100%' : 'auto',
          maxWidth: '90vw',
          backdropFilter: 'blur(8px)',
          transition: 'all 0.3s ease-in-out',
          overflow: 'auto',          
          '&::-webkit-scrollbar': {
          width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#888',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            backgroundColor: '#555',
          },

          // Firefox support (limited)
          scrollbarWidth: 'thin',
          scrollbarColor: '#888 transparent',
        }}
      >
        <AnimatePresence mode='wait'>
          <LayoutContext.Provider value={{ spread, unSpread }}>
            {children}
          </LayoutContext.Provider>
        </AnimatePresence>
      </Box>
    </Box>
  );
};