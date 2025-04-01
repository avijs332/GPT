import { FC, useState } from "react";
import { Polyline, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

import { BusRoute } from './route.hook'

const getRandomColor = () => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  
  return color;
}

const createSvgIcon = (color: string) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="45" viewBox="0 0 30 45">
      <defs>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.5"/>
        </filter>
      </defs>
      <path fill="${color}" stroke="white" stroke-width="2" 
        d="M15,1 C22,1 29,8 29,15 C29,22 15,44 15,44 C15,44 1,22 1,15 C1,8 8,1 15,1 Z" 
        filter="url(#shadow)"/>
      <circle cx="15" cy="15" r="6" fill="white" stroke="black" stroke-width="2"/>
    </svg>
  `;

  return new L.Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svg)}`,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  });
};

const createBusStopIcon = (color: string) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="50" viewBox="0 0 40 50">
      <rect x="5" y="5" width="30" height="35" rx="5" ry="5" fill="${color}" stroke="white" stroke-width="3"/>
      <circle cx="20" cy="40" r="3" fill="black"/>
      <circle cx="30" cy="40" r="3" fill="black"/>
      <path d="M12,25 L28,25 M12,20 L28,20 M12,15 L28,15 M15,10 L25,10" stroke="white" stroke-width="2"/>
    </svg>
  `;

  return new L.Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svg)}`,
    iconSize: [40, 50],
    iconAnchor: [20, 50],
    popupAnchor: [0, -40]
  });
};

export const Route: FC<{route: BusRoute, stops: BusRoute}> = ({ route, stops }) => {
  const [color] = useState(getRandomColor());

  return (
    <>
      {route.length > 0 && (
        <Polyline 
          positions={route}
          color={color}
          weight={5}
          opacity={0.8}
        />
      )}
      
      {route.length > 0 && (
        <>
          <Marker position={route[0]} icon={createSvgIcon(color)}>
            <Popup>Start</Popup>
          </Marker>
          <Marker position={route[route.length - 1]} icon={createSvgIcon(color)}>
            <Popup>End</Popup>
          </Marker>
        </>
      )}

      { 
        stops.map(stop => (
          <Marker position={stop} icon={createBusStopIcon(color)}>
            <Popup>Stop</Popup>
          </Marker>
        ))
      }
    </>
  );
};