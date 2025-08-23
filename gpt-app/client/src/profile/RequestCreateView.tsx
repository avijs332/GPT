import React from 'react';
import { Typography, CircularProgress, Paper } from '@mui/material';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

import { useToken } from '../providers/token-provider';
import { MotionWrapper } from '../common';

export const RequestCreateView: React.FC = () => {
  const { requestId } = useParams();
  const { getToken } = useToken();

  useEffect(() => {
    const postRequest = async () => {
      try {
        await axios.post(
          `${import.meta.env.VITE_SERVER_ADDRESS}/api/results`,
          {  requestId },
          {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${getToken()}`,
            },
          }
        );
      } catch (error) {
        // Handle error if needed
      }
    };
    if (requestId) {
      postRequest();
    }
  }, []);

  return (
    <MotionWrapper shouldPad={true} shouldSpread={true}>
      <Paper
        elevation={6}
        sx={{
          p: 5,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          maxWidth: 400,
          width: '100%',
        }}
      >
        <CircularProgress color="primary" size={60} sx={{ mb: 3 }} />
        <Typography variant="h5" fontWeight={700} gutterBottom>
          Creating Your Route
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center">
          We are now creating the best Route for you,<br />
          please come back later.
        </Typography>
      </Paper>
    </MotionWrapper>
  );
};
