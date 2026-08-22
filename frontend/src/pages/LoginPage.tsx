import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/useAuth";
import { AuthBrand } from "../components/AuthBrand";

export function LoginPage() {
  const { token, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (token !== null) {
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      await signIn(username.trim(), password);
      navigate(from, { replace: true });
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "Не удалось войти");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="auth">
      <AuthBrand />

      <div className="auth__side">
        <form className="auth__form" onSubmit={handleSubmit}>
          <h1 className="auth__title">Вход</h1>

          <div className="auth__fields">
            <label className="field">
              <span className="label-mono">Логин</span>
              <input
                className="input"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                autoFocus
                required
              />
              <span className="hint">Вход по логину, не по email.</span>
            </label>

            <label className="field">
              <span className="label-mono">Пароль</span>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            {error ? <div className="notice notice--error">{error}</div> : null}

            <button type="submit" className="btn btn--primary btn--lg btn--block" disabled={pending}>
              {pending ? "Входим…" : "Войти"}
            </button>
          </div>

          <div className="auth__foot">
            Нет аккаунта? <Link to="/register">Создать</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
