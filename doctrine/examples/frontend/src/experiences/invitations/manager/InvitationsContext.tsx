import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import { useInvitationsManager } from "./useInvitationsManager";
import type { InvitationsBinding, InvitationsDependencies } from "./useInvitationsManager";

const InvitationsContext = createContext<InvitationsBinding | null>(null);

interface InvitationsProviderProps extends InvitationsDependencies {
  readonly children: ReactNode;
}

export function InvitationsProvider({ children, ...dependencies }: InvitationsProviderProps) {
  const binding = useInvitationsManager(dependencies);
  return <InvitationsContext value={binding}>{children}</InvitationsContext>;
}

/** What presentation reads: the current snapshot and `emit`. */
export function useInvitations(): InvitationsBinding {
  const binding = useContext(InvitationsContext);
  if (binding === null) {
    throw new Error("useInvitations must be called inside InvitationsProvider");
  }
  return binding;
}
