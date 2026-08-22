export type UserRole = "user" | "office_manager";

export type BookingStatus = "pending" | "confirmed" | "cancelled";

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Desk {
  id: number;
  floor: number;
  is_active: boolean;
  created_at: string;
}

export interface Room {
  id: number;
  name: string;
  capacity: number;
  equipment: string | null;
  created_at: string;
}

export interface DeskAvailability {
  date: string;
  available: number;
}

export interface DeskBooking {
  id: number;
  date: string;
  status: BookingStatus;
  created_at: string;
  user_id: number;
}

export interface RoomBooking {
  id: number;
  start_time: string;
  end_time: string;
  status: BookingStatus;
  created_at: string;
  room_id: number;
  user_id: number;
}

export interface Page {
  skip?: number;
  limit?: number;
}
