import type { BookingStatus, DeskBooking, Room, RoomBooking } from "../api/types";
import { formatTimeRange, parseDateKey } from "./dates";

export type BookingKind = "desk" | "room";

export interface UnifiedBooking {
  key: string;
  kind: BookingKind;
  id: number;
  userId: number;
  status: BookingStatus;
  createdAt: string;
  startsAt: number;
  day: Date;
  title: string;
  subtitle: string;
  timeLabel: string;
  startTime?: string;
  endTime?: string;
  roomId?: number;
}

export function roomLabel(rooms: Room[] | undefined, roomId: number): string {
  const room = rooms?.find((item) => item.id === roomId);
  return room ? `Переговорка «${room.name}»` : `Переговорка #${roomId}`;
}

export function roomMeta(rooms: Room[] | undefined, roomId: number): string {
  const room = rooms?.find((item) => item.id === roomId);
  if (!room) {
    return "";
  }
  const capacity = `${room.capacity} ${plural(room.capacity, "место", "места", "мест")}`;
  return room.equipment ? `${capacity} · ${room.equipment}` : capacity;
}

export function plural(count: number, one: string, few: string, many: string): string {
  const mod100 = count % 100;
  if (mod100 >= 11 && mod100 <= 14) {
    return many;
  }
  const mod10 = count % 10;
  if (mod10 === 1) {
    return one;
  }
  if (mod10 >= 2 && mod10 <= 4) {
    return few;
  }
  return many;
}

export function fromDeskBooking(booking: DeskBooking): UnifiedBooking {
  const day = parseDateKey(booking.date);
  return {
    key: `desk-${booking.id}`,
    kind: "desk",
    id: booking.id,
    userId: booking.user_id,
    status: booking.status,
    createdAt: booking.created_at,
    startsAt: day.getTime(),
    day,
    title: "Рабочее место",
    subtitle: "Общий пул мест",
    timeLabel: "весь день",
  };
}

export function fromRoomBooking(booking: RoomBooking, rooms: Room[] | undefined): UnifiedBooking {
  const start = new Date(booking.start_time);
  return {
    key: `room-${booking.id}`,
    kind: "room",
    id: booking.id,
    userId: booking.user_id,
    status: booking.status,
    createdAt: booking.created_at,
    startsAt: start.getTime(),
    day: new Date(start.getFullYear(), start.getMonth(), start.getDate()),
    title: roomLabel(rooms, booking.room_id),
    subtitle: roomMeta(rooms, booking.room_id),
    timeLabel: formatTimeRange(booking.start_time, booking.end_time),
    startTime: booking.start_time,
    endTime: booking.end_time,
    roomId: booking.room_id,
  };
}

export function byStartAsc(a: UnifiedBooking, b: UnifiedBooking): number {
  return a.startsAt - b.startsAt || a.key.localeCompare(b.key);
}
