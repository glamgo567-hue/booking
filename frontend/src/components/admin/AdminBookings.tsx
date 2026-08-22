import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ApiError } from "../../api/client";
import {
  getAllDeskBookings,
  getAllRoomBookings,
  getRooms,
  getUsers,
} from "../../api/endpoints";
import { StatusChip } from "../StatusChip";
import { DeskIcon, RoomIcon } from "../Icons";
import { ChevronLeftIcon, ChevronRightIcon } from "../Icons";
import { useBookingActions } from "../../hooks/useBookingActions";
import { byStartAsc, fromDeskBooking, fromRoomBooking, plural } from "../../lib/bookings";
import type { UnifiedBooking } from "../../lib/bookings";
import { addDays, dateKey, formatLongDate, parseDateKey, todayKey } from "../../lib/dates";

type Filter = "all" | "desk" | "room";

const PAGE_STEP = 20;

export function AdminBookings() {
  const actions = useBookingActions();
  const [dayKey, setDayKey] = useState(todayKey);
  const [filter, setFilter] = useState<Filter>("all");
  const [limit, setLimit] = useState(PAGE_STEP);

  const day = parseDateKey(dayKey);

  const rooms = useQuery({ queryKey: ["rooms"], queryFn: () => getRooms({ limit: 100 }) });
  const users = useQuery({ queryKey: ["users"], queryFn: () => getUsers({ limit: 100 }) });

  const deskBookings = useQuery({
    queryKey: ["bookings", "desk", "all", dayKey, limit],
    queryFn: () => getAllDeskBookings({ date: dayKey, limit }),
    enabled: filter !== "room",
  });

  const roomBookings = useQuery({
    queryKey: ["bookings", "room", "all", dayKey, limit],
    queryFn: () => getAllRoomBookings({ date: dayKey, limit }),
    enabled: filter !== "desk",
  });

  const userNames = useMemo(() => {
    const map = new Map<number, string>();
    for (const user of users.data ?? []) {
      map.set(user.id, user.username);
    }
    return map;
  }, [users.data]);

  const rows = useMemo<UnifiedBooking[]>(() => {
    const desks = filter === "room" ? [] : (deskBookings.data ?? []).map(fromDeskBooking);
    const meetings =
      filter === "desk"
        ? []
        : (roomBookings.data ?? []).map((booking) => fromRoomBooking(booking, rooms.data));
    return [...desks, ...meetings].sort(byStartAsc);
  }, [filter, deskBookings.data, roomBookings.data, rooms.data]);

  const hasMore =
    (deskBookings.data?.length ?? 0) >= limit || (roomBookings.data?.length ?? 0) >= limit;

  const isLoading =
    (filter !== "room" && deskBookings.isPending) || (filter !== "desk" && roomBookings.isPending);
  const error = deskBookings.error ?? roomBookings.error ?? actions.error;

  function shiftDay(days: number) {
    setDayKey(dateKey(addDays(day, days)));
    setLimit(PAGE_STEP);
  }

  return (
    <>
      <div className="mt-24 row-flex" style={{ justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div className="row-flex gap-16" style={{ flexWrap: "wrap" }}>
          <div className="stepper">
            <button type="button" className="icon-btn" aria-label="Предыдущий день" onClick={() => shiftDay(-1)}>
              <ChevronLeftIcon />
            </button>
            <span className="stepper__value">
              {formatLongDate(day)} {day.getFullYear()}
            </span>
            <button type="button" className="icon-btn" aria-label="Следующий день" onClick={() => shiftDay(1)}>
              <ChevronRightIcon />
            </button>
          </div>

          <div className="segmented">
            {(
              [
                ["all", "Все"],
                ["desk", "Столы"],
                ["room", "Переговорки"],
              ] as [Filter, string][]
            ).map(([value, label]) => (
              <button
                key={value}
                type="button"
                className={
                  filter === value ? "segmented__item segmented__item--active" : "segmented__item"
                }
                onClick={() => {
                  setFilter(value);
                  setLimit(PAGE_STEP);
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <span className="mono hint">
          {rows.length} {plural(rows.length, "активная бронь", "активные брони", "активных броней")}
        </span>
      </div>

      {error ? (
        <div className="notice notice--error mt-16">
          {error instanceof ApiError ? error.message : "Не удалось загрузить брони"}
        </div>
      ) : null}

      <div className="card mt-20">
        <div className="table__head">
          <div style={{ width: 280 }}>Ресурс</div>
          <div style={{ width: 230 }}>Сотрудник</div>
          <div style={{ width: 190 }}>Время</div>
          <div style={{ width: 170 }}>Статус</div>
          <div className="grow" />
        </div>

        {isLoading ? (
          <div className="empty">Загрузка…</div>
        ) : rows.length === 0 ? (
          <div className="empty">На этот день активных броней нет.</div>
        ) : (
          rows.map((booking) => (
            <div className="table__row" key={booking.key}>
              <div className="table__resource" style={{ width: 280 }}>
                <span style={{ color: "var(--ink-2)", display: "flex" }}>
                  {booking.kind === "desk" ? <DeskIcon size={18} /> : <RoomIcon size={18} />}
                </span>
                <span>{booking.title}</span>
              </div>
              <div style={{ width: 230, fontSize: 14, color: "var(--ink-2)" }}>
                {userNames.get(booking.userId) ?? `#${booking.userId}`}
              </div>
              <div className="mono" style={{ width: 190, fontSize: 14 }}>
                {booking.timeLabel}
              </div>
              <div style={{ width: 170 }}>
                <StatusChip status={booking.status} />
              </div>
              <div className="grow right">
                <button
                  type="button"
                  className="btn btn--ghost btn--sm btn--danger"
                  disabled={actions.busy}
                  onClick={() => actions.cancel.mutate({ kind: booking.kind, id: booking.id })}
                >
                  Отменить
                </button>
              </div>
            </div>
          ))
        )}

        {hasMore ? (
          <div className="table__foot">
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => setLimit((current) => Math.min(100, current + PAGE_STEP))}
              disabled={limit >= 100}
            >
              Показать ещё
            </button>
            <span className="mono hint">показано {rows.length}</span>
          </div>
        ) : null}
      </div>
    </>
  );
}
