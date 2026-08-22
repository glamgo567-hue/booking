import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "../../api/client";
import { changeRole, getUsers } from "../../api/endpoints";
import type { UserRole } from "../../api/types";
import { useAuth } from "../../auth/useAuth";

export function AdminUsers() {
  const queryClient = useQueryClient();
  const { user: me } = useAuth();

  const users = useQuery({ queryKey: ["users"], queryFn: () => getUsers({ limit: 100 }) });

  const update = useMutation({
    mutationFn: ({ id, role }: { id: number; role: UserRole }) => changeRole(id, role),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["users"] });
      void queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const error = users.error ?? update.error;

  return (
    <>
      {error ? (
        <div className="notice notice--error mt-24">
          {error instanceof ApiError ? error.message : "Не удалось загрузить сотрудников"}
        </div>
      ) : null}

      <div className="card mt-24">
        <div className="table__head">
          <div style={{ width: 220 }}>Логин</div>
          <div className="grow">Email</div>
          <div style={{ width: 220 }}>Роль</div>
        </div>

        {users.isPending ? (
          <div className="empty">Загрузка…</div>
        ) : (
          (users.data ?? []).map((user) => (
            <div className="table__row" key={user.id}>
              <div style={{ width: 220, fontSize: 14, fontWeight: 500 }}>{user.username}</div>
              <div className="grow" style={{ fontSize: 14, color: "var(--ink-2)" }}>
                {user.email}
              </div>
              <div style={{ width: 220 }}>
                <select
                  className="input input--sm"
                  value={user.role}
                  disabled={update.isPending || user.id === me?.id}
                  onChange={(event) =>
                    update.mutate({ id: user.id, role: event.target.value as UserRole })
                  }
                >
                  <option value="user">сотрудник</option>
                  <option value="office_manager">офис-менеджер</option>
                </select>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="hint mt-16">Свою собственную роль сменить нельзя.</div>
    </>
  );
}
