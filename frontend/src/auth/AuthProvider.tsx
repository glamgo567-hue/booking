import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { setUnauthorizedHandler, tokenStorage } from "../api/client";
import { getMe, login as loginRequest } from "../api/endpoints";
import { AuthContext } from "./AuthContext";
import type { AuthValue } from "./AuthContext";

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(() => tokenStorage.read());

  const signOut = useCallback(() => {
    tokenStorage.clear();
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => {
    setUnauthorizedHandler(signOut);
    return () => setUnauthorizedHandler(null);
  }, [signOut]);

  const meQuery = useQuery({
    queryKey: ["me", token],
    queryFn: ({ signal }) => getMe(signal),
    enabled: token !== null,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const signIn = useCallback(
    async (username: string, password: string) => {
      const issued = await loginRequest(username, password);
      tokenStorage.write(issued.access_token);
      setToken(issued.access_token);
    },
    [],
  );

  const value = useMemo<AuthValue>(
    () => ({
      token,
      user: meQuery.data ?? null,
      isLoading: token !== null && meQuery.isPending,
      isManager: meQuery.data?.role === "office_manager",
      signIn,
      signOut,
    }),
    [token, meQuery.data, meQuery.isPending, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
