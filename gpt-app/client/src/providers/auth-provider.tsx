import axios from "axios";
import { createContext, PropsWithChildren, useContext, useEffect, useState } from "react";
import { UseQueryResult } from "@tanstack/react-query";

import { useToken } from "./token-provider";
import { useAuthQuery, useGet, useServerGet } from "../hooks";

interface User {
  id: string;
  name: string;
  email: string;
};

interface LoginBody {
  username: string;
  password: string;
};

interface AuthResponse {
  user: User;
  token: string;
}

interface RegisterBody extends User {
  password: string;
};

interface AuthReturn {
  user: User | null;
  isLoading: boolean;
};

interface IAuthContext {
  user: User | null;
  login: (username: string, password: string) => Promise<AuthReturn>;
  register: (body: RegisterBody) => Promise<AuthReturn>;
  logout: () => void;
  isAuthenticated: () => boolean;
  isMeLoading: boolean;
  isErrorOnAuth?: boolean;
};

const AuthContext = createContext<IAuthContext>({} as IAuthContext);

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [user, setUser] = useState<User | null>(null);
  const { getToken, setToken, removeToken } = useToken();

  const meResponse = useServerGet<User>('auth/me', { enabled: getToken() !== null && user === null });

  const handleAuth = (response: UseQueryResult<AuthResponse, Error>) => {
    if (response.isSuccess && response.data) {
      setUser(response.data.user);
      setToken(response.data.token);
    };

    return {
      user: response.data?.user || null,
      isLoading: response.isLoading,
    };
  };

  const login = async (username: string, password: string) => {
    const response = useAuthQuery<AuthResponse, LoginBody>('login', { username, password });

    return handleAuth(response);
  }

  const register = async (body: RegisterBody) => {
    const response = useAuthQuery<AuthResponse, RegisterBody>('login', body);

    return handleAuth(response);
  };

  const logout = () => {
    setUser(null);
    removeToken();
  };

  const isAuthenticated = () => {
    return user !== null;
  };

  useEffect(() => {
    if (meResponse.isSuccess && meResponse.data) {
      setUser(meResponse.data);
    }
  }, [meResponse.isLoading]);

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      register, 
      logout, 
      isAuthenticated, 
      isMeLoading: meResponse.isLoading, 
      isErrorOnAuth: meResponse.isError }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext<IAuthContext>(AuthContext);