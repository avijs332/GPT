import 'leaflet/dist/leaflet.css';

import { useRoutes } from './route.hook';
import { MapContainer } from './MapContainer';
import { Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const BusRouteMap = () => {  
  const { data, isLoading, error } = useRoutes('Neve Tzedek, Tel Aviv, Israel', [1, 1], [-1, -1]);
  const navigate = useNavigate();

  const onClick = () => { navigate('/') };
  
  if (error) {
    console.error(error)
  };

  return (
    <div className="bus-route-container">
      <h2>Bus Route Map</h2>
      
      {isLoading && <p>Loading route data...</p>}
      {error && <p className="error">Error: {error.message}</p>}
      
      {
        isLoading ?
          <CircularProgress /> :
          (!error && data) && (
            <MapContainer data={data} />
          )
      }
      <Stack alignItems='center' bgcolor='rgb(70, 75, 178)' padding='20px'>
        <Button onClick={onClick}>
          <Typography>
            Go Back
          </Typography>
        </Button>
      </Stack>
    </div>
  );
};

export default BusRouteMap;