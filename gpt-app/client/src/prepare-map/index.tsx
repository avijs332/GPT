import 'leaflet/dist/leaflet.css';
import { Box, Checkbox, CircularProgress, Divider, Grid, Stack, TextField, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { LatLngTuple } from 'leaflet';

import { BackButton } from '../common/BackButton';
import { PrepareMap } from './PrepareMap';
import { OsmLocation, useOsmSearch } from '../hooks';
import { useCity } from '../providers/city-provider';
import { PointsList } from './PointsList';
import { Button } from '../common/Button';
import { MotionWrapper } from '../common';
import { useCreateRequest } from '../hooks/query/create-request.hook';

export const PreparePage = () => {
  const { city, busCount, interestPoints, setInterestPoints, centralPoints, setCentralPoints } = useCity();
  const navigate = useNavigate();
  const { mutate: postRequest, isPending: isPosting } = useCreateRequest();

  const { register, watch } = useForm();

  const search = watch('locationSearch') as string;

  const { data: locations, isLoading: isLoadingLocations } = useOsmSearch(search, { viewBox: city.boundingbox });

  const markLocationOnChange = <T extends OsmLocation>(event: React.ChangeEvent<HTMLInputElement>, location: T, setMethod: React.Dispatch<React.SetStateAction<T[]>>, mutate?: (x:T) => void) => {
    const isChecked = event.target.checked;

    if (isChecked) {
      mutate?.(location);
      setMethod(prev => [...prev, location])
    } else {
      setMethod(prev => prev.filter(x => x.osm_id !== location.osm_id))
    }
  };

  const handleSubmit = () => {
    postRequest({
      city,
      busCount, // Replace with actual busCount if available
      interestPoints,
      centralPoints
    }, {
      onSuccess: () => {
        navigate('/thank-you');
      }
    });
  };

  return (
    <MotionWrapper shouldPad={true} shouldSpread={true}>
      <Stack>
        <Typography variant='h2'>Preparation Stage</Typography>
        <Divider sx={{ marginBottom: '10px' }} />
        <Box overflow='visible'>
          <PrepareMap 
            city={city} 
            interestPoints={interestPoints.map(x => [x.lat, x.lon] as LatLngTuple)}
            centralPoints={centralPoints.map(x => [x.lat, x.lon] as LatLngTuple)}
          />
        </Box>
        <TextField {...register('locationSearch')} />
        {
          isLoadingLocations ?
            <CircularProgress /> :
              search &&
              (
                (locations && locations.length) ?
                  locations.map(x => 
                    <Box key={x.osm_id} sx={{ mb: 2, p: 1.5, borderRadius: 2, boxShadow: 1, bgcolor: 'background.paper', minWidth: 0 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, wordBreak: 'break-word', color: 'primary.main', fontWeight: 500 }}>
                        {x.display_name}
                      </Typography>
                      <Box display="flex" gap={4} justifyContent="flex-start" sx={{ mt: 1 }}>
                        <Box display="flex" flexDirection="column" alignItems="center" sx={{ flex: 1 }}>
                          <Checkbox
                            size="medium"
                            sx={{
                              p: 0.5,
                              bgcolor: '#e3f2fd',
                              borderRadius: '12px',
                              boxShadow: 3,
                              border: '2px solid',
                              borderColor: '#90caf9',
                              transition: 'all 0.2s',
                              '&.Mui-checked': {
                                color: '#fff',
                                bgcolor: '#1976d2',
                                borderColor: '#1976d2',
                              },
                              '&:hover': {
                                bgcolor: '#bbdefb',
                              },
                            }}
                            icon={<Box sx={{ width: 22, height: 22, borderRadius: '8px', border: '2px solid #90caf9', bgcolor: '#e3f2fd' }} />}
                            checkedIcon={<Box sx={{ width: 22, height: 22, borderRadius: '8px', bgcolor: '#1976d2', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', border: '2px solid #1976d2' }}>
                              <svg width="16" height="16" viewBox="0 0 16 16"><polyline points="3,8 7,12 13,4" fill="none" stroke="#fff" strokeWidth="2"/></svg>
                            </Box>}
                            defaultChecked={!!interestPoints.find(point => x.osm_id === point.osm_id)}
                            // @ts-ignore TODO: fix later
                            onChange={(event) => markLocationOnChange(event, x, setInterestPoints, point => point.grade = 1) }
                            title="Mark as Interest Point (blue)"
                          />
                          <Typography variant="caption" sx={{ mt: 0.5, color: '#1976d2', fontWeight: 500 }}>Interest</Typography>
                        </Box>
                        <Box display="flex" flexDirection="column" alignItems="center" sx={{ flex: 1 }}>
                          <Checkbox
                            size="medium"
                            sx={{
                              p: 0.5,
                              bgcolor: '#fce4ec',
                              borderRadius: '12px',
                              boxShadow: 3,
                              border: '2px solid',
                              borderColor: '#f48fb1',
                              transition: 'all 0.2s',
                              '&.Mui-checked': {
                                color: '#fff',
                                bgcolor: '#d81b60',
                                borderColor: '#d81b60',
                              },
                              '&:hover': {
                                bgcolor: '#f8bbd0',
                              },
                            }}
                            icon={<Box sx={{ width: 22, height: 22, borderRadius: '8px', border: '2px solid #f48fb1', bgcolor: '#fce4ec' }} />}
                            checkedIcon={<Box sx={{ width: 22, height: 22, borderRadius: '8px', bgcolor: '#d81b60', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', border: '2px solid #d81b60' }}>
                              <svg width="16" height="16" viewBox="0 0 16 16"><polyline points="3,8 7,12 13,4" fill="none" stroke="#fff" strokeWidth="2"/></svg>
                            </Box>}
                            defaultChecked={!!centralPoints.find(point => x.osm_id === point.osm_id)}
                            onChange={(event) => markLocationOnChange(event, x, setCentralPoints) }
                            title="Mark as Central Station (red)"
                          />
                          <Typography variant="caption" sx={{ mt: 0.5, color: '#d81b60', fontWeight: 500 }}>Central</Typography>
                        </Box>
                      </Box>
                    </Box>
                  ) :
                  <Typography>Seems like nothing like this exist</Typography>
                )
                
        }         
        <PointsList />
        <Grid container flex={1}>
          <Box flex={1} height='100%'>
            <BackButton fullWidth />
          </Box>
          <Box flex={1} height='100%'>
            <Button fullWidth label='Submit' onClick={handleSubmit} disabled={isPosting} />
            {isPosting && <Box display="flex" justifyContent="center" mt={2}><CircularProgress /></Box>}
          </Box>
        </Grid>
      </Stack>
    </MotionWrapper>
  );
};