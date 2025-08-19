import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { LatLngTuple } from "leaflet";
import { FC, useEffect } from "react";
import L from 'leaflet';

import { OsmLocation } from '../hooks';

interface PrepareMapProps {
  city: OsmLocation;
  interestPoints: Array<LatLngTuple>;
  centralPoints: Array<LatLngTuple>;
};

const MapRefresh = () => {
  const map = useMap();
  
  useEffect(() => {
    setTimeout(() => {
      map.invalidateSize();
    }, 1000);
  }, []);

  return null;
}

export const PrepareMap: FC<PrepareMapProps> = ({ city, interestPoints, centralPoints }) => {
  const center = [city.lat, city.lon] as LatLngTuple;
  
  return (
    <div style={{ height: '500px', width: '100%', overflow: 'visible' }}>
      <MapContainer
        center={center} 
        zoom={15} 
        style={{ height: '100%', width: '100%' }}
      >
        <MapRefresh />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {interestPoints.map(position => (
          <Marker key={`interest-${position[0]},${position[1]}`} position={position}
            icon={L.divIcon({
              className: '',
              html: `<div style="background:#e3f2fd;border:2px solid #1976d2;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;"><span style='font-size:13px;font-weight:bold;color:#1976d2;'>I</span></div>`
            })}
          >
            <Popup>Interest Point at {position[0]}, {position[1]}</Popup>
          </Marker>
        ))}
        {centralPoints.map(position => (
          <Marker key={`central-${position[0]},${position[1]}`} position={position}
            icon={L.divIcon({
              className: '',
              html: `<div style="background:#fce4ec;border:2px solid #d81b60;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;"><span style='font-size:13px;font-weight:bold;color:#d81b60;'>C</span></div>`
            })}
          >
            <Popup>Central Point at {position[0]}, {position[1]}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
};