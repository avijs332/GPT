import React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';

import { useApiGet } from '../hooks';
import { Request } from '../common/types';
import { MotionWrapper } from '../common';

interface RequestsApiResult {
  success: boolean;
  data: Request[];
};

export const AdminPage: React.FC = () => {
  const { data, isLoading } = useApiGet<RequestsApiResult>(`requests/open`, { extraKeys: ['open'] });  
  const navigate = useNavigate();

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', marginTop: 40 }}><CircularProgress /></div>;

  return (
    <MotionWrapper shouldPad={false} shouldSpread={true}>
      <div style={{ padding: 32 }}>
        <Typography variant="h4" gutterBottom>Open Requests</Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created At</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.data && data.data.map(req => (
                <TableRow key={req.id} hover style={{ cursor: 'pointer' }} onClick={() => navigate(`/admin/requests/${req.id}`)}>
                  <TableCell>{req.id}</TableCell>
                  <TableCell>{req.city.name}</TableCell>
                  <TableCell>{req.status}</TableCell>
                  <TableCell>
                    {new Date(req.createdAt).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'numeric',
                      day: 'numeric'
                    })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    </MotionWrapper>
  );
};