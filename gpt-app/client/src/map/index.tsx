import 'leaflet/dist/leaflet.css';
import { CircularProgress } from '@mui/material';
import { useSearchParams } from 'react-router-dom';

import { useRoutes } from './route.hook';
import { MapContainer } from './MapContainer';
import { BackButton } from '../common/BackButton';

const BusRouteMap = () => {  
  const [searchParams] = useSearchParams() 
  const { data, isLoading, error } = useRoutes(
    searchParams.get('cityName') as string, 
    Number(searchParams.get('busCount'))
  );
  
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
      <BackButton route='/' />
    </div>
  );
};

export default BusRouteMap;