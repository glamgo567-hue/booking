import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { getMyDeskBookings, getMyRoomBookings, getRooms } from "../api/endpoints";
import { PendingBanner } from "../components/PendingBanner";
import { StatusChip } from "../components/StatusChip";
import { DeskIcon, RoomIcon } from "../components/Icons";
import { useBookingActions } from "../hooks/useBookingActions";
import { byStartAsc, fromDeskBooking, fromRoomBooking } from "../lib/bookings";
import type { UnifiedBooking } from "../lib/bookings";
import { dateKey, formatDayMonth, weekdayShort } from "../lib/dates";

const PAGE_STEP = 10;

export function MyBookingsPage() {
  const navigate = useNavigate();
  const actions = useBookingActions();
  const [visible, setVisible] = useState(PAGE_STEP);

  const rooms = useQuery({ queryKey: ["rooms"], queryFn: () => getRooms({ limit: 100 }) });

  const deskBookings = useQuery({
    queryKey: ["bookings", "desk", "me"],
    queryFn: () => getMyDeskBookings({ limit: 100 }),
  });

  const roomBookings = useQuery({
    queryKey: ["bookings", "room", "me"],
    queryFn: () => getMyRoomBookings({ limit: 100 }),
  });

  const all = useMemo<UnifiedBooking[]>(() => {
    const desks = (deskBookings.data ?? []).map(fromDeskBooking);
    const meetings = (roomBookings.data ?? []).map((booking) =>
      fromRoomBooking(booking, rooms.data),
    );
    return [...desks, ...meetings].sort(byStartAsc);
  }, [deskBookings.data, roomBookings.data, rooms.data]);

  const pending = all.filter((booking) => booking.status === "pending");

  const startOfToday = useMemo(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  }, []);

  const upcoming = all.filter(
    (booking) => booking.status !== "pending" && booking.startsAt >= startOfToday,
  );

  const isLoading = deskBookings.isPending || roomBookings.isPending;
  const loadError = deskBookings.error ?? roomBookings.error;

  return (
    <div className="page">
      <div className="page__inner">
        <h1 className="h1">Мои брони</h1>

        {loadError ? (
          <div className="notice notice--error mt-24">
            {loadError instanceof ApiError ? loadError.message : "Не удалось загрузить брони"}
          </div>
        ) : null}

        {actions.error ? (
          <div className="notice notice--error mt-24">
            {actions.error instanceof ApiError ? actions.error.message : "Действие не выполнено"}
          </div>
        ) : null}

        <div className="stack gap-16 mt-24">
          {pending.map((booking) => (
            <PendingBanner
              key={booking.key}
              booking={booking}
              busy={actions.busy}
              onConfirm={() => actions.confirm.mutate({ kind: booking.kind, id: booking.id })}
              onCancel={() => actions.cancel.mutate({ kind: booking.kind, id: booking.id })}
              onExpire={actions.refresh}
            />
          ))}
        </div>

        <div className="section-rule">
          <span className="label-mono">Ближайшие</span>
          <span className="section-rule__line" />
        </div>

        {isLoading ? (
          <div className="empty">Загрузка…</div>
        ) : upcoming.length === 0 ? (
          <div className="empty">
            Ближайших броней нет. Забронируйте место на вкладке «Столы» или переговорку на вкладке
            «Переговорки».
          </div>
        ) : (
          <>
            <div className="mt-8">
              {upcoming.slice(0, visible).map((booking) => (
                <div
                  key={booking.key}
                  className={
                    booking.status === "cancelled" ? "booking-row booking-row--cancelled" : "booking-row"
                  }
                >
                  <div className="booking-row__date">
                    <div className="booking-row__day">{formatDayMonth(booking.day)}</div>
                    <div className="booking-row__weekday">{weekdayShort(booking.day)}</div>
                  </div>

                  <div className="booking-row__icon">
                    {booking.kind === "desk" ? <DeskIcon /> : <RoomIcon />}
                  </div>

                  <div className="booking-row__main">
                    <div className="booking-row__title">{booking.title}</div>
                    <div className="booking-row__sub">{booking.subtitle}</div>
                  </div>

                  <div className="booking-row__time">{booking.timeLabel}</div>

                  <div className="booking-row__status">
                    <StatusChip status={booking.status} />
                  </div>

                  <div className="booking-row__actions">
                    {booking.status === "confirmed" && booking.kind === "room" ? (
                      <button
                        type="button"
                        className="btn btn--ghost btn--sm"
                        onClick={() =>
                          navigate(
                            `/rooms?room=${booking.roomId}&date=${dateKey(booking.day)}&reschedule=${booking.id}`,
                          )
                        }
                      >
                        Перенести
                      </button>
                    ) : null}
                    {booking.status === "confirmed" ? (
                      <button
                        type="button"
                        className="btn btn--ghost btn--sm btn--danger"
                        disabled={actions.busy}
                        onClick={() => actions.cancel.mutate({ kind: booking.kind, id: booking.id })}
                      >
                        Отменить
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>

            {upcoming.length > visible ? (
              <div className="load-more">
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => setVisible((count) => count + PAGE_STEP)}
                >
                  Показать ещё
                </button>
                <span className="mono hint">показано {visible}</span>
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}
