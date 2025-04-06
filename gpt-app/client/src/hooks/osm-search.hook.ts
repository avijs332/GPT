import { useQuery } from "@tanstack/react-query"
import axios from "axios";
export interface OsmLocation {
  place_id: number;
  licence: string;
  osm_type: string;
  osm_id: string;
  lat: number;
  lon: number;
  class: string;
  type: string;
  place_rank: number;
  importance: number;
  addresstype: string;
  name: string;
  display_name: string;
  boundingbox: [number, number, number, number];
};

interface HookOptions {
  viewBox?: [number, number, number, number]
};

export const useOsmSearch = (search: string, options?: HookOptions) => {
  const response = useQuery<Array<OsmLocation>>({
    queryKey: [search],
    refetchInterval: Infinity,
    enabled: !!search,
    queryFn: () => (
      axios.get(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(search)}&format=json${options?.viewBox ? `&viewbox=${options.viewBox[2]},${options.viewBox[0]},${options.viewBox[3]},${options.viewBox[1]}&bounded=1` : ''}`)
    ).then(x => x.data)
  });

  return response;
};