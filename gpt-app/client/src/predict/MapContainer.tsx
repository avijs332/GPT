import { FC, useState } from 'react';
import { MapContainer as LeafletMapContainer, TileLayer } from 'react-leaflet';

import { RouteHookReturnType } from './route.hook';
import { LatLngExpression } from 'leaflet';
import { Route } from './Route';
import { Box, Checkbox, List, ListItem, Typography } from '@mui/material';

const getRandomColor = () => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  
  return color;
}

export const MapContainer: FC<{ data: RouteHookReturnType }> = ({ data }) => {
  const center: LatLngExpression = data.city;
  const [shouldShowRoutes, setShouldShowRoutes] = useState(Object.keys(data).filter(x => x !== 'city').map(() => true));

  const [colors] = useState(Object.keys(data)
    .filter(x => x !== 'city').filter(((_,index) => shouldShowRoutes[index]))
    .map(getRandomColor))


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
          Object.keys(data)
            .filter(x => x !== 'city').filter(((_,index) => shouldShowRoutes[index]))
            .map((x, index) => <Route color={colors[index]} key={x} route={data[x].route} stops={data[x].stops} />)
        }
      </LeafletMapContainer>
      <Box height='200px'>
        <List>
          {
            Object.keys(data).filter(x => x !== 'city').map((_, index) =>
              <ListItem>
                <Checkbox sx={{
                    color: colors[index],
                    '&.Mui-checked': {
                      color: colors[index],
                    },
                  }} checked={shouldShowRoutes[index]} onClick={() => setShouldShowRoutes(prev => prev.map((shouldShow, prevIndex) => index === prevIndex ? !shouldShow : shouldShow))} />
                <Typography>Bus Lane {index + 1}</Typography>
              </ListItem>
            )
          }
        </List>
      </Box>
    </div>
  );
};
