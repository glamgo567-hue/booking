import { useContext } from "react";
import { AuthContext } from "./AuthContext";

export function useAuth() {
  const value = useContext(AuthContext);
  if (value === null) {
    throw new Error("useAuth вызван вне AuthProvider");
  }
  return value;
}
