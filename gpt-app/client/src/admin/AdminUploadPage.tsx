import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import FeedbackIcon from '@mui/icons-material/Feedback';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Alert from '@mui/material/Alert';
import Chip from '@mui/material/Chip';
import { useParams } from 'react-router-dom';

import { useToken } from '../providers/token-provider';
import { MotionWrapper } from '../common';

interface Model {
  id: string;
  filename: string;
  requestId: string;
  uploadedAt: string;
  size?: number;
}

interface Feedback {
  id: string;
  requestId: string;
  feedback: string;
  createdAt: string;
  userId: string;
}

export const AdminUploadPage = () => {
  const { requestId } = useParams<{ requestId: string }>();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);  const [requestModels, setRequestModels] = useState<Model[]>([]);
  const [requestFeedbacks, setRequestFeedbacks] = useState<Feedback[]>([]);
  const [loadingRequestModels, setLoadingRequestModels] = useState(false);
  const [loadingRequestFeedbacks, setLoadingRequestFeedbacks] = useState(false);
  const [feedbackDialog, setFeedbackDialog] = useState<{ open: boolean; feedback: Feedback | null }>({
    open: false,
    feedback: null
  });
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; modelId: string | null }>({
    open: false,
    modelId: null
  });
  const { getToken } = useToken();
  useEffect(() => {
    if (tabValue === 1 && requestId) {
      fetchRequestModels();
    } else if (tabValue === 2 && requestId) {
      fetchRequestFeedbacks();
    }
  }, [tabValue, requestId]);

  const fetchRequestModels = async () => {
    if (!requestId) return;
    
    setLoadingRequestModels(true);
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/admin/models/request/${requestId}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          }
        }
      );
      setRequestModels(response.data.data || []);
    } catch (err) {
      console.error('Failed to fetch request models:', err);
      setResult('Failed to fetch request models.');
    } finally {
      setLoadingRequestModels(false);
    }
  };
  const fetchRequestFeedbacks = async () => {
    if (!requestId) return;
    
    setLoadingRequestFeedbacks(true);
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/admin/feedbacks/request/${requestId}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          }
        }
      );
      setRequestFeedbacks(response.data.data || []);
    } catch (err) {
      console.error('Failed to fetch request feedbacks:', err);
      setResult('Failed to fetch request feedbacks.');
    } finally {
      setLoadingRequestFeedbacks(false);
    }
  };
  const handleDeleteModel = async (modelId: string) => {
    try {
      await axios.delete(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/admin/models/${modelId}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          }
        }
      );
      setResult('Model deleted successfully.');
      if (requestId) {
        fetchRequestModels(); // Refresh request models if we're viewing a specific request
      }
      setDeleteConfirm({ open: false, modelId: null });
    } catch (err) {
      console.error('Failed to delete model:', err);
      setResult('Failed to delete model.');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setResult(null);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !requestId) return;
    setUploading(true);
    setResult(null);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('request_id', requestId);
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/admin/upload-model/`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          }
        }
      );
      const data = response.data;
      setResult(data.doc_id ? `Upload successful! Doc ID: ${data.doc_id}` : 'Upload failed.');      if (data.doc_id) {
        if (tabValue === 1) {
          fetchRequestModels(); // Refresh request models if we're on that tab
        }
      }
    } catch (err) {
      setResult('Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleMarkComplete = async () => {
    if (!requestId) return;
    try {
      await axios.put(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/admin/requests/complete/${requestId}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          }
        }
      );
      setResult('Request marked as complete!');
    } catch (err) {
      setResult('Failed to mark request as complete.');
    }
  };

  return (
    <MotionWrapper shouldSpread={true} shouldPad={true}>
      <Box sx={{ maxWidth: 1200, margin: '0 auto', color: 'black' }}>
        <Typography variant="h4" gutterBottom sx={{ color: 'white', mb: 3 }}>
          Admin Panel
        </Typography>
        
        <Paper sx={{ mb: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={(_, newValue) => setTabValue(newValue)}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"          >
            <Tab label="Upload Model" />
            {requestId && <Tab label="Request Models" />}
            {requestId && <Tab label="Request Feedbacks" />}
          </Tabs>
        </Paper>

        {/* Tab 0: Upload Model */}
        {tabValue === 0 && (
          <Paper sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>Upload Model for Request</Typography>
            {requestId && (
              <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                Request ID: {requestId}
              </Typography>
            )}
            
            <Box component="form" onSubmit={handleUpload}>
              <Button
                variant="contained"
                component="label"
                sx={{ width: '100%', mb: 2 }}
              >
                Select Model File
                <input type="file" accept=".keras" hidden onChange={handleFileChange} />
              </Button>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {file ? `Selected file: ${file.name}` : 'No file selected'}
              </Typography>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={!file || uploading}
                sx={{ width: '100%', mb: 2 }}
              >
                {uploading ? <CircularProgress size={24} /> : 'Upload Model'}
              </Button>
            </Box>
            
            {requestId && (
              <Button
                variant="outlined"
                color="success"
                sx={{ width: '100%', mb: 2 }}
                onClick={handleMarkComplete}
                disabled={!requestId || uploading}
              >
                Mark Request as Complete
              </Button>
            )}
            
            {result && (
              <Alert severity={result.includes('successful') ? 'success' : 'error'} sx={{ mt: 2 }}>
                {result}
              </Alert>
            )}
          </Paper>
        )}

        {/* Tab 1: Request Models (only show if requestId exists) */}
        {tabValue === 1 && requestId && (
          <Paper sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>Models for Request: {requestId}</Typography>
            {loadingRequestModels ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <List>
                {requestModels.length === 0 ? (
                  <Typography variant="body1" sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>
                    No models found for this request
                  </Typography>
                ) : (
                  requestModels.map((model) => (
                    <ListItem key={model.id} sx={{ border: 1, borderColor: 'divider', mb: 1, borderRadius: 1 }}>
                      <ListItemText
                        primary={model.filename}
                        secondary={
                          <Box>
                            <Typography variant="caption" display="block">
                              Uploaded: {new Date(model.uploadedAt).toLocaleString()}
                            </Typography>
                            {model.size && (
                              <Typography variant="caption" display="block">
                                Size: {(model.size / 1024 / 1024).toFixed(2)} MB
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => setDeleteConfirm({ open: true, modelId: model.id })}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItem>
                  ))
                )}
              </List>
            )}
          </Paper>
        )}        {/* Tab 2: Request Feedbacks (only show if requestId exists) */}
        {tabValue === 2 && requestId && (
          <Paper sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>Feedbacks for Request: {requestId}</Typography>
            {loadingRequestFeedbacks ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <List>
                {requestFeedbacks.length === 0 ? (
                  <Typography variant="body1" sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>
                    No feedbacks found for this request
                  </Typography>
                ) : (
                  requestFeedbacks.map((feedback) => (
                    <ListItem key={feedback.id} sx={{ border: 1, borderColor: 'divider', mb: 1, borderRadius: 1 }}>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1">User ID: {feedback.userId}</Typography>
                            <Chip 
                              size="small" 
                              label={new Date(feedback.createdAt).toLocaleDateString()} 
                              variant="outlined" 
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" sx={{ 
                            overflow: 'hidden', 
                            textOverflow: 'ellipsis', 
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical'
                          }}>
                            {feedback.feedback}
                          </Typography>
                        }
                      />
                      <IconButton
                        edge="end"
                        aria-label="view feedback"
                        onClick={() => setFeedbackDialog({ open: true, feedback })}
                        color="primary"
                      >
                        <FeedbackIcon />
                      </IconButton>
                    </ListItem>
                  ))
                )}
              </List>
            )}
          </Paper>
        )}

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteConfirm.open}
          onClose={() => setDeleteConfirm({ open: false, modelId: null })}
        >
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            <Typography>Are you sure you want to delete this model? This action cannot be undone.</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteConfirm({ open: false, modelId: null })}>
              Cancel
            </Button>
            <Button 
              onClick={() => deleteConfirm.modelId && handleDeleteModel(deleteConfirm.modelId)}
              color="error"
              variant="contained"
            >
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Feedback Detail Dialog */}
        <Dialog
          open={feedbackDialog.open}
          onClose={() => setFeedbackDialog({ open: false, feedback: null })}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Feedback Details</DialogTitle>
          <DialogContent>
            {feedbackDialog.feedback && (
              <Box>                <Typography variant="subtitle2" gutterBottom>
                  Request ID: {feedbackDialog.feedback.requestId}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                  User ID: {feedbackDialog.feedback.userId}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                  Date: {new Date(feedbackDialog.feedback.createdAt).toLocaleString()}
                </Typography>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                  Feedback:
                </Typography>
                <Typography variant="body1" sx={{ 
                  p: 2, 
                  bgcolor: 'grey.50', 
                  borderRadius: 1,
                  whiteSpace: 'pre-wrap',
                  color: 'black'
                }}>
                  {feedbackDialog.feedback.feedback}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFeedbackDialog({ open: false, feedback: null })}>
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </MotionWrapper>
  );
};