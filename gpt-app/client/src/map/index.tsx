import 'leaflet/dist/leaflet.css';
import { CircularProgress } from '@mui/material';

import { useRoutes } from './route.hook';
import { MapContainer } from './MapContainer';
import { BackButton } from '../common/BackButton';
import { useCity } from '../providers/city-provider';

const BusRouteMap = () => {  
  const { city, busCount, interestPoints, startPoints } = useCity();

  const { data, isLoading, error } = useRoutes(
    city.name, busCount, interestPoints, startPoints
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