import { createContext, PropsWithChildren, useContext, useState } from "react";

import { OsmLocation } from '../hooks';

interface CityContext {
  city: OsmLocation;
  busCount: number;
  setCity: (city: OsmLocation) => void;
  setBusCount: (count: number) => void;
  interestPoints: Array<OsmLocation>;
  setInterestPoints: React.Dispatch<React.SetStateAction<OsmLocation[]>>
  startPoints: Array<OsmLocation>;
  setStartPoints: React.Dispatch<React.SetStateAction<OsmLocation[]>>
};

const cityContext = createContext<CityContext>({} as CityContext);

export const CityProvider = ({ children }: PropsWithChildren) => {
  const [city, setCity] = useState<OsmLocation>({} as OsmLocation);
  const [busCount, setBusCount] = useState(0);
  const [interestPoints, setInterestPoints] = useState<Array<OsmLocation>>([]);
  const [startPoints, setStartPoints] = useState<Array<OsmLocation>>([]);

  return (
    <cityContext.Provider value={{ city, setCity, busCount, setBusCount, interestPoints, setInterestPoints, startPoints, setStartPoints }}>
      { children }
    </cityContext.Provider>
  );
};

export const useCity = () => useContext(cityContext);