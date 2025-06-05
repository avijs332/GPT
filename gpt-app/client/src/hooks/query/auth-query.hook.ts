import axios from "axios";
import { useQuery } from "@tanstack/react-query";

import { FetchOptions } from "./base-query.hook";

export const useAuthQuery = <TResponse, TBody>(url: 'login' | 'register', body: TBody, options: FetchOptions = {}) => {
  const response = useQuery({
    queryKey: [url],
    refetchInterval: Infinity,
    refetchIntervalInBackground: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
    retry: 3,
    retryOnMount: false,
    enabled: options.enabled ?? true,
    queryFn: () =>
      axios.post(`${import.meta.env.VITE_SERVER_ADD}/auth/${url}`, body)
        .then((res) => res.data as TResponse),
  });

  return response;
};
