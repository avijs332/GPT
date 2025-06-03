import { Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

import { Button, MotionWrapper } from '../common';

export const Home = () => {
  const navigate = useNavigate();
  console.log(import.meta.env.VITE_SERVER_ADDRESS)

  return (
    <MotionWrapper>
      <img src="/gpt-logo.png" alt="GPT Logo" style={{ width: 100, marginBottom: 16 }} />
      <Typography variant="h3" gutterBottom>
        Welcome to GPT
      </Typography>
      <Typography variant="body1" paragraph>
        Generative Public Transport (GPT) helps cities design optimized and intelligent bus lanes using generative algorithms. Plan your city’s future with data-driven public transport.
      </Typography>
      <Button label='Start Planning' onClick={() => navigate('/plan')} />
    </MotionWrapper>
  );
};