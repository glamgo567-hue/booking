import { useState } from "react";
import { AdminBookings } from "../components/admin/AdminBookings";
import { AdminDesks } from "../components/admin/AdminDesks";
import { AdminRooms } from "../components/admin/AdminRooms";
import { AdminUsers } from "../components/admin/AdminUsers";

type Tab = "bookings" | "desks" | "rooms" | "users";

const TABS: [Tab, string][] = [
  ["bookings", "Брони"],
  ["desks", "Столы"],
  ["rooms", "Переговорки"],
  ["users", "Сотрудники"],
];

export function AdminPage() {
  const [tab, setTab] = useState<Tab>("bookings");

  return (
    <div className="page">
      <div className="page__inner">
        <h1 className="h1">Админка</h1>

        <div className="tabs">
          {TABS.map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={tab === value ? "tabs__item tabs__item--active" : "tabs__item"}
              onClick={() => setTab(value)}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === "bookings" ? <AdminBookings /> : null}
        {tab === "desks" ? <AdminDesks /> : null}
        {tab === "rooms" ? <AdminRooms /> : null}
        {tab === "users" ? <AdminUsers /> : null}
      </div>
    </div>
  );
}
