import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { register } from "../api/endpoints";
import { useAuth } from "../auth/useAuth";
import { AuthBrand } from "../components/AuthBrand";

export function RegisterPage() {
  const { token, signIn } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (token !== null) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (password !== confirm) {
      setError("Пароли не совпадают");
      return;
    }

    setPending(true);
    try {
      const trimmed = username.trim();
      await register({
        username: trimmed,
        email: email.trim(),
        password,
        confirm_password: confirm,
      });
      await signIn(trimmed, password);
      navigate("/", { replace: true });
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "Не удалось зарегистрироваться");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="auth">
      <AuthBrand />

      <div className="auth__side">
        <form className="auth__form" onSubmit={handleSubmit}>
          <h1 className="auth__title">Регистрация</h1>

          <div className="auth__fields">
            <label className="field">
              <span className="label-mono">Логин</span>
              <input
                className="input"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                minLength={3}
                maxLength={100}
                autoComplete="username"
                autoFocus
                required
              />
              <span className="hint">От 3 символов. С ним же вы будете входить.</span>
            </label>

            <label className="field">
              <span className="label-mono">Email</span>
              <input
                className="input"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </label>

            <label className="field">
              <span className="label-mono">Пароль</span>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={8}
                autoComplete="new-password"
                required
              />
              <span className="hint">От 8 символов.</span>
            </label>

            <label className="field">
              <span className="label-mono">Пароль ещё раз</span>
              <input
                className="input"
                type="password"
                value={confirm}
                onChange={(event) => setConfirm(event.target.value)}
                minLength={8}
                autoComplete="new-password"
                required
              />
            </label>

            {error ? <div className="notice notice--error">{error}</div> : null}

            <button type="submit" className="btn btn--primary btn--lg btn--block" disabled={pending}>
              {pending ? "Создаём…" : "Создать аккаунт"}
            </button>
          </div>

          <div className="auth__foot">
            Уже есть аккаунт? <Link to="/login">Войти</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
