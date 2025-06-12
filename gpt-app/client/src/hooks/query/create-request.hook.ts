import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { useToken } from '../../providers/token-provider';
import { useAuth } from '../../providers/auth-provider';

export type CreateRequestPayload = {
  city: any; // Replace 'any' with the actual city type if available
  busCount: number;
  interestPoints: any[]; // Replace 'any' with the actual type if available
  centralPoints: any[]; // Replace 'any' with the actual type if available
};

export const useCreateRequest = () => {
  const { getToken } = useToken();
  const { user } = useAuth();

  return useMutation({
    mutationFn: async (payload: CreateRequestPayload) => {
      const response = await axios.post(
        `${import.meta.env.VITE_SERVER_ADDRESS}/api/requests`,
         { ...payload, userId: user.id },
        {  
            headers: {
              Authorization: `Bearer ${getToken()}`,
          }
        });
      return response.data;
    },

  });
}
