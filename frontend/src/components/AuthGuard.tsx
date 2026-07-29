import { ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

export function AuthGuard({ children, fallback }: Props) {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0f1117' }}>
        <div className="auth-spinner" />
      </div>
    );
  }

  if (!token) {
    return <>{fallback}</> ?? null;
  }

  return <>{children}</>;
}
