import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { OsmLocation } from '../hooks';
import { LatLngTuple } from "leaflet";
import { FC } from "react";

interface PrepareMapProps {
  city: OsmLocation;
  markers: Array<LatLngTuple>
};

export const PrepareMap: FC<PrepareMapProps> = ({ city, markers }) => {
  const center = [city.lat, city.lon] as LatLngTuple;
  
  return (
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
        {markers.map(position => (
            <Marker key={`${position[0]}, ${position[1]}`} position={position}>
                <Popup>Marker at {position[0]}, {position[1]}</Popup>
            </Marker>
        ))}

      </MapContainer>
    </div>
  )
};