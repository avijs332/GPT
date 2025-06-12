import axios from "axios";
import { useQuery } from "@tanstack/react-query";

import { useToken } from "../../providers/token-provider";

export interface FetchOptions {
  refetchInterval?: number;
  enabled?: boolean;
  extraKeys?: any[];
};

export const useGet = <TResponse>(url: string, options: FetchOptions = {}) => {
  const { getToken } = useToken();

  const response = useQuery({
    queryKey: [url, ...options.extraKeys ?? []],
    refetchInterval: options.refetchInterval ?? Infinity,
    enabled: options.enabled ?? true,
    queryFn: async () =>
      await axios.get(url, { headers: { Authorization: `Bearer ${getToken()}` } })
        .then((res) => res.data as TResponse),
  });

  return response;
};

export const useServerGet = <TResponse>(url: string, options: FetchOptions = {}) => {
  return useGet<TResponse>(`${import.meta.env.VITE_SERVER_ADDRESS}/${url}`, options);
};