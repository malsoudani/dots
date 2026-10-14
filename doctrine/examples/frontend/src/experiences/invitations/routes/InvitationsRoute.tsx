import { useState } from "react";
import { ApiClient } from "../../../common/http/ApiClient";
import { InvitationsProvider } from "../manager/InvitationsContext";
import type { InvitationsDependencies } from "../manager/useInvitationsManager";
import { isExpiryEnabled } from "../models/InvitationFlags";
import { InvitationsPage } from "../pages/InvitationsPage";
import { InvitationApiService } from "../services/InvitationApiService";
import { SessionApiService } from "../services/SessionApiService";

/**
 * The only code in the experience that reads the environment or browser storage
 * (FE-MGR-4, FE-SVC-6). Both services share one ApiClient (FE-SVC-4).
 */
function createRouteServices(): InvitationsDependencies {
  const apiClient = new ApiClient({
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? "",
    storage: window.localStorage,
  });
  return {
    sessionService: new SessionApiService(apiClient),
    invitationService: new InvitationApiService(apiClient),
    expiryEnabled: isExpiryEnabled(import.meta.env),
  };
}

/**
 * FE-STRUCT-4: the composition root. `useState` runs the factory once per mount,
 * so a re-render never builds a second service and never resets its in-flight
 * guard (FE-SVC-8). `teamId` comes from the router that mounts this route.
 */
export function InvitationsRoute({ teamId }: { readonly teamId: string }) {
  const [services] = useState(createRouteServices);
  return (
    <InvitationsProvider {...services}>
      <InvitationsPage teamId={teamId} />
    </InvitationsProvider>
  );
}
