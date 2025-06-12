import { Box, Toolbar as MuiToolbar } from '@mui/material';
import { FC } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../providers/auth-provider';

interface ToolbarProps {
  unSpread: () => void;
};

export const Toolbar: FC<ToolbarProps> = ({ unSpread }) => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    unSpread();
    logout();
  };

  return (
    <>
      {
        isAuthenticated && (
          <MuiToolbar>
            <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'space-between' }} >
              <Box
                component="button"
                onClick={() => navigate('/')}
                sx={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  padding: 0,
                  margin: 0,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                }}
                title="Go to Home"
              >
                <img src="/gpt-icon-white.png" alt="GPT Logo" style={{ width: 60, marginRight: 16 }} />
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box
                  component="button"
                  onClick={() => navigate('/profile')}
                  sx={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    padding: 0,
                    display: 'flex',
                    alignItems: 'center',
                    marginRight: 2
                  }}
                  title="Go to Profile"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.7 0 8 1.34 8 4v2H4v-2c0-2.66 5.3-4 8-4zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/>
                  </svg>
                </Box>
                <Box
                  component="button"
                  onClick={handleLogout}
                  sx={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    padding: 0,
                    display: 'flex',
                    alignItems: 'center',
                  }}
                  title="Logout"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24"
                    width="24"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M16 13v-2H7V8l-5 4 5 4v-3zM20 3h-8c-1.1 0-2 .9-2 2v4h2V5h8v14h-8v-4h-2v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
                  </svg>
                </Box>
              </Box>
            </Box>
          </MuiToolbar>
        )
      }
    </>
  );
};