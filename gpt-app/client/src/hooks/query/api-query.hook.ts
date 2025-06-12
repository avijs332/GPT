import { FetchOptions, useServerGet } from "./base-query.hook"

export const useApiGet = <TResponse>(url: string, options: FetchOptions = {}) => {
  const response = useServerGet<TResponse>(`api/${url}`, options);

  return response;
};