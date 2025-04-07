import { createContext, PropsWithChildren, useContext, useState } from "react";

import { OsmLocation } from '../hooks';

interface CityContext {
  city: OsmLocation;
  busCount: number;
  setCity: (city: OsmLocation) => void;
  setBusCount: (count: number) => void;
  interestPoints: Array<OsmLocation>;
  setInterestPoints: React.Dispatch<React.SetStateAction<OsmLocation[]>>
  centralPoints: Array<OsmLocation>;
  setCentralPoints: React.Dispatch<React.SetStateAction<OsmLocation[]>>;
  reset: () => void;
};

const cityContext = createContext<CityContext>({} as CityContext);

export const CityProvider = ({ children }: PropsWithChildren) => {
  const [city, setCity] = useState<OsmLocation>({} as OsmLocation);
  const [busCount, setBusCount] = useState(0);
  const [interestPoints, setInterestPoints] = useState<Array<OsmLocation>>([]);
  const [centralPoints, setCentralPoints] = useState<Array<OsmLocation>>([]);

  const reset = () => {
    setBusCount(0);
    setCity({} as OsmLocation);
    setInterestPoints([]);
    setCentralPoints([]);
  }

  return (
    <cityContext.Provider value={{ city, setCity, busCount, setBusCount, interestPoints, setInterestPoints, centralPoints, setCentralPoints, reset }}>
      { children }
    </cityContext.Provider>
  );
};

export const useCity = () => useContext(cityContext);