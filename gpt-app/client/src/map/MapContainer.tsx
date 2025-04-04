import { FC } from 'react';
import { MapContainer as LeafletMapContainer, TileLayer } from 'react-leaflet';

import { RouteHookReturnType } from './route.hook';
import { LatLngExpression } from 'leaflet';
import { Route } from './Route';

export const MapContainer: FC<{ data: RouteHookReturnType }> = ({ data }) => {
  const center: LatLngExpression = data.city;
  
  return (
    <div style={{ height: '500px', width: '100%' }}>
      <LeafletMapContainer 
        center={center} 
        zoom={15} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {
          Object.keys(data).map(x => x !== 'city' ? <Route key={x} route={data[x].route} stops={data[x].stops} /> : '')
        }
      </LeafletMapContainer>
    </div>
  );
};
