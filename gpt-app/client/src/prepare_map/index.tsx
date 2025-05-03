import 'leaflet/dist/leaflet.css';
import { Box, Checkbox, CircularProgress, Grid, Stack, TextField, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { LatLngTuple } from 'leaflet';

import { BackButton } from '../common/BackButton';
import { PrepareMap } from './PrepareMap';
import { OsmLocation, useOsmSearch } from '../hooks';
import { useCity } from '../providers/city-provider';
import { PointsList } from './PointsList';
import { Button } from '../common/Button';
import { useEffect } from 'react';

export const PreparePage = () => {
  const { city, interestPoints, setInterestPoints, centralPoints, setCentralPoints } = useCity();
  const navigate = useNavigate();

  const { register, watch } = useForm();

  const search = watch('locationSearch') as string;

  // let search = '';
  // const [searchValue, setSearchValue] = 

  // useEffect(() => {
  //   search = watch('locationSearch') as string;
  // }, [])

  // useEffect(() => {
  //   const handler = setTimeout(() => {
  //     search = watch('locationSearch') as string;
  //   }, 500);

  //   return () => {
  //     clearTimeout(handler);
  //   };
  // }, [search, 500]);

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

  return (
    <Stack>
      <TextField {...register('locationSearch')} />
      {
        isLoadingLocations ?
          <CircularProgress /> :
            search &&
            (
              (locations && locations.length) ?
                locations.map(x => 
                  <Box display='flex' key={x.osm_id}>
                    <Checkbox 
                      defaultChecked={!!interestPoints.find(point => x.osm_id === point.osm_id)} 
                      onChange={(event) => markLocationOnChange(event, x, setInterestPoints, point => point.grade = 1) } />
                    <Checkbox 
                      defaultChecked={!!centralPoints.find(point => x.osm_id === point.osm_id)} 
                      onChange={(event) => markLocationOnChange(event, x, setCentralPoints) } />
                    <Typography>{ x.display_name }</Typography>
                  </Box>
                ) :
                  <Typography>Seems like nothing like this exist</Typography>
            )
            
      }         
      <PrepareMap city={city} markers={interestPoints.map(x => [x.lat, x.lon] as LatLngTuple).concat(centralPoints.map(x => [x.lat, x.lon]))} />
      <PointsList />
      <Grid container flex={1}>
        <Box flex={1} height='100%'>
          <BackButton fullWidth />
        </Box>
        <Box flex={1} height='100%'>
          <Button fullWidth label='Submit' onClick={() => {navigate(`/map`)}} />
        </Box>
      </Grid>
    </Stack>
  );
};