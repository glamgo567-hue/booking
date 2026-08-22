import { request } from "./client";
import type {
  Desk,
  DeskAvailability,
  DeskBooking,
  Page,
  Room,
  RoomBooking,
  Token,
  User,
  UserRole,
} from "./types";

export function login(username: string, password: string) {
  return request<Token>("/auth/login", {
    method: "POST",
    form: { username, password },
    auth: false,
  });
}

export function register(data: {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
}) {
  return request<User>("/auth/register", { method: "POST", json: data, auth: false });
}

export function getMe(signal?: AbortSignal) {
  return request<User>("/auth/me", { signal });
}

export function getDesks(page: Page = {}) {
  return request<Desk[]>("/desks", { query: { skip: page.skip, limit: page.limit } });
}

export function createDesk(floor: number) {
  return request<Desk>("/desks", { method: "POST", json: { floor } });
}

export function updateDesk(id: number, data: { floor?: number; is_active?: boolean }) {
  return request<Desk>(`/desks/${id}`, { method: "PATCH", json: data });
}

export function deleteDesk(id: number) {
  return request<void>(`/desks/${id}`, { method: "DELETE" });
}

export function getRooms(page: Page = {}) {
  return request<Room[]>("/rooms", { query: { skip: page.skip, limit: page.limit } });
}

export function createRoom(data: { name: string; capacity: number; equipment: string | null }) {
  return request<Room>("/rooms", { method: "POST", json: data });
}

export function updateRoom(
  id: number,
  data: { name?: string; capacity?: number; equipment?: string | null },
) {
  return request<Room>(`/rooms/${id}`, { method: "PATCH", json: data });
}

export function deleteRoom(id: number) {
  return request<void>(`/rooms/${id}`, { method: "DELETE" });
}

export function getUsers(page: Page = {}) {
  return request<User[]>("/users", { query: { skip: page.skip, limit: page.limit } });
}

export function changeRole(id: number, role: UserRole) {
  return request<User>(`/users/${id}/role`, { method: "PATCH", json: { role } });
}

export function getDeskAvailability(date: string) {
  return request<DeskAvailability>("/bookings/desks/availability", { query: { date } });
}

export function getDeskAvailabilityRange(dateFrom: string, dateTo: string) {
  return request<DeskAvailability[]>("/bookings/desks/availability/range", {
    query: { date_from: dateFrom, date_to: dateTo },
  });
}

export function getMyDeskBookings(page: Page = {}) {
  return request<DeskBooking[]>("/bookings/desks/me", {
    query: { skip: page.skip, limit: page.limit },
  });
}

export function getAllDeskBookings(params: Page & { date?: string } = {}) {
  return request<DeskBooking[]>("/bookings/desks", {
    query: { date: params.date, skip: params.skip, limit: params.limit },
  });
}

export function createDeskBooking(date: string) {
  return request<DeskBooking>("/bookings/desks", { method: "POST", json: { date } });
}

export function confirmDeskBooking(id: number) {
  return request<DeskBooking>(`/bookings/desks/${id}/confirm`, { method: "PATCH" });
}

export function cancelDeskBooking(id: number) {
  return request<void>(`/bookings/desks/${id}`, { method: "DELETE" });
}

export function getMyRoomBookings(page: Page = {}) {
  return request<RoomBooking[]>("/bookings/rooms/me", {
    query: { skip: page.skip, limit: page.limit },
  });
}

export function getRoomBookings(roomId: number, params: Page & { date?: string } = {}) {
  return request<RoomBooking[]>(`/bookings/rooms/${roomId}`, {
    query: { date: params.date, skip: params.skip, limit: params.limit },
  });
}

export function getAllRoomBookings(params: Page & { date?: string } = {}) {
  return request<RoomBooking[]>("/bookings/rooms", {
    query: { date: params.date, skip: params.skip, limit: params.limit },
  });
}

export function createRoomBooking(data: { room_id: number; start_time: string; end_time: string }) {
  return request<RoomBooking>("/bookings/rooms", { method: "POST", json: data });
}

export function rescheduleRoomBooking(id: number, data: { start_time: string; end_time: string }) {
  return request<RoomBooking>(`/bookings/rooms/${id}`, { method: "PATCH", json: data });
}

export function confirmRoomBooking(id: number) {
  return request<RoomBooking>(`/bookings/rooms/${id}/confirm`, { method: "PATCH" });
}

export function cancelRoomBooking(id: number) {
  return request<void>(`/bookings/rooms/${id}`, { method: "DELETE" });
}
