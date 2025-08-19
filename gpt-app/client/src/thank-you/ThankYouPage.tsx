import { Box, Button, Stack, Typography } from '@mui/material';
import { Link } from 'react-router-dom';
import { MotionWrapper } from '../common';

export const ThankYouPage = () => {
  return (
    <MotionWrapper shouldPad={true} shouldSpread={false}>
        <Stack alignItems="center" justifyContent="center" spacing={4} sx={{ minHeight: '60vh' }}>
        <Typography variant="h3" color="primary" gutterBottom>
            Thank you for submitting a request!
        </Typography>
        <Box display="flex" gap={2}>
            <Button component={Link} to="/" variant="contained" color="primary">
            Create a new one
            </Button>
            <Button component={Link} to="/profile" variant="outlined" color="primary">
            Go to see requests
            </Button>
        </Box>
        </Stack>
    </MotionWrapper>
  );
};
