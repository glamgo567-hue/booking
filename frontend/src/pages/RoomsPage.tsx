import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import {
  createRoomBooking,
  getRoomBookings,
  getRooms,
  rescheduleRoomBooking,
} from "../api/endpoints";
import type { RoomBooking } from "../api/types";
import { ChevronLeftIcon, ChevronRightIcon, RoomIcon } from "../components/Icons";
import { AUTO_CANCEL_SECONDS, DAY_END_MINUTES, DAY_START_MINUTES, SLOT_MINUTES } from "../config";
import { useAuth } from "../auth/useAuth";
import { plural } from "../lib/bookings";
import {
  addDays,
  dateKey,
  formatDateWithWeekdayShort,
  labelFromMinutes,
  minutesFromLabel,
  minutesOfDay,
  parseDateKey,
  toIsoInstant,
  todayKey,
} from "../lib/dates";

const ROW_HEIGHT = 46;

interface Draft {
  key: string;
  start: number;
  end: number;
}

interface Slice {
  booking: RoomBooking;
  start: number;
  end: number;
  mine: boolean;
}

export function RoomsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [params, setParams] = useSearchParams();

  const rooms = useQuery({ queryKey: ["rooms"], queryFn: () => getRooms({ limit: 100 }) });

  const roomParam = Number(params.get("room"));
  const dayParam = params.get("date") ?? todayKey();
  const rescheduleId = Number(params.get("reschedule")) || null;

  const roomId = useMemo(() => {
    const list = rooms.data ?? [];
    if (list.some((room) => room.id === roomParam)) {
      return roomParam;
    }
    return list[0]?.id ?? null;
  }, [rooms.data, roomParam]);

  const day = parseDateKey(dayParam);
  const draftKey = `${roomId ?? "none"}:${dayParam}`;
  const [draftState, setDraftState] = useState<Draft | null>(null);
  const draft = draftState !== null && draftState.key === draftKey ? draftState : null;

  const setDraft = (next: { start: number; end: number } | null) =>
    setDraftState(next === null ? null : { key: draftKey, ...next });

  const schedule = useQuery({
    queryKey: ["bookings", "room", "byRoom", roomId, dayParam],
    enabled: roomId !== null,
    queryFn: async () => {
      const keys = [dateKey(addDays(day, -1)), dayParam, dateKey(addDays(day, 1))];
      const pages = await Promise.all(
        keys.map((key) => getRoomBookings(roomId as number, { date: key, limit: 100 })),
      );
      const seen = new Set<number>();
      const merged: RoomBooking[] = [];
      for (const page of pages) {
        for (const booking of page) {
          if (!seen.has(booking.id)) {
            seen.add(booking.id);
            merged.push(booking);
          }
        }
      }
      return merged;
    },
  });

  const slices = useMemo<Slice[]>(() => {
    const result: Slice[] = [];
    for (const booking of schedule.data ?? []) {
      if (booking.id === rescheduleId) {
        continue;
      }
      const start = minutesOfDay(booking.start_time, day);
      const end = minutesOfDay(booking.end_time, day);
      if (end <= 0 || start >= 24 * 60) {
        continue;
      }
      result.push({ booking, start, end, mine: booking.user_id === user?.id });
    }
    return result.sort((a, b) => a.start - b.start);
  }, [schedule.data, day, rescheduleId, user?.id]);

  const busyRanges = slices.map((slice) => ({ start: slice.start, end: slice.end }));

  const nowMinutes = useMemo(() => {
    const now = new Date();
    return dateKey(now) === dayParam ? now.getHours() * 60 + now.getMinutes() : -1;
  }, [dayParam]);

  const save = useMutation({
    mutationFn: (range: { start: number; end: number }) => {
      const payload = {
        start_time: toIsoInstant(day, range.start),
        end_time: toIsoInstant(day, range.end),
      };
      return rescheduleId
        ? rescheduleRoomBooking(rescheduleId, payload)
        : createRoomBooking({ room_id: roomId as number, ...payload });
    },
    onSuccess: () => {
      setDraft(null);
      void queryClient.invalidateQueries({ queryKey: ["bookings"] });
      if (rescheduleId) {
        navigate("/");
      }
    },
  });

  const selectedRoom = rooms.data?.find((room) => room.id === roomId) ?? null;
  const error = rooms.error ?? schedule.error ?? save.error;

  function isFree(start: number, end: number): boolean {
    return busyRanges.every((range) => start >= range.end || end <= range.start);
  }

  function pickSlot(start: number) {
    const nextBusy = busyRanges
      .filter((range) => range.start >= start)
      .reduce((min, range) => Math.min(min, range.start), DAY_END_MINUTES);
    const end = Math.min(start + 60, nextBusy, DAY_END_MINUTES);
    if (end > start) {
      setDraft({ start, end });
    }
  }

  function shiftDay(days: number) {
    const next = dateKey(addDays(day, days));
    const nextParams = new URLSearchParams(params);
    nextParams.set("date", next);
    setParams(nextParams, { replace: true });
  }

  function selectRoom(id: number) {
    const nextParams = new URLSearchParams(params);
    nextParams.set("room", String(id));
    setParams(nextParams, { replace: true });
  }

  const hours: number[] = [];
  for (let minutes = DAY_START_MINUTES; minutes < DAY_END_MINUTES; minutes += 60) {
    hours.push(minutes);
  }

  const timeOptions: number[] = [];
  for (let minutes = DAY_START_MINUTES; minutes <= DAY_END_MINUTES; minutes += SLOT_MINUTES) {
    timeOptions.push(minutes);
  }

  const draftValid =
    draft !== null &&
    draft.end > draft.start &&
    isFree(draft.start, draft.end) &&
    (nowMinutes < 0 || draft.start > nowMinutes);

  return (
    <div className="page">
      <div className="page__inner">
        <div className="page__head">
          <div>
            <h1 className="h1">Переговорки</h1>
            <div className="subtitle">Сначала комната, затем свободное время в её расписании.</div>
          </div>
          <div className="stepper">
            <button type="button" className="icon-btn" aria-label="Предыдущий день" onClick={() => shiftDay(-1)}>
              <ChevronLeftIcon />
            </button>
            <span className="stepper__value">{formatDateWithWeekdayShort(day)}</span>
            <button type="button" className="icon-btn" aria-label="Следующий день" onClick={() => shiftDay(1)}>
              <ChevronRightIcon />
            </button>
          </div>
        </div>

        {rescheduleId ? (
          <div className="notice mt-24">
            Переносим бронь: выберите новое время и нажмите «Перенести сюда».{" "}
            <button
              type="button"
              className="nav__link"
              style={{ textDecoration: "underline" }}
              onClick={() => navigate("/")}
            >
              Отменить перенос
            </button>
          </div>
        ) : null}

        {error ? (
          <div className="notice notice--error mt-24">
            {error instanceof ApiError ? error.message : "Что-то пошло не так"}
          </div>
        ) : null}

        {rooms.isPending ? (
          <div className="empty">Загрузка…</div>
        ) : (rooms.data ?? []).length === 0 ? (
          <div className="empty">
            Переговорок пока нет — их заводит офис-менеджер во вкладке «Админка».
          </div>
        ) : (
          <div className="split" style={{ gap: 32 }}>
            <div className="split__aside card" style={{ width: 340 }}>
              <div style={{ padding: "14px 18px", borderBottom: "1px solid var(--line)" }}>
                <span className="label-mono">Комнаты</span>
              </div>
              {(rooms.data ?? []).map((room) => (
                <button
                  key={room.id}
                  type="button"
                  className={room.id === roomId ? "room-item room-item--active" : "room-item"}
                  onClick={() => selectRoom(room.id)}
                >
                  <div className="room-item__name">{room.name}</div>
                  <div className="room-item__meta">
                    {room.capacity} {plural(room.capacity, "место", "места", "мест")}
                    {room.equipment ? ` · ${room.equipment}` : ""}
                  </div>
                </button>
              ))}
            </div>

            <div className="split__main card">
              <div
                style={{
                  padding: "16px 20px",
                  borderBottom: "1px solid var(--line)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 16,
                  flexWrap: "wrap",
                }}
              >
                <div className="row-flex gap-12">
                  <span style={{ display: "flex" }}>
                    <RoomIcon />
                  </span>
                  <span style={{ fontSize: 18, fontWeight: 600 }}>{selectedRoom?.name}</span>
                  {selectedRoom ? (
                    <span className="mono hint">
                      {selectedRoom.capacity}{" "}
                      {plural(selectedRoom.capacity, "место", "места", "мест")}
                      {selectedRoom.equipment ? ` · ${selectedRoom.equipment}` : ""}
                    </span>
                  ) : null}
                </div>
                <div className="timeline__legend">
                  <span>
                    <i style={{ background: "var(--off-bg)", border: "1px solid var(--off-line)" }} />
                    занято
                  </span>
                  <span>
                    <i style={{ background: "var(--pending-bg)", border: "1px solid var(--pending-line)" }} />
                    ваша бронь
                  </span>
                </div>
              </div>

              <div className="timeline">
                {hours.map((hourStart) => (
                  <div className="timeline__row" key={hourStart}>
                    <div
                      className={
                        draft !== null && draft.start >= hourStart && draft.start < hourStart + 60
                          ? "timeline__label timeline__label--active"
                          : "timeline__label"
                      }
                    >
                      {labelFromMinutes(hourStart)}
                    </div>
                    <div className="timeline__lane">
                      {[0, SLOT_MINUTES].map((offset) => {
                        const slotStart = hourStart + offset;
                        const occupied = !isFree(slotStart, slotStart + SLOT_MINUTES);
                        const isPast = nowMinutes >= 0 && slotStart <= nowMinutes;
                        return (
                          <button
                            key={offset}
                            type="button"
                            aria-label={`Выбрать ${labelFromMinutes(slotStart)}`}
                            className={
                              offset === 0 ? "timeline__slot" : "timeline__slot timeline__slot--second"
                            }
                            disabled={occupied || isPast}
                            onClick={() => pickSlot(slotStart)}
                          />
                        );
                      })}

                      {slices
                        .filter((slice) => slice.start >= hourStart && slice.start < hourStart + 60)
                        .map((slice) => (
                          <div
                            key={slice.booking.id}
                            className={
                              slice.mine
                                ? slice.booking.status === "pending"
                                  ? "timeline__block timeline__block--mine"
                                  : "timeline__block timeline__block--mine-ok"
                                : "timeline__block"
                            }
                            style={{
                              top: ((slice.start - hourStart) / 60) * ROW_HEIGHT + 3,
                              height: Math.max(
                                18,
                                ((Math.min(slice.end, DAY_END_MINUTES) - slice.start) / 60) *
                                  ROW_HEIGHT -
                                  6,
                              ),
                            }}
                          >
                            <span className="timeline__block-time">
                              {labelFromMinutes(slice.start)}–{labelFromMinutes(slice.end)}
                            </span>
                            <span className="timeline__block-name">
                              {slice.mine
                                ? slice.booking.status === "pending"
                                  ? "Ваша бронь · ждёт подтверждения"
                                  : "Ваша бронь"
                                : "Занято"}
                            </span>
                          </div>
                        ))}

                      {draft !== null && draft.start >= hourStart && draft.start < hourStart + 60 ? (
                        <div
                          className="timeline__block timeline__block--draft"
                          style={{
                            top: ((draft.start - hourStart) / 60) * ROW_HEIGHT + 3,
                            height: Math.max(18, ((draft.end - draft.start) / 60) * ROW_HEIGHT - 6),
                          }}
                        >
                          <span className="timeline__block-time">
                            {labelFromMinutes(draft.start)}–{labelFromMinutes(draft.end)}
                          </span>
                          <span className="timeline__block-name">
                            {rescheduleId ? "Новое время" : "Новая бронь"}
                          </span>
                        </div>
                      ) : null}
                    </div>
                  </div>
                ))}
              </div>

              <div className="timeline__footer">
                <div className="row-flex gap-8">
                  <span className="label-mono">с</span>
                  <select
                    className="input input--sm input--mono"
                    value={draft ? labelFromMinutes(draft.start) : ""}
                    onChange={(event) => {
                      const start = minutesFromLabel(event.target.value);
                      setDraft({
                        start,
                        end: Math.max(start + SLOT_MINUTES, draft?.end ?? start + 60),
                      });
                    }}
                  >
                    <option value="" disabled>
                      —
                    </option>
                    {timeOptions.slice(0, -1).map((minutes) => (
                      <option key={minutes} value={labelFromMinutes(minutes)}>
                        {labelFromMinutes(minutes)}
                      </option>
                    ))}
                  </select>

                  <span className="label-mono" style={{ marginLeft: 6 }}>
                    до
                  </span>
                  <select
                    className="input input--sm input--mono"
                    value={draft ? labelFromMinutes(draft.end) : ""}
                    disabled={draft === null}
                    onChange={(event) => {
                      if (draft !== null) {
                        setDraft({ start: draft.start, end: minutesFromLabel(event.target.value) });
                      }
                    }}
                  >
                    <option value="" disabled>
                      —
                    </option>
                    {timeOptions
                      .filter((minutes) => draft === null || minutes > draft.start)
                      .map((minutes) => (
                        <option key={minutes} value={labelFromMinutes(minutes)}>
                          {labelFromMinutes(minutes)}
                        </option>
                      ))}
                  </select>
                </div>

                <div className="row-flex gap-16">
                  <span className="hint">
                    {draft === null
                      ? "Выберите свободный интервал в расписании"
                      : draftValid
                        ? rescheduleId
                          ? "перенос не требует повторного подтверждения"
                          : `подтвердить в течение ${Math.round(AUTO_CANCEL_SECONDS / 60)} минут`
                        : "интервал занят или уже прошёл"}
                  </span>
                  <button
                    type="button"
                    className="btn btn--primary"
                    style={{ height: 44, padding: "0 24px", fontSize: 15 }}
                    disabled={!draftValid || save.isPending}
                    onClick={() => draft && save.mutate(draft)}
                  >
                    {rescheduleId ? "Перенести сюда" : "Забронировать"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
