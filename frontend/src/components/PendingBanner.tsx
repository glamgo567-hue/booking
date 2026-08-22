import { AUTO_CANCEL_SECONDS } from "../config";
import { useCountdown } from "../hooks/useCountdown";
import { formatDateWithWeekdayShort, formatSeconds } from "../lib/dates";
import type { UnifiedBooking } from "../lib/bookings";
import { ClockIcon } from "./Icons";

interface Props {
  booking: UnifiedBooking;
  onConfirm: () => void;
  onCancel: () => void;
  onExpire: () => void;
  busy?: boolean;
}

export function PendingBanner({ booking, onConfirm, onCancel, onExpire, busy = false }: Props) {
  const deadline = new Date(booking.createdAt).getTime() + AUTO_CANCEL_SECONDS * 1000;
  const left = useCountdown(deadline, onExpire);
  const width = Math.round((left / AUTO_CANCEL_SECONDS) * 148);

  const when =
    booking.kind === "desk"
      ? formatDateWithWeekdayShort(booking.day)
      : `${formatDateWithWeekdayShort(booking.day)}, ${booking.timeLabel}`;

  return (
    <div className="card card--pending card__pad pending">
      <div className="grow">
        <span className="chip chip--pending">
          <ClockIcon />
          ожидает подтверждения
        </span>
        <div style={{ marginTop: 12, fontSize: 20, fontWeight: 600, letterSpacing: "-0.01em" }}>
          {booking.title} · {when}
        </div>
        <div className="subtitle">
          {booking.kind === "desk"
            ? "Место удерживается за вами, пока идёт отсчёт. Не подтвердите — вернётся в общий пул."
            : "Комната удерживается за вами, пока идёт отсчёт. Не подтвердите — слот вернётся всем."}
        </div>
      </div>

      <div className="pending__aside">
        <div className="pending__clock">
          <div className="pending__value">{formatSeconds(left)}</div>
          <div className="pending__caption">до автоотмены</div>
          <div className="pending__track">
            <div className="pending__fill" style={{ width: `${Math.max(0, width)}px` }} />
          </div>
        </div>

        <div className="pending__divider" />

        <div className="pending__actions">
          <button type="button" className="btn btn--primary" onClick={onConfirm} disabled={busy || left === 0}>
            Подтвердить
          </button>
          <button type="button" className="btn btn--ghost" onClick={onCancel} disabled={busy}>
            Отменить
          </button>
        </div>
      </div>
    </div>
  );
}
