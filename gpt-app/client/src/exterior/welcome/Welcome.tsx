import { Stack, Typography, Paper, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import { Button, MotionWrapper } from '../../common';

export const Welcome = () => {

  return (
    <MotionWrapper shouldPad={false} shouldSpread={true}>
      <Stack alignItems="center" justifyContent="center" minHeight="100vh" sx={{ background: `linear-gradient(135deg, #232946 0%, #16161a 100%)`, py: 6 }}>
        <Paper elevation={10} sx={{
          borderRadius: 4,
          px: { xs: 1, sm: 4, md: 6 },
          py: { xs: 2, sm: 4 },
          width: '100%',
          maxWidth: 'none',
          textAlign: 'center',
          backdropFilter: 'blur(8px)',
          backgroundColor: 'rgba(30, 32, 38, 0.95)',
          color: 'rgba(255,255,255,0.92)',
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.25)'
        }}>
          <img src="/gpt-icon-white.png" alt="GPT Logo" style={{ width: 90, marginBottom: 20 }} />
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom sx={{ fontSize: { xs: '1.5rem', sm: '2rem' } }}>
            Welcome to GPT Smart City
          </Typography>
          <Typography variant="body1" color="text.secondary" mb={3} sx={{ fontSize: { xs: '1rem', sm: '1.15rem' } }}>
            <b>GPT</b> is a smart city solution that uses artificial intelligence to automatically design efficient bus lanes. Our system generates optimized bus routes and lane allocations to improve coverage, reduce congestion, and support sustainable mobility. Powered by deep reinforcement learning and geospatial data, the AI adapts plans to the unique layout and needs of each city.
          </Typography>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={3} justifyContent="center">
            <Paper variant="outlined" sx={{ flex: 1, minWidth: 180, p: 2, borderRadius: 3, background: 'rgba(36, 37, 46, 0.95)', borderColor: 'primary.main' }}>
              <Typography variant="subtitle1" color="primary" fontWeight={600} gutterBottom sx={{ fontSize: '1.1rem' }}>Our Target</Typography>
              <Typography color="text.primary" sx={{ fontSize: '0.95rem' }}>Cities, municipalities, and transit agencies seeking to modernize public transportation and make urban mobility smarter, greener, and more accessible.</Typography>
            </Paper>
            <Paper variant="outlined" sx={{ flex: 1, minWidth: 180, p: 2, borderRadius: 3, background: 'rgba(36, 37, 46, 0.95)', borderColor: 'success.main' }}>
              <Typography variant="subtitle1" color="success.main" fontWeight={600} gutterBottom sx={{ fontSize: '1.1rem' }}>Our Vision</Typography>
              <Typography color="text.primary" sx={{ fontSize: '0.95rem' }}>To revolutionize urban transit by leveraging AI for sustainable, efficient, and inclusive mobility solutions that benefit both people and the environment.</Typography>
            </Paper>
            <Paper variant="outlined" sx={{ flex: 1, minWidth: 180, p: 2, borderRadius: 3, background: 'rgba(36, 37, 46, 0.95)', borderColor: 'secondary.main' }}>
              <Typography variant="subtitle1" color="secondary" fontWeight={600} gutterBottom sx={{ fontSize: '1.1rem' }}>AI-Powered Solution</Typography>
              <Typography color="text.primary" sx={{ fontSize: '0.95rem' }}>Our deep reinforcement learning engine analyzes geospatial data to create adaptive, city-specific bus lane plans—maximizing coverage and minimizing congestion.</Typography>
            </Paper>
          </Stack>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} justifyContent="center" alignItems="center">
            <Box width={{ xs: '100%', sm: 'auto' }}>
              <Link to="/login" style={{ textDecoration: 'none' }}>
                <Button fullWidth label="Login" />
              </Link>
            </Box>
            <Box width={{ xs: '100%', sm: 'auto' }}>
              <Link to="/register" style={{ textDecoration: 'none' }}>
                <Button fullWidth label="Register" />
              </Link>
            </Box>
          </Stack>
        </Paper>
      </Stack>
    </MotionWrapper>
  );
};