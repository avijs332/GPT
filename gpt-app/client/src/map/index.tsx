import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { LatLngExpression } from 'leaflet';

import { useRoutes } from './route.hook';
import { Route } from './Route';

const BusRouteMap = () => {  
  // Default center coordinates (will adjust when route is loaded)
  const defaultCenter: LatLngExpression = [37.7749, -122.4194]; // San Francisco

  const { data, isLoading, error } = useRoutes('Neve Tzedek, Tel Aviv, Israel', [1, 1], [-1, -1]);

  // Calculated center based on route or default
  const center: LatLngExpression = data ? data.city : defaultCenter;
  
  if (error) {
    console.error(error)
  };

  return (
    <div className="bus-route-container">
      <h2>Bus Route Map</h2>
      
      {isLoading && <p>Loading route data...</p>}
      {error && <p className="error">Error: {error.message}</p>}
      
      {(!isLoading && !error && data) && (
        <div style={{ height: '500px', width: '100%' }}>
          <MapContainer 
            center={center} 
            zoom={15} 
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {
              Object.keys(data).map(x => x !== 'city' ? <Route route={data[x].route} stops={data[x].stops} /> : '')
            }
          </MapContainer>
        </div>
      )}
    </div>
  );
};

export default BusRouteMap;