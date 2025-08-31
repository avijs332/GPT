import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Paper from '@mui/material/Paper';

import { useApiGet } from "../hooks";
import { ResultApiResponse } from "../results";
import { MotionWrapper } from "../common";

export const RequestView: React.FC = () => {
  const navigate = useNavigate();
  const { requestId } = useParams<{ requestId: string }>();

  const { data, isLoading } = useApiGet<{
    Sucess: boolean;
    data: ResultApiResponse[]
  }>(`results/requests/${requestId}`, { extraKeys: [requestId] });
  

  const handleCreateNew = () => {
    navigate(`/request/${requestId}/create`);
  };

  const handleNotSatisfied = () => {
    navigate(`/request/${requestId}/retry`);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <MotionWrapper shouldPad={true} shouldSpread={true}>
      <Box sx={{ padding: 3 }}>
        <Typography variant="h4" gutterBottom>
          Request Details
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Request ID: {requestId}
        </Typography>
        <Typography variant="h6" sx={{ mt: 2 }}>
          Available Results
        </Typography>
        <List>
          {data?.data && data.data.map((result) => {
            const timestamp = result.createdAt
              ? new Date(result.createdAt).toLocaleString('en-US', {
                  year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                })
              : new Date().toLocaleString('en-US', {
                  year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                });
            return (
              <ListItem
                key={result.id}
                sx={{ mb: 2, cursor: 'pointer' }}
                onClick={() => navigate(`/result/${result.id}`)}
              >
                <Paper sx={{ padding: 2, width: '100%' }} elevation={2}>
                  <Typography variant="body2">ID: {result.id}</Typography>
                  <Typography variant="caption" color="text.secondary">{timestamp}</Typography>
                </Paper>
              </ListItem>
            );
          })}
        </List>
        <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
          <Button variant="contained" color="primary" onClick={handleCreateNew}>
            Create New Result
          </Button>
          <Button variant="contained" color="error" onClick={handleNotSatisfied}>
            Not Satisfied? Retry
          </Button>
        </Box>
      </Box>
    </MotionWrapper>
  );
};