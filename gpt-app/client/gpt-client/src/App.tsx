import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { Suspense } from 'react';

import { QueryContext } from './contexts/query';

export const App = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['generate_routes'],
    queryFn: () => axios.post('http://127.0.0.1:8080/generate_routes').then(x => x.data)
  });
  
  return (
    <QueryContext>
      {/* // <Suspense fallback='Shit'>
      //   {data}
      // </Suspense> */}
      <>
        {
          isLoading ? { shit: 1 } : data
        }
      </>
    </QueryContext>
  )
};