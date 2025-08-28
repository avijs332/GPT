import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  CircularProgress
} from '@mui/material';

import { MotionWrapper } from '../common';
import { useToken } from '../providers/token-provider';

export const RequestRejectedView: React.FC = () => {
  const navigate = useNavigate();
  const { requestId } = useParams<{ requestId: string }>();
  const { getToken } = useToken();
  
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const submitFeedback = useMutation({
    mutationFn: async (feedbackText: string) => {
      const response = await axios.post(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/requests/${requestId}/reject`,
        { feedback: feedbackText },
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    },
    onSuccess: () => {
      setSubmitted(true);
      // Navigate back to the request view after a short delay
      setTimeout(() => {
        navigate(`/request/${requestId}`);
      }, 2000);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (feedback.trim()) {
      submitFeedback.mutate(feedback.trim());
    }
  };

  const handleGoBack = () => {
    navigate(`/request/${requestId}`);
  };

  if (submitted) {
    return (
      <MotionWrapper shouldPad={true} shouldSpread={false}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center'
        }}>
          <Alert severity="success" sx={{ mb: 3, width: '100%', maxWidth: 500 }}>
            Thank you for your feedback! We will review your comments and work to improve our results.
          </Alert>
          <Typography variant="body1" color="text.secondary">
            Redirecting you back to your request...
          </Typography>
        </Box>
      </MotionWrapper>
    );
  }

  return (
    <MotionWrapper shouldPad={true} shouldSpread={false}>
      <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
        <Paper elevation={2} sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom color="error" sx={{ mb: 2 }}>
            We're Sorry
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.6 }}>
            We are sorry that the current results don't satisfy you. Please let us know what you would like improved, and we will get back to you with better solutions.
          </Typography>

          <form onSubmit={handleSubmit}>
            <TextField
              label="What would you like us to improve?"
              multiline
              rows={6}
              fullWidth
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Please describe what didn't meet your expectations and what improvements you'd like to see..."
              variant="outlined"
              sx={{ mb: 3 }}
              required
              disabled={submitFeedback.isPending}
            />

            {submitFeedback.isError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                Failed to submit feedback. Please try again.
              </Alert>
            )}

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                type="button"
                variant="outlined"
                onClick={handleGoBack}
                disabled={submitFeedback.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={!feedback.trim() || submitFeedback.isPending}
                startIcon={submitFeedback.isPending ? <CircularProgress size={20} /> : null}
              >
                {submitFeedback.isPending ? 'Submitting...' : 'Submit Feedback'}
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </MotionWrapper>
  );
};