import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "../../api/client";
import { createDesk, deleteDesk, getDesks, updateDesk } from "../../api/endpoints";
import { plural } from "../../lib/bookings";

export function AdminDesks() {
  const queryClient = useQueryClient();
  const [floor, setFloor] = useState("1");

  const desks = useQuery({ queryKey: ["desks"], queryFn: () => getDesks({ limit: 100 }) });

  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["desks"] });
    void queryClient.invalidateQueries({ queryKey: ["availability"] });
  };

  const create = useMutation({ mutationFn: createDesk, onSuccess: refresh });
  const toggle = useMutation({
    mutationFn: ({ id, isActive }: { id: number; isActive: boolean }) =>
      updateDesk(id, { is_active: isActive }),
    onSuccess: refresh,
  });
  const remove = useMutation({ mutationFn: deleteDesk, onSettled: refresh });

  const error = create.error ?? toggle.error ?? remove.error ?? desks.error;
  const active = desks.data?.filter((desk) => desk.is_active).length ?? 0;

  function handleCreate(event: FormEvent) {
    event.preventDefault();
    const value = Number(floor);
    if (Number.isInteger(value)) {
      create.mutate(value);
    }
  }

  return (
    <>
      <div className="mt-24 row-flex" style={{ justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <form className="row-flex gap-8" onSubmit={handleCreate}>
          <span className="label-mono">Этаж</span>
          <input
            className="input input--sm input--mono"
            style={{ width: 90 }}
            type="number"
            value={floor}
            onChange={(event) => setFloor(event.target.value)}
            required
          />
          <button type="submit" className="btn btn--primary btn--sm" disabled={create.isPending}>
            Добавить место
          </button>
        </form>

        <span className="mono hint">
          {active} {plural(active, "активное место", "активных места", "активных мест")} из{" "}
          {desks.data?.length ?? 0}
        </span>
      </div>

      <div className="hint mt-8">
        Размер пула считается по активным местам. Изменения применяются к датам, которые ещё не
        открывались — уже посчитанные дни пересчитаются после того, как их счётчик истечёт в Redis.
      </div>

      {error ? (
        <div className="notice notice--error mt-16">
          {error instanceof ApiError ? error.message : "Не удалось изменить места"}
        </div>
      ) : null}

      <div className="card mt-20">
        <div className="table__head">
          <div style={{ width: 100 }}>ID</div>
          <div style={{ width: 160 }}>Этаж</div>
          <div style={{ width: 200 }}>Статус</div>
          <div className="grow" />
        </div>

        {desks.isPending ? (
          <div className="empty">Загрузка…</div>
        ) : (desks.data ?? []).length === 0 ? (
          <div className="empty">Мест пока нет — добавьте первое.</div>
        ) : (
          (desks.data ?? []).map((desk) => (
            <div className="table__row" key={desk.id}>
              <div className="mono" style={{ width: 100, fontSize: 14, color: "var(--ink-2)" }}>
                #{desk.id}
              </div>
              <div style={{ width: 160, fontSize: 14, fontWeight: 500 }}>{desk.floor}</div>
              <div style={{ width: 200 }}>
                <span className={desk.is_active ? "chip chip--confirmed" : "chip"}>
                  {desk.is_active ? "в пуле" : "выключено"}
                </span>
              </div>
              <div className="grow right">
                <button
                  type="button"
                  className="btn btn--ghost btn--sm"
                  disabled={toggle.isPending}
                  onClick={() => toggle.mutate({ id: desk.id, isActive: !desk.is_active })}
                >
                  {desk.is_active ? "Выключить" : "Включить"}
                </button>
                <button
                  type="button"
                  className="btn btn--ghost btn--sm btn--danger"
                  disabled={remove.isPending}
                  onClick={() => remove.mutate(desk.id)}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </>
  );
}
