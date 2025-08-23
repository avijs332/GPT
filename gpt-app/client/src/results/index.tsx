import { useParams } from 'react-router-dom';
import { CircularProgress, Typography, Paper, Stack, Box, Divider } from '@mui/material';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import { useEffect, useState } from 'react';
import { MotionWrapper } from '../common';
import { useApiGet } from '../hooks';
import { useLayout } from '../layout';
import L from 'leaflet';

// Helper to convert API points to Leaflet LatLng
const toLatLng = (arr: {lat: number, lng: number}[]) => arr.map(({ lat, lng }) => [lat, lng] as [number, number]);

export type ResultApiResponse = {
  id: string,
  city: {lat: number, lng: number}, 
  lanes: Record<string, {
    stops: Array<{lat: number, lng: number}>;
    route: Array<{lat: number, lng: number}>
  }>,
  createdAt: Date,
};

export const ResultPage = () => {
  const { id } = useParams();
  const { spread, unSpread } = useLayout();
  const [visibleLanes, setVisibleLanes] = useState<Record<string, boolean>>({});

  const { data: dataFull, isLoading, error } = useApiGet<{
    Sucess: boolean;
    data: ResultApiResponse
    }>(`results/${id}`, { extraKeys: [id] });

  useEffect(() => {
    spread();
    // Initialize all lanes as visible when data loads
    if (dataFull && dataFull.data && dataFull.data.lanes) {
      const initial: Record<string, boolean> = {};
      Object.keys(dataFull.data.lanes).forEach(laneId => {
        initial[laneId] = true;
      });
      setVisibleLanes(initial);
    }
    return () => {
      unSpread();
    };
  }, [dataFull]);

  if (isLoading) return <MotionWrapper shouldPad={true} shouldSpread={false}><CircularProgress /></MotionWrapper>;
  if (error) return <MotionWrapper shouldPad={true} shouldSpread={false}><Typography color="error">Error loading result.</Typography></MotionWrapper>;
  if (!dataFull) return <MotionWrapper shouldPad={true} shouldSpread={false}><Typography>No data found.</Typography></MotionWrapper>;

  const data: ResultApiResponse = dataFull.data;

  const { city, lanes } = data;
  const cityLatLng = [city.lat, city.lng] as [number, number];

  return (
    <MotionWrapper shouldPad={false} shouldSpread={true}>
      <Stack alignItems="center" justifyContent="center">
        <Paper elevation={8} sx={{ borderRadius: 4, px: { xs: 2, sm: 6 }, py: { xs: 3, sm: 5 }, width: '100%', textAlign: 'center' }}>
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>
            Route Result
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
          </Box>
          <Box sx={{ width: '100%', height: 500, mb: 3, borderRadius: 3, overflow: 'hidden' }}>
            <MapContainer center={cityLatLng} zoom={13} style={{ width: '100%', height: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {Object.entries(lanes).map(([laneId, lane], idx) => (
                visibleLanes[laneId] && (
                  <>
                    <Polyline key={laneId} positions={toLatLng(lane.route)} color={['#3182ce', '#38a169', '#805ad5', '#e53e3e'][idx % 4]} weight={5} />
                    {/* Start marker */}
                    {lane.route.length > 0 && (
                      <Marker 
                        key={laneId + '-start'}
                        position={[lane.route[0].lat, lane.route[0].lng]}
                        icon={L.divIcon({
                          className: '',
                          html: `<div style="background:#fff;border:2px solid #43a047;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;"><span style='font-size:13px;font-weight:bold;color:#43a047;'>S</span></div>`
                        })}
                      >
                        <Popup>Start of Lane {laneId}</Popup>
                      </Marker>
                    )}
                    {/* End marker */}
                    {lane.route.length > 0 && (
                      <Marker 
                        key={laneId + '-end'}
                        position={[lane.route[lane.route.length-1].lat, lane.route[lane.route.length-1].lng]}
                        icon={L.divIcon({
                          className: '',
                          html: `<div style="background:#fff;border:2px solid #d32f2f;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;"><span style='font-size:13px;font-weight:bold;color:#d32f2f;'>E</span></div>`
                        })}
                      >
                        <Popup>End of Lane {laneId}</Popup>
                      </Marker>
                    )}
                    {/* Stops */}
                    {lane.stops.map((stop, i) => (
                      <Marker 
                        key={laneId + '-stop-' + i} 
                        position={[stop.lat, stop.lng]}
                        icon={L.divIcon({
                          className: '',
                          html: `<div style="background:#fff;border:2px solid ${['#3182ce', '#38a169', '#805ad5', '#e53e3e'][idx % 4]};border-radius:50%;width:18px;height:18px;display:flex;align-items:center;justify-content:center;"><span style='display:block;width:8px;height:8px;background:${['#3182ce', '#38a169', '#805ad5', '#e53e3e'][idx % 4]};border-radius:50%'></span></div>`
                        })}
                      >
                        <Popup>Stop {i + 1} (Lane {laneId})</Popup>
                      </Marker>
                    ))}
                  </>
                )
              ))}
            </MapContainer>
          </Box>
          <Typography variant="h6" gutterBottom>Bus Lanes</Typography>
          <Stack direction="row" spacing={2} justifyContent="center" flexWrap="wrap">
            {Object.entries(lanes).map(([laneId, lane]) => {
              return (
                <Paper key={laneId} variant="outlined" sx={{
                  p: 1.5,
                  borderRadius: 2,
                  background: '#232946',
                  position: 'relative',
                  minWidth: 140,
                  maxWidth: 180,
                  width: '100%',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <Typography fontWeight={600} color="primary.main">Lane {laneId.replace('lane_', '')}</Typography>
                    <Box component="button"
                      onClick={() => setVisibleLanes(v => ({ ...v, [laneId]: !v[laneId] }))
                      }
                      sx={{
                        backgroundColor: visibleLanes[laneId] ? 'primary.main' : 'grey.700',
                        color: 'white',
                        border: 'none',
                        borderRadius: 2,
                        px: 1.5,
                        py: 0.5,
                        cursor: 'pointer',
                        fontWeight: 600,
                        fontSize: '0.85rem',
                        ml: 1,
                        transition: 'background 0.2s',
                      }}
                    >
                      {visibleLanes[laneId] ? 'Hide' : 'Show'}
                    </Box>
                  </Box>
                  <Typography color="text.secondary" fontSize={13}>Stops: {lane.stops.length}</Typography>
                </Paper>
              );
            })}
          </Stack>
        </Paper>
      </Stack>
    </MotionWrapper>
  );
};
