import 'leaflet/dist/leaflet.css';
import { Box, Checkbox, CircularProgress, Grid, Stack, TextField, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';

import { BackButton } from '../common/BackButton';
import { PrepareMap } from './PrepareMap';
import { OsmLocation, useOsmSearch } from '../hooks';
import { useCity } from '../providers/city-provider';
import { LatLngTuple } from 'leaflet';

export const PreparePage = () => {
  const { city, interestPoints, setInterestPoints, startPoints, setStartPoints } = useCity();

  const { register, watch } = useForm();

  const search = watch('locationSearch') as string;

  const { data: locations, isLoading: isLoadingLocations } = useOsmSearch(search, { viewBox: city.boundingbox });

  const markLocationOnChange = (event: React.ChangeEvent<HTMLInputElement>, location: OsmLocation, setMethod: React.Dispatch<React.SetStateAction<OsmLocation[]>>) => {
    const isChecked = event.target.checked;

    if (isChecked) {
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
                    <Checkbox onChange={(event) => markLocationOnChange(event, x, setInterestPoints) } />
                    <Checkbox onChange={(event) => markLocationOnChange(event, x, setStartPoints) } />
                    <Typography>{ x.display_name }</Typography>
                  </Box>
                ) :
                  <Typography>Seems like nothing like this exist</Typography>
            )
            
      }         
      <PrepareMap city={city} markers={interestPoints.map(x => [x.lat, x.lon] as LatLngTuple).concat(startPoints.map(x => [x.lat, x.lon]))} />
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