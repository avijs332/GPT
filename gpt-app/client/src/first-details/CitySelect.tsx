import { CircularProgress, List, ListItemButton, ListItemText } from "@mui/material";
import { FC } from "react";

import { OsmLocation, useOsmSearch } from "../hooks";
import { useCity } from "../providers/city-provider";

interface CitySelectProps {
  cityName: string;
};

export const CitySelect: FC<CitySelectProps> = ({ cityName }) => {
  const { data: cities, isLoading: isLoadingCities } = useOsmSearch(cityName);
  const { city, setCity } = useCity();

  const handleChooseCity = (chosenCity: OsmLocation) => {
    setCity(chosenCity);
  };

  return (
    <>
      {
        isLoadingCities ?
          <CircularProgress /> :
          cities &&
          <List component="nav">
            {cities.map(x => (
              <ListItemButton
                key={x.osm_id}
                selected={x.osm_id === city.osm_id}
                onClick={() => handleChooseCity(x)}
              >
                <ListItemText primary={x.display_name} />
              </ListItemButton>
            ))}
          </List>
      }
    </>
  );
};