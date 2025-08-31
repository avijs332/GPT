import { Divider, Stack, Typography, Paper, Box, CircularProgress } from '@mui/material';
import { MotionWrapper } from '../common';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../providers/auth-provider';
import { useApiGet } from '../hooks';
import { Request } from '../common/types';

interface RequestsApiResult {
  success: boolean;
  data: Request[];
};

export const Profile = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data, isLoading } = useApiGet<RequestsApiResult>(`requests/profile/${user.id}`, { extraKeys: [user.id] });

  if (isLoading) {
    return (
      <MotionWrapper shouldPad={true} shouldSpread={true}>
        <Stack alignItems="center" justifyContent="center" minHeight="100vh">
          <CircularProgress color="primary" size={60} />
        </Stack>
      </MotionWrapper>
    );
  }

  const results = data?.data || [];
  const ongoing = results.filter(r => r.status === 'pending');
  const finished = results.filter(r => r.status === 'finished');

  return (
    <MotionWrapper shouldPad={true} shouldSpread={true}>
      <Stack alignItems="center" justifyContent="center" minHeight="100vh" sx={{ py: 6 }}>
        <Paper elevation={8} sx={{ borderRadius: 4, px: { xs: 2, sm: 6 }, py: { xs: 3, sm: 5 }, width: '100%', maxWidth: 800, textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>
            Profile
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={4} justifyContent="center" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h6">Name</Typography>
              <Typography color="text.secondary">{user.name}</Typography>
            </Box>
            <Box>
              <Typography variant="h6">Email</Typography>
              <Typography color="text.secondary">{user.email}</Typography>
            </Box>
            <Box>
              <Typography variant="h6">Joined</Typography>
              <Typography color="text.secondary">
                {new Date(user.joinedAt).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </Typography>
            </Box>
          </Stack>
        </Paper>
        <Divider sx={{ width: '100%', maxWidth: 800, mb: 4 }} />
        <Paper elevation={6} sx={{ borderRadius: 4, px: { xs: 2, sm: 6 }, py: { xs: 3, sm: 5 }, width: '100%', maxWidth: 800, textAlign: 'left', mb: 4 }}>
          <Typography variant="h5" fontWeight={600} color="primary" gutterBottom>
            Results
          </Typography>
          {finished.length === 0 ? (
            <Typography color="text.secondary">No results yet.</Typography>
          ) : (
            <Stack spacing={2}>
              {finished.map(request => (
                <Paper
                  key={request.id}
                  variant="outlined"
                  sx={{ p: 2, borderRadius: 2, background: '#232946', cursor: 'pointer' }}
                  onClick={() => navigate(`/request/${request.id}`)}
                  elevation={3}
                >
                  <Typography fontWeight={600}>City: {request.city.name} • Lanes: {request.busCount}</Typography>
                  <Typography color="success.main">{request.status}</Typography>
                  <Typography color="info.main">
                    {new Date(request.createdAt).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </Typography>
                </Paper>
              ))}
            </Stack>
          )}
        </Paper>
        <Paper elevation={6} sx={{ borderRadius: 4, px: { xs: 2, sm: 6 }, py: { xs: 3, sm: 5 }, width: '100%', maxWidth: 800, textAlign: 'left' }}>
          <Typography variant="h5" fontWeight={600} color="primary" gutterBottom>
            Ongoing Processes
          </Typography>
          {ongoing.length === 0 ? (
            <Typography color="text.secondary">No ongoing processes.</Typography>
          ) : (
            <Stack spacing={2}>
              {ongoing.map(ongoingRequest => (
                <Paper key={ongoingRequest.id} variant="outlined" sx={{ p: 2, borderRadius: 2, background: '#232946' }}>
                  <Typography fontWeight={600}>City: {ongoingRequest.city.name} • Lanes: {ongoingRequest.busCount}</Typography>
                  <Typography color="warning.main">{ongoingRequest.status}</Typography>
                  <Typography color="info.main">
                    {new Date(ongoingRequest.createdAt).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </Typography>
                </Paper>
              ))}
            </Stack>
          )}
        </Paper>
      </Stack>
    </MotionWrapper>
  );
};
