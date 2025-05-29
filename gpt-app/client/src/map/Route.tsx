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

// @ts-ignore TODO: fix later
const createBusStopIcon = (color: string) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="50" height="60" viewBox="0 0 50 60">
      <!-- Marker Shape -->
      <path d="M10 8 Q25 -5 40 8 V35 Q40 42 25 55 Q10 42 10 35 Z" fill="${color}" stroke="white" stroke-width="3"/>
    
      <!-- Windows -->
      <rect x="15" y="12" width="20" height="10" rx="3" ry="3" fill="white"/>
      <line x1="25" y1="12" x2="25" y2="22" stroke="${color}" stroke-width="2"/>
    
      <!-- Headlights -->
      <circle cx="15" cy="34" r="3" fill="yellow"/>
      <circle cx="35" cy="34" r="3" fill="yellow"/>
    
      <!-- Wheels -->
      <circle cx="18" cy="42" r="4" fill="black" stroke="white" stroke-width="2"/>
      <circle cx="32" cy="42" r="4" fill="black" stroke="white" stroke-width="2"/>
    </svg>
  `;
  
  return new L.Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svg)}`,
    iconSize: [40, 50],
    iconAnchor: [20, 50],
    popupAnchor: [0, -40]
  });
};

// @ts-ignore TODO: fix later
export const Route: FC<{route: BusRoute, stops: BusRoute}> = ({ route, stops }) => {
  const [color] = useState(getRandomColor());
  console.log(route[5])
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

      {/* { 
        stops.map(stop => (
          <Marker key={stop.toString()} position={stop} icon={createBusStopIcon(color)}>
            <Popup>Stop</Popup>
          </Marker>
        ))
      } */}
    </>
  );
};