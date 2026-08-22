import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "../api/client";
import {
  createDeskBooking,
  getDeskAvailabilityRange,
  getDesks,
  getMyDeskBookings,
} from "../api/endpoints";
import { ChevronLeftIcon, ChevronRightIcon } from "../components/Icons";
import { StatusChip } from "../components/StatusChip";
import { AUTO_CANCEL_SECONDS } from "../config";
import { useBookingActions } from "../hooks/useBookingActions";
import { useCountdown } from "../hooks/useCountdown";
import { plural } from "../lib/bookings";
import {
  addMonths,
  buildMonthGrid,
  dateKey,
  formatLongDateWithWeekday,
  formatMonthYear,
  formatSeconds,
  isWeekend,
  minBookableKey,
  parseDateKey,
  startOfMonth,
  todayKey,
} from "../lib/dates";
import type { DeskBooking } from "../api/types";

const LOW_THRESHOLD = 5;
const WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"];

export function DesksPage() {
  const queryClient = useQueryClient();
  const actions = useBookingActions();

  const minKey = minBookableKey();
  const [month, setMonth] = useState(() => startOfMonth(parseDateKey(minKey)));
  const [selected, setSelected] = useState(minKey);

  const grid = useMemo(() => buildMonthGrid(month), [month]);
  const rangeFrom = dateKey(grid[0]);
  const rangeTo = dateKey(grid[grid.length - 1]);

  const availability = useQuery({
    queryKey: ["availability", "range", rangeFrom, rangeTo],
    queryFn: () => getDeskAvailabilityRange(rangeFrom, rangeTo),
  });

  const myBookings = useQuery({
    queryKey: ["bookings", "desk", "me"],
    queryFn: () => getMyDeskBookings({ limit: 100 }),
  });

  const desks = useQuery({ queryKey: ["desks"], queryFn: () => getDesks({ limit: 100 }) });

  const availableByDate = useMemo(() => {
    const map = new Map<string, number>();
    for (const item of availability.data ?? []) {
      map.set(item.date, item.available);
    }
    return map;
  }, [availability.data]);

  const mineByDate = useMemo(() => {
    const map = new Map<string, DeskBooking>();
    for (const booking of myBookings.data ?? []) {
      if (booking.status !== "cancelled") {
        map.set(booking.date, booking);
      }
    }
    return map;
  }, [myBookings.data]);

  const book = useMutation({
    mutationFn: (date: string) => createDeskBooking(date),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["bookings"] });
      void queryClient.invalidateQueries({ queryKey: ["availability"] });
    },
  });

  const totalActive = desks.data?.filter((desk) => desk.is_active).length;
  const selectedDate = parseDateKey(selected);
  const selectedAvailable = availableByDate.get(selected);
  const selectedBooking = mineByDate.get(selected);
  const today = todayKey();

  const error = availability.error ?? book.error ?? actions.error;

  return (
    <div className="page">
      <div className="page__inner">
        <div className="page__head">
          <div>
            <h1 className="h1">Рабочее место</h1>
            <div className="subtitle">
              Места не закреплены — бронируется одно из свободных на выбранный день.
            </div>
          </div>
          <span className="mono hint">одна бронь на человека в день</span>
        </div>

        {error ? (
          <div className="notice notice--error mt-24">
            {error instanceof ApiError ? error.message : "Что-то пошло не так"}
          </div>
        ) : null}

        <div className="split">
          <div className="split__main card" style={{ padding: 20 }}>
            <div className="calendar__head">
              <div className="calendar__month">{formatMonthYear(month)}</div>
              <div className="row-flex gap-8">
                <button
                  type="button"
                  className="icon-btn"
                  aria-label="Предыдущий месяц"
                  onClick={() => setMonth((current) => addMonths(current, -1))}
                >
                  <ChevronLeftIcon />
                </button>
                <button
                  type="button"
                  className="icon-btn"
                  aria-label="Следующий месяц"
                  onClick={() => setMonth((current) => addMonths(current, 1))}
                >
                  <ChevronRightIcon />
                </button>
              </div>
            </div>

            <div className="calendar__grid mt-16">
              {WEEKDAYS.map((day) => (
                <div key={day} className="calendar__weekday">
                  {day}
                </div>
              ))}
            </div>

            <div className="calendar__grid mt-8">
              {grid.map((day) => {
                const key = dateKey(day);
                const outside = day.getMonth() !== month.getMonth();
                const past = key < minKey;
                const mine = mineByDate.get(key);
                const available = availableByDate.get(key);
                const full = available === 0;
                const low = available !== undefined && available > 0 && available <= LOW_THRESHOLD;

                const classes = ["day"];
                if (outside) classes.push("day--outside");
                else if (mine) classes.push("day--mine");
                else if (full) classes.push("day--full");
                else if (low) classes.push("day--low");
                else if (isWeekend(day)) classes.push("day--weekend");
                if (key === selected) classes.push("day--selected");

                return (
                  <button
                    key={key}
                    type="button"
                    className={classes.join(" ")}
                    disabled={outside || past}
                    onClick={() => setSelected(key)}
                  >
                    <span className="day__top">
                      <span className={key === today ? "day__num day__num--strong" : "day__num"}>
                        {day.getDate()}
                      </span>
                      {key === today ? <span className="day__today">сегодня</span> : null}
                    </span>

                    {outside || past ? null : mine ? (
                      <span className="day__bottom">
                        <span
                          className={
                            mine.status === "pending" ? "day__mark day__mark--pending" : "day__mark"
                          }
                        />
                        <span
                          className={
                            mine.status === "pending" ? "day__mine day__mine--pending" : "day__mine"
                          }
                        >
                          {mine.status === "pending" ? "ждёт вас" : "ваша бронь"}
                        </span>
                      </span>
                    ) : available === undefined ? (
                      <span className="day__unit">…</span>
                    ) : full ? (
                      <span className="day__full-label">нет мест</span>
                    ) : (
                      <span className="day__bottom">
                        <span className={low ? "day__count day__count--low" : "day__count"}>
                          {available}
                        </span>
                        <span className={low ? "day__unit day__unit--low" : "day__unit"}>
                          {low ? "мало" : plural(available, "место", "места", "мест")}
                        </span>
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="split__aside card card__pad">
            <span className="label-mono">Выбрано</span>
            <div style={{ marginTop: 10, fontSize: 20, fontWeight: 600, letterSpacing: "-0.01em" }}>
              {formatLongDateWithWeekday(selectedDate)}
            </div>

            <div className="divider" />

            {selectedBooking ? (
              <SelectedBooking
                booking={selectedBooking}
                busy={actions.busy}
                onConfirm={() => actions.confirm.mutate({ kind: "desk", id: selectedBooking.id })}
                onCancel={() => actions.cancel.mutate({ kind: "desk", id: selectedBooking.id })}
                onExpire={actions.refresh}
              />
            ) : (
              <>
                <div className="big-number">
                  <span className="big-number__value">
                    {selectedAvailable === undefined ? "—" : selectedAvailable}
                  </span>
                  <span style={{ fontSize: 14, color: "var(--ink-2)" }}>
                    свободных мест
                    {totalActive === undefined ? "" : ` из ${totalActive}`}
                  </span>
                </div>

                <button
                  type="button"
                  className="btn btn--primary btn--lg btn--block mt-24"
                  disabled={book.isPending || selectedAvailable === 0 || selectedAvailable === undefined}
                  onClick={() => book.mutate(selected)}
                >
                  {selectedAvailable === 0 ? "Мест нет" : "Забронировать место"}
                </button>

                <div className="mt-12" style={{ fontSize: 13, color: "var(--ink-2)", lineHeight: 1.45 }}>
                  После брони есть{" "}
                  <span className="mono">{Math.round(AUTO_CANCEL_SECONDS / 60)} минут</span> на
                  подтверждение — иначе место вернётся в общий пул.
                </div>
              </>
            )}

            <div className="divider" />

            <span className="label-mono">Обозначения</span>
            <div className="legend">
              <div className="legend__item">
                <span className="legend__swatch" />
                места есть
              </div>
              <div className="legend__item">
                <span
                  className="legend__swatch"
                  style={{ background: "var(--pending-bg-soft)", borderColor: "var(--pending-line)" }}
                />
                <span style={{ color: "var(--pending-fg)" }}>осталось мало</span>
              </div>
              <div className="legend__item">
                <span
                  className="legend__swatch"
                  style={{ background: "var(--off-bg)", borderColor: "var(--off-line)" }}
                />
                мест нет
              </div>
              <div className="legend__item">
                <span
                  className="legend__swatch"
                  style={{ background: "var(--ok-fg)", borderColor: "var(--ok-fg)" }}
                />
                ваша бронь
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface SelectedBookingProps {
  booking: DeskBooking;
  busy: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  onExpire: () => void;
}

function SelectedBooking({ booking, busy, onConfirm, onCancel, onExpire }: SelectedBookingProps) {
  const deadline = new Date(booking.created_at).getTime() + AUTO_CANCEL_SECONDS * 1000;
  const left = useCountdown(deadline, onExpire);
  const isPending = booking.status === "pending";

  return (
    <>
      <StatusChip status={booking.status} />

      {isPending ? (
        <div className="mt-16">
          <div className="pending__value">{formatSeconds(left)}</div>
          <div className="pending__caption">до автоотмены</div>
        </div>
      ) : (
        <div className="mt-16" style={{ fontSize: 14, color: "var(--ink-2)" }}>
          Место закреплено за вами на этот день.
        </div>
      )}

      {isPending ? (
        <button
          type="button"
          className="btn btn--primary btn--lg btn--block mt-24"
          disabled={busy || left === 0}
          onClick={onConfirm}
        >
          Подтвердить
        </button>
      ) : null}

      <button
        type="button"
        className={isPending ? "btn btn--ghost btn--lg btn--block mt-8" : "btn btn--ghost btn--lg btn--block mt-24"}
        disabled={busy}
        onClick={onCancel}
      >
        Отменить бронь
      </button>
    </>
  );
}
