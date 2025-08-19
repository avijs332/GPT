import { createContext, PropsWithChildren, useContext } from "react";

interface ITokenContext {
  getToken: () => string | null;
  setToken: (token: string) => void;
  removeToken: () => void;
}

const TokenContext = createContext<ITokenContext>({} as ITokenContext);

export const TokenProvider = ({ children }: PropsWithChildren) => {
  const getToken = () => {
    const token = localStorage.getItem('token');
    if (!token) {
      return null;
    };
  
    return token;
  };

  const setToken = (token: string) => {
    localStorage.setItem('token', token);
  };

  const removeToken = () => {
    localStorage.removeItem('token');
  };

  return (
    <TokenContext.Provider value={{ getToken, setToken, removeToken }}>
      {children}
    </TokenContext.Provider>
  );
};

export const useToken = () => useContext(TokenContext);