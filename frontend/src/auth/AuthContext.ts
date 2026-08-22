import { createContext } from "react";
import type { User } from "../api/types";

export interface AuthValue {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  isManager: boolean;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => void;
}

export const AuthContext = createContext<AuthValue | null>(null);
