import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { debounce } from "@mui/material";

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
}

interface HookOptions {
  viewBox?: [number, number, number, number];
}

export const useOsmSearch = (search: string, options?: HookOptions) => {
  const [debouncedSearch, setDebouncedSearch] = useState(search);

  const debouncedSetSearch = useMemo(() => debounce(setDebouncedSearch, 500), []);

  useEffect(() => {
    debouncedSetSearch(search);
  }, [search, debouncedSetSearch]);

  const response = useQuery<Array<OsmLocation>>({
    queryKey: [debouncedSearch],
    refetchInterval: Infinity,
    enabled: !!debouncedSearch,
    queryFn: () =>
      axios
        .get(
          `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(debouncedSearch)}&format=json${
            options?.viewBox
              ? `&viewbox=${options.viewBox[2]},${options.viewBox[0]},${options.viewBox[3]},${options.viewBox[1]}&bounded=1`
              : ""
          }`
        )
        .then((x) => x.data),
  });

  return response;
};
