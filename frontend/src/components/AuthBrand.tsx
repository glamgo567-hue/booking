import { useQuery } from "@tanstack/react-query";
import { getDesks, getRooms } from "../api/endpoints";
import { plural } from "../lib/bookings";

export function AuthBrand({ withStats = false }: { withStats?: boolean }) {
  const desks = useQuery({
    queryKey: ["desks", { limit: 100 }],
    queryFn: () => getDesks({ limit: 100 }),
    enabled: withStats,
  });
  const rooms = useQuery({
    queryKey: ["rooms", { limit: 100 }],
    queryFn: () => getRooms({ limit: 100 }),
    enabled: withStats,
  });

  const deskCount = desks.data?.filter((desk) => desk.is_active).length;
  const roomCount = rooms.data?.length;

  return (
    <div className="auth__brand">
      <div className="wordmark" style={{ color: "var(--bg)" }}>
        <span className="wordmark__mark" style={{ borderColor: "var(--bg)" }} />
        <span className="wordmark__text">БРОНЬ</span>
      </div>

      <div>
        <div className="auth__statement">Столы и переговорки офиса — в одном месте.</div>
        {withStats && deskCount !== undefined && roomCount !== undefined ? (
          <div className="auth__stats">
            <div>
              <div className="auth__stat-value">{deskCount}</div>
              <div className="auth__stat-label">
                {plural(deskCount, "рабочее место", "рабочих места", "рабочих мест")}
              </div>
            </div>
            <div>
              <div className="auth__stat-value">{roomCount}</div>
              <div className="auth__stat-label">
                {plural(roomCount, "переговорка", "переговорки", "переговорок")}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      <div style={{ fontSize: 13, color: "#8f877b" }}>Внутренний сервис компании</div>
    </div>
  );
}
