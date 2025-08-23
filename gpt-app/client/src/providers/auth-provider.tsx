import { createContext, PropsWithChildren, useContext, useEffect, useState } from "react";
import { UseMutationResult } from "@tanstack/react-query";

import { useToken } from "./token-provider";
import { useAuthMutation, useServerGet } from "../hooks";

interface User {
  id: string;
  name: string;
  username: string;
  email: string;
  joinedAt: Date;
};

interface LoginBody {
  username: string;
  password: string;
};


interface AuthResponse {
  user: User;
  token: string;
};

interface RegisterBody extends Omit<User, 'id' | 'joinedAt'> {
  password: string;
};

interface AuthReturn {
  user: User | null;
  isLoading: boolean;
};

interface IAuthContext {
  user: User;
  login: (username: string, password: string) => AuthReturn;
  loginState: UseMutationResult<AuthResponse, Error, LoginBody, unknown>;
  register: (body: RegisterBody) => AuthReturn;
  registerState: UseMutationResult<AuthResponse, Error, RegisterBody, unknown>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isMeLoading: boolean;
  isErrorOnAuth?: boolean;
};

const AuthContext = createContext<IAuthContext>({} as IAuthContext);

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [user, setUser] = useState<User | null>(null);
  const { getToken, setToken, removeToken } = useToken();

  const meResponse = useServerGet<User>('auth/me', { enabled: getToken() !== null && user === null });
  const loginState = useAuthMutation<AuthResponse, LoginBody>('login', ({ user, token }) => {
    setUser(user);
    setToken(token);
  });

  const registerState = useAuthMutation<AuthResponse, RegisterBody>('register', ({ user, token }) => {
    setUser(user);
    setToken(token);
  });

  const handleAuth = (response: UseMutationResult<AuthResponse, Error, any, unknown>) => {
    return {
      user: response.data?.user || null,
      isLoading: response.isPending,
    };
  };

  const login = (username: string, password: string) => {
    loginState.mutate({ username, password });

    return handleAuth(loginState);
  }

  const register = (body: RegisterBody) => {
    registerState.mutate(body);

    return handleAuth(registerState);
  };

  const logout = () => {
    setUser(null);
    removeToken();
  };

  const isAuthenticated = user !== null;
  const isAdmin = user?.username === 'admin';

  useEffect(() => {
    if (meResponse.isSuccess && meResponse.data) {
      setUser(meResponse.data);
    } else if (meResponse.isError) {
      setUser(null);
      removeToken();
    };
  }, [meResponse.isLoading]);

  return (
    <AuthContext.Provider value={{ 
      //@ts-ignore
      user, 
      login,
      loginState,
      register, 
      registerState,
      logout, 
      isAuthenticated,
      isAdmin, 
      isMeLoading: meResponse.isLoading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext<IAuthContext>(AuthContext);