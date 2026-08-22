import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export function RequireAuth() {
  const { token, user, isLoading } = useAuth();
  const location = useLocation();

  if (token === null) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (isLoading) {
    return <div className="empty">Загрузка…</div>;
  }

  if (user === null) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export function RequireManager() {
  const { isManager } = useAuth();

  if (!isManager) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
