import 'leaflet/dist/leaflet.css';
import { useState } from 'react';
import { useSearchParams } from "react-router-dom";
import { CircularProgress } from '@mui/material';
import { MapContainer, Marker, Popup, TileLayer, useMapEvents } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';

import { useOsmCity } from "./osm.hook";
import { BackButton } from '../common/BackButton';

export const PreparePage = () => {
  const [searchParams] = useSearchParams() 
  const { data, isLoading } = useOsmCity(searchParams.get('cityName') as string)
  const [markers, setMarkers] = useState<Array<LatLngExpression>>([]);

  function AddMarkerOnClick() {
      useMapEvents({
          click(e) {
              setMarkers([...markers, e.latlng]);
          },
      });
      return null;
  }

  const center = (!isLoading ? [data.lat, data.lon] : [-1, 1]) as LatLngExpression;

  return (
    <div className="bus-route-container">
      {
        isLoading ? 
          <CircularProgress /> :
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
              <AddMarkerOnClick />
              {markers.map((position, index) => (
                  <Marker key={index} position={position}>
                      <Popup>Marker at {position[0]}, {position[1]}</Popup>
                  </Marker>
              ))}

            </MapContainer>
          </div>
      }
      <BackButton route='/map' />
      <BackButton />
    </div>
  );
};