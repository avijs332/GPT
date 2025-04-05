import { createContext, PropsWithChildren, useContext } from "react";
import { OsmLocation } from '../hooks';

interface CityContext {
  city: OsmLocation
};

const cityContext = createContext<CityContext>({} as CityContext);

export const CityProvider = ({ city, children }: PropsWithChildren<{city: OsmLocation}>) => {
  return (
    <cityContext.Provider value={{ city }}>
      { children }
    </cityContext.Provider>
  );
};

export const useCity = () => useContext(cityContext);