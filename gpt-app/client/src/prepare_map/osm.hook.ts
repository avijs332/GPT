import { useQuery } from "@tanstack/react-query"
import axios from "axios";

export const useOsmCity = (cityName: string) => {
  const response = useQuery({
    queryKey: [cityName],
    refetchInterval: Infinity,
    queryFn: () => (
      axios.get(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(cityName)}&format=json`)
    ).then(x => x.data[0])
  });

  return response;
};