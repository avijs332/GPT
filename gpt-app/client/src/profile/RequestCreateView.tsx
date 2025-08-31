import React from 'react';
import { Typography, CircularProgress } from '@mui/material';
import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

import { useToken } from '../providers/token-provider';
import { MotionWrapper } from '../common';

export const RequestCreateView: React.FC = () => {
  const { requestId } = useParams();
  const { getToken } = useToken();
  const navigate = useNavigate();

  useEffect(() => {
    const postRequest = async () => {
      try {
        const res = await axios.post(
          `${import.meta.env.VITE_SERVER_ADDRESS}/api/results`,
          {  requestId },
          {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${getToken()}`,
            },
          }
        );

        if (res.status === 200) {
          navigate(`/result/${res.data.data.id}`);
        }
      } catch (error) {
        // Handle error if needed
      }
    };
    if (requestId) {
      postRequest();
    }
  }, []);

  return (
    <MotionWrapper shouldPad={true} shouldSpread={false}>
      <CircularProgress color="primary" size={60} sx={{ mb: 3 }} />
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Creating Your Route
      </Typography>
      <Typography variant="body1" color="text.secondary" align="center">
        We are now creating the best Route for you,<br />
        please come back later.
      </Typography>
    </MotionWrapper>
  );
};
