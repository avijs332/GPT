import { FC, PropsWithChildren } from 'react';
import { ErrorBoundary, FallbackProps } from 'react-error-boundary'; 
import { useNavigate } from 'react-router-dom';

export const ErrorBoundaryProvider = ({ children }: PropsWithChildren) => {
  const navigate = useNavigate();

  return (
    <ErrorBoundary 
      FallbackComponent={ErrorPage}
      onReset={() => navigate('/')}
    >
      {children}
    </ErrorBoundary>
  );
};

const ErrorPage: FC<FallbackProps> = ({ resetErrorBoundary }) => (
  <div role="alert" className="p-4 bg-red-100 text-red-700">
    <p>Something went wrong</p>
    <button onClick={resetErrorBoundary} className="mt-2 px-4 py-1 bg-red-500 text-white rounded">
      Try again
    </button>
  </div>
);