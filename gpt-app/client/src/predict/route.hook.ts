import { useQuery } from "@tanstack/react-query";
import { LatLngExpression } from "leaflet";
import axios from 'axios';
import { OsmLocation } from "../hooks";
import { useToken } from "../providers/token-provider";

export type BusRoute = Array<LatLngExpression>;

// export const useRoutes = (cityName: String, startLocation: LatLngExpression, endLocation: LatLngExpression) => {
//   const response = useQuery<BusRoute>({
//     queryKey: [cityName, [startLocation, endLocation]],
//     queryFn: () => axios.post(
//       'http://localhost:8000/predict_route', 
//       JSON.stringify({ city_name: cityName, start_location: 'startLocation', end_location: 'endLocation' }),
//       {
//         headers:
//           {'Content-Type': 'application/json',}
//       }
//     )
//     .then(x => x.data.route)
//     .then((x: Array<{lat: number, lng: number}>) => x.map(point => [point.lat, point.lng] as LatLngExpression)),
//   });

//   return response;
// };
type ApiResponse = { 
  city: {lat: number, lng: number, name: string}, 
  lanes: Record<string, {
    stops: Array<{lat: number, lng: number}>;
    route: Array<{lat: number, lng: number}>
  }> 
};

export type RouteHookReturnType = { city: LatLngExpression } & Record<string, {
  stops: Array<LatLngExpression>;
  route: Array<LatLngExpression>;
}>;

export const useRoutes = (cityName: string, busCount: number, interestPoints: Array<OsmLocation>, centralPoints: Array<OsmLocation>) => {
  const { getToken } = useToken();
  const response = useQuery<RouteHookReturnType>({
    queryKey: [cityName, busCount, interestPoints, centralPoints],
    refetchInterval: Infinity,
    queryFn: () => axios.post(
      `${import.meta.env.VITE_SERVER_ADDRESS}/api/maps/predict`, 
      // 'http://localhost:8000/mock/predict_route', 
      JSON.stringify({ city_name: cityName, bus_count: busCount, interest_points: interestPoints, central_points: centralPoints }),
      {
        headers:
          {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`,
          }
      },
    )
    .then(x => x.data.data as ApiResponse)
    .then(data => {
      const returnData = {} as RouteHookReturnType;
      returnData.city = [data.city.lat, data.city.lng] as LatLngExpression

      Object.keys(data.lanes).forEach(key => {        
        returnData[key] = { route: [], stops: [] };
        returnData[key].route = data.lanes[key].route.map(point => [point.lat, point.lng] as LatLngExpression)
        returnData[key].stops = data.lanes[key].stops.map(point => [point.lat, point.lng] as LatLngExpression)
      })

      return returnData;
    }),
  });

  return response;
};