import 'leaflet/dist/leaflet.css';
import { useState } from 'react';
import { useSearchParams } from "react-router-dom";
import { Box, Checkbox, CircularProgress, Grid, Stack, TextField, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';

import { BackButton } from '../common/BackButton';
import { PrepareMap } from './PrepareMap';
import { OsmLocation, useOsmSearch } from '../hooks';

export const PreparePage = () => {
  const [searchParams] = useSearchParams() 
  const { data: city, isLoading: isLoadingCity } = useOsmSearch(searchParams.get('cityName') as string)
  const [chosenLocation, setChosenLocations] = useState<Array<OsmLocation>>([]);

  const { register, watch } = useForm();

  const search = watch('locationSearch') as string;

  const { data: locations, isLoading: isLoadingLocations } = useOsmSearch(search);

  const markLocationOnChange = (event: React.ChangeEvent<HTMLInputElement>, location: OsmLocation) => {
    const isChecked = event.target.checked;

    if (isChecked) {
      setChosenLocations(prev => [...prev, location])
    } else {
      setChosenLocations(prev => prev.filter(x => x.osm_id !== location.osm_id))
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
                  <Box display='flex'>
                    <Checkbox onChange={(event) => markLocationOnChange(event, x) } />
                    <Typography>{ x.display_name }</Typography>
                  </Box>
                ) :
                  <Typography>Seems like nothing like this exist</Typography>
            )
            
      }
      {
        isLoadingCity ? 
          <CircularProgress /> :
          city && city.length ?
            <PrepareMap city={city[0]} markers={chosenLocation.map(x => [x.lat, x.lon])} /> :
            <Typography>Something went wrong</Typography>
      }
      <Grid container flex={1}>
        <Box flex={1} height='100%'>
          <BackButton route='/' fullWidth />
        </Box>
        <Box flex={1} height='100%'>
          <BackButton fullWidth label='Submit' route={`/map?cityName=${'a'}&busCount=${1}`} />
        </Box>
      </Grid>
    </Stack>
  );
};