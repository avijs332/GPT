import React, { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import { useParams } from 'react-router-dom';

import { useToken } from '../providers/token-provider';
import { MotionWrapper } from '../common';

export const AdminUploadPage = () => {
  const { requestId } = useParams<{ requestId: string }>();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const { getToken } = useToken();

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
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/admin/upload-model/`, formData,
      {  
        headers: {
          Authorization: `Bearer ${getToken()}`,
        }
      });
      const data = response.data
      setResult(data.doc_id ? `Upload successful! Doc ID: ${data.doc_id}` : 'Upload failed.');
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
      // Optionally navigate or refresh
      // navigate(`/requests/${requestId}`);
    } catch (err) {
      setResult('Failed to mark request as complete.');
    }
  };

  return (
    <MotionWrapper shouldSpread={false} shouldPad={false}>
      <Box sx={{ color: 'black', maxWidth: 400, margin: '40px auto', padding: 3, borderRadius: 2, boxShadow: 2, background: '#fff' }}>
        <Typography variant="h5" gutterBottom>Admin Model Upload</Typography>
        <Box component="form" onSubmit={handleUpload}>
          <Button
            variant="contained"
            component="label"
            sx={{ width: '100%', mb: 2 }}
          >
            Select Model File
            <input type="file" accept=".h5" hidden onChange={handleFileChange} />
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
        <Button
          variant="outlined"
          color="success"
          sx={{ width: '100%', mb: 2 }}
          onClick={handleMarkComplete}
          disabled={!requestId || uploading}
        >
          Mark Request as Complete
        </Button>
        {result && <Typography sx={{ mt: 2 }}>{result}</Typography>}
      </Box>
    </MotionWrapper>
  );
};