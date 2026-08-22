import type { BookingStatus } from "../api/types";
import { ClockIcon } from "./Icons";

const LABELS: Record<BookingStatus, string> = {
  pending: "ожидает",
  confirmed: "подтверждена",
  cancelled: "отменена",
};

export function StatusChip({ status }: { status: BookingStatus }) {
  return (
    <span className={`chip chip--${status}`}>
      {status === "pending" ? <ClockIcon /> : null}
      {LABELS[status]}
    </span>
  );
}
