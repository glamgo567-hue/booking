import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "../../api/client";
import { createRoom, deleteRoom, getRooms } from "../../api/endpoints";
import { plural } from "../../lib/bookings";

export function AdminRooms() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState("4");
  const [equipment, setEquipment] = useState("");

  const rooms = useQuery({ queryKey: ["rooms"], queryFn: () => getRooms({ limit: 100 }) });

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["rooms"] });

  const create = useMutation({
    mutationFn: createRoom,
    onSuccess: () => {
      setName("");
      setEquipment("");
      void refresh();
    },
  });

  const remove = useMutation({ mutationFn: deleteRoom, onSettled: () => void refresh() });

  const error = create.error ?? remove.error ?? rooms.error;

  function handleCreate(event: FormEvent) {
    event.preventDefault();
    create.mutate({
      name: name.trim(),
      capacity: Number(capacity),
      equipment: equipment.trim() === "" ? null : equipment.trim(),
    });
  }

  return (
    <>
      <form className="mt-24 row-flex gap-8" style={{ flexWrap: "wrap" }} onSubmit={handleCreate}>
        <input
          className="input input--sm"
          style={{ width: 200 }}
          placeholder="Название"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
        <input
          className="input input--sm input--mono"
          style={{ width: 110 }}
          type="number"
          min={1}
          placeholder="Мест"
          value={capacity}
          onChange={(event) => setCapacity(event.target.value)}
          required
        />
        <input
          className="input input--sm"
          style={{ width: 260 }}
          placeholder="Оборудование (необязательно)"
          value={equipment}
          onChange={(event) => setEquipment(event.target.value)}
        />
        <button type="submit" className="btn btn--primary btn--sm" disabled={create.isPending}>
          Добавить переговорку
        </button>
      </form>

      {error ? (
        <div className="notice notice--error mt-16">
          {error instanceof ApiError ? error.message : "Не удалось изменить переговорки"}
        </div>
      ) : null}

      <div className="card mt-20">
        <div className="table__head">
          <div style={{ width: 240 }}>Название</div>
          <div style={{ width: 140 }}>Вместимость</div>
          <div className="grow">Оборудование</div>
          <div style={{ width: 120 }} />
        </div>

        {rooms.isPending ? (
          <div className="empty">Загрузка…</div>
        ) : (rooms.data ?? []).length === 0 ? (
          <div className="empty">Переговорок пока нет — добавьте первую.</div>
        ) : (
          (rooms.data ?? []).map((room) => (
            <div className="table__row" key={room.id}>
              <div style={{ width: 240, fontSize: 14, fontWeight: 500 }}>{room.name}</div>
              <div className="mono" style={{ width: 140, fontSize: 14 }}>
                {room.capacity} {plural(room.capacity, "место", "места", "мест")}
              </div>
              <div className="grow" style={{ fontSize: 14, color: "var(--ink-2)" }}>
                {room.equipment ?? "—"}
              </div>
              <div style={{ width: 120 }} className="right">
                <button
                  type="button"
                  className="btn btn--ghost btn--sm btn--danger"
                  disabled={remove.isPending}
                  onClick={() => remove.mutate(room.id)}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="hint mt-16">
        Переговорку с любыми бронями — даже отменёнными — удалить нельзя, сервер вернёт 409.
      </div>
    </>
  );
}
