const WEEKDAY_SHORT = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];

const monthLong = new Intl.DateTimeFormat("ru-RU", { month: "long" });
const dayMonthLong = new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "long" });
const weekdayLong = new Intl.DateTimeFormat("ru-RU", { weekday: "long" });
const timeShort = new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" });

function pad(value: number): string {
  return String(value).padStart(2, "0");
}

export function dateKey(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function parseDateKey(key: string): Date {
  const [year, month, day] = key.split("-").map(Number);
  return new Date(year, month - 1, day);
}

export function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function addMonths(date: Date, months: number): Date {
  return new Date(date.getFullYear(), date.getMonth() + months, 1);
}

export function isSameDay(a: Date, b: Date): boolean {
  return dateKey(a) === dateKey(b);
}

export function todayKey(): string {
  return dateKey(new Date());
}

export function minBookableKey(): string {
  const now = new Date();
  const utcKey = `${now.getUTCFullYear()}-${pad(now.getUTCMonth() + 1)}-${pad(now.getUTCDate())}`;
  const localKey = dateKey(now);
  return localKey > utcKey ? localKey : utcKey;
}

export function buildMonthGrid(month: Date): Date[] {
  const first = startOfMonth(month);
  const leading = (first.getDay() + 6) % 7;
  const start = addDays(first, -leading);
  const daysInMonth = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const cells = Math.ceil((leading + daysInMonth) / 7) * 7;
  return Array.from({ length: cells }, (_, index) => addDays(start, index));
}

export function isWeekend(date: Date): boolean {
  const day = date.getDay();
  return day === 0 || day === 6;
}

export function weekdayShort(date: Date): string {
  return WEEKDAY_SHORT[date.getDay()];
}

export function formatDayMonth(date: Date): string {
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}`;
}

export function formatMonthYear(date: Date): string {
  const name = monthLong.format(date);
  return `${name.charAt(0).toUpperCase()}${name.slice(1)} ${date.getFullYear()}`;
}

export function formatLongDate(date: Date): string {
  return dayMonthLong.format(date);
}

export function formatLongDateWithWeekday(date: Date): string {
  return `${dayMonthLong.format(date)}, ${weekdayLong.format(date)}`;
}

export function formatDateWithWeekdayShort(date: Date): string {
  return `${dayMonthLong.format(date)}, ${weekdayShort(date)}`;
}

export function formatTime(iso: string): string {
  return timeShort.format(new Date(iso));
}

export function formatTimeRange(startIso: string, endIso: string): string {
  return `${formatTime(startIso)}–${formatTime(endIso)}`;
}

export function minutesFromLabel(label: string): number {
  const [hours, minutes] = label.split(":").map(Number);
  return hours * 60 + minutes;
}

export function labelFromMinutes(minutes: number): string {
  return `${pad(Math.floor(minutes / 60))}:${pad(minutes % 60)}`;
}

export function minutesOfDay(iso: string, day: Date): number {
  const moment = new Date(iso);
  const dayStart = new Date(day.getFullYear(), day.getMonth(), day.getDate());
  return Math.round((moment.getTime() - dayStart.getTime()) / 60000);
}

export function toIsoInstant(day: Date, minutes: number): string {
  const moment = new Date(
    day.getFullYear(),
    day.getMonth(),
    day.getDate(),
    Math.floor(minutes / 60),
    minutes % 60,
    0,
    0,
  );
  return moment.toISOString();
}

export function formatSeconds(totalSeconds: number): string {
  const safe = Math.max(0, totalSeconds);
  return `${pad(Math.floor(safe / 60))}:${pad(safe % 60)}`;
}
