import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { RequireAuth, RequireManager } from "./components/RouteGuards";
import { AdminPage } from "./pages/AdminPage";
import { DesksPage } from "./pages/DesksPage";
import { LoginPage } from "./pages/LoginPage";
import { MyBookingsPage } from "./pages/MyBookingsPage";
import { RegisterPage } from "./pages/RegisterPage";
import { RoomsPage } from "./pages/RoomsPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<MyBookingsPage />} />
          <Route path="desks" element={<DesksPage />} />
          <Route path="rooms" element={<RoomsPage />} />
          <Route element={<RequireManager />}>
            <Route path="admin" element={<AdminPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
