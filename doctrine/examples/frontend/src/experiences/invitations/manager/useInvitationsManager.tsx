import { useCallback, useState } from "react";
import type { InvitationsEvent } from "./InvitationsEvent";
import { InvitationsManager } from "./InvitationsManager";
import type { InvitationsManagerOptions, InvitationsSnapshot } from "./InvitationsManager";

export type InvitationsDependencies = Omit<InvitationsManagerOptions, "onChange">;

export interface InvitationsBinding {
  readonly snapshot: InvitationsSnapshot;
  readonly emit: (event: InvitationsEvent) => void;
}

/**
 * FE-MGR-1: the whole framework binding. It creates one manager per mount and
 * mirrors each snapshot into React state. It holds no logic of its own.
 */
export function useInvitationsManager(dependencies: InvitationsDependencies): InvitationsBinding {
  const [mirrored, setMirrored] = useState<InvitationsSnapshot | null>(null);
  // The lazy initializer runs once per mount, so every later render reuses this manager.
  const [manager] = useState(() => new InvitationsManager({ ...dependencies, onChange: setMirrored }));
  const emit = useCallback(
    (event: InvitationsEvent) => {
      void manager.emit(event);
    },
    [manager],
  );
  return { snapshot: mirrored ?? manager.snapshot, emit };
}
