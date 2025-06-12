import { createContext, PropsWithChildren, useContext, useState } from 'react';
import { Box, useTheme } from '@mui/material';
import { AnimatePresence } from 'framer-motion';

import { Toolbar } from './Toolbar';
import { useAuth } from '../providers/auth-provider';

const LayoutContext = createContext<ILayoutContext>({} as ILayoutContext);

interface ILayoutContext {
  spread: Function;
  unSpread: Function;
  pad: Function;
  unPad: Function;
};

export const useLayout = () => useContext(LayoutContext);

export const LayoutWrapper = ({ children }: PropsWithChildren) => {
  const theme = useTheme();
  const { isAuthenticated } = useAuth();

  const [shouldSpread, setShouldSpread] = useState(false);
  const [shouldPad, setShouldPad] = useState(true);

  const spread = () => setShouldSpread(true);
  const unSpread = () => setShouldSpread(false);

  const pad = () => setShouldPad(true);
  const unPad = () => setShouldPad(false);

  return (
    <>
      <Toolbar unSpread={unSpread} />
      <Box
        sx={{
          width: '100vw',
          height: isAuthenticated ? 'calc(100vh - 64px)' : '100vh', // Adjust 64px to your Toolbar's height if different
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
            padding: shouldPad ? (shouldSpread ? theme.spacing(2) : theme.spacing(6)) : 0,
            borderRadius: shouldSpread ? 0 : +theme.shape.borderRadius * 2,
            boxShadow: theme.shadows[10],
            textAlign: 'center',
            width: shouldSpread ? '90%' : '600px',
            height: shouldSpread ? '100%' : 'auto',
            maxWidth: '90vw',
            minHeight: '60vh',
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
            <LayoutContext.Provider value={{ spread, unSpread, pad, unPad }}>
              {children}
            </LayoutContext.Provider>
          </AnimatePresence>
        </Box>
      </Box>
    </>
  );
};