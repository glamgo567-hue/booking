const raw = Number(import.meta.env.VITE_BOOKING_AUTO_CANCEL_SECONDS);

export const AUTO_CANCEL_SECONDS = Number.isFinite(raw) && raw > 0 ? raw : 600;

export const DAY_START_MINUTES = 9 * 60;
export const DAY_END_MINUTES = 19 * 60;
export const SLOT_MINUTES = 30;
