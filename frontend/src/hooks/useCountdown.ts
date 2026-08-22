import { useEffect, useRef, useState } from "react";

export function useCountdown(deadline: number, onExpire?: () => void): number {
  const [left, setLeft] = useState(() => Math.max(0, Math.round((deadline - Date.now()) / 1000)));
  const expired = useRef(false);
  const onExpireRef = useRef(onExpire);

  useEffect(() => {
    onExpireRef.current = onExpire;
  }, [onExpire]);

  useEffect(() => {
    expired.current = false;

    const tick = () => {
      const seconds = Math.max(0, Math.round((deadline - Date.now()) / 1000));
      setLeft(seconds);
      if (seconds === 0 && !expired.current) {
        expired.current = true;
        onExpireRef.current?.();
      }
    };

    tick();
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [deadline]);

  return left;
}
