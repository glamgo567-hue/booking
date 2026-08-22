import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

function initials(username: string): string {
  const parts = username.split(/[.\s_-]+/).filter(Boolean);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return username.slice(0, 2).toUpperCase();
}

function navClass({ isActive }: { isActive: boolean }): string {
  return isActive ? "nav__link nav__link--active" : "nav__link";
}

export function AppLayout() {
  const { user, isManager, signOut } = useAuth();

  return (
    <>
      <header className="topbar">
        <div className="topbar__left">
          <NavLink to="/" className="wordmark">
            <span className="wordmark__mark" />
            <span className="wordmark__text">БРОНЬ</span>
          </NavLink>
          <nav className="nav">
            <NavLink to="/" end className={navClass}>
              Мои брони
            </NavLink>
            <NavLink to="/desks" className={navClass}>
              Столы
            </NavLink>
            <NavLink to="/rooms" className={navClass}>
              Переговорки
            </NavLink>
            {isManager ? (
              <NavLink to="/admin" className={navClass}>
                Админка
              </NavLink>
            ) : null}
          </nav>
        </div>

        <div className="topbar__right">
          {isManager ? <span className="role-chip">офис-менеджер</span> : null}
          {user ? (
            <div className="user-chip">
              <span className="avatar">{initials(user.username)}</span>
              <span>{user.username}</span>
            </div>
          ) : null}
          <button type="button" className="btn btn--ghost btn--sm" onClick={signOut}>
            Выйти
          </button>
        </div>
      </header>

      <Outlet />
    </>
  );
}
