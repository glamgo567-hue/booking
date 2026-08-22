import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  cancelDeskBooking,
  cancelRoomBooking,
  confirmDeskBooking,
  confirmRoomBooking,
} from "../api/endpoints";
import type { BookingKind } from "../lib/bookings";

export interface BookingRef {
  kind: BookingKind;
  id: number;
}

export function useBookingActions() {
  const queryClient = useQueryClient();

  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["bookings"] });
    void queryClient.invalidateQueries({ queryKey: ["availability"] });
  };

  const confirm = useMutation({
    mutationFn: async ({ kind, id }: BookingRef) => {
      if (kind === "desk") {
        await confirmDeskBooking(id);
      } else {
        await confirmRoomBooking(id);
      }
    },
    onSettled: refresh,
  });

  const cancel = useMutation({
    mutationFn: async ({ kind, id }: BookingRef) => {
      if (kind === "desk") {
        await cancelDeskBooking(id);
      } else {
        await cancelRoomBooking(id);
      }
    },
    onSettled: refresh,
  });

  return {
    confirm,
    cancel,
    refresh,
    busy: confirm.isPending || cancel.isPending,
    error: confirm.error ?? cancel.error,
  };
}
