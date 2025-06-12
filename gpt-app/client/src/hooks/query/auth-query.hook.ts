import axios from "axios";
import { useMutation } from "@tanstack/react-query";

export const useAuthMutation = <TResponse, TBody>(url: 'login' | 'register', onSuccess: (user: TResponse) => void) => {
  const response = useMutation({
    mutationFn: (body: TBody) => 
      axios.post(`${import.meta.env.VITE_SERVER_ADDRESS}/auth/${url}`, body)
        .then((res) => res.data as TResponse) ,
    onSuccess    
  });

  return response;
};