import { useEffect } from "react";
import { InvitationForm } from "../components/InvitationForm";
import { InvitationList } from "../components/InvitationList";
import { invitationsCopy, pendingSummary } from "../components/invitationsCopy";
import { useInvitations } from "../manager/InvitationsContext";
import {
  DirectorySearchRequested,
  DraftChanged,
  InvitationsRequested,
  RevokeRequested,
  SessionRequested,
  SubmitRequested,
} from "../manager/InvitationsEvent";
import type { DirectorySearch } from "../manager/InvitationsState";

/**
 * FE-UI-1 and FE-UI-2: the page selects what to render by `kind` and turns user
 * actions into events. It calls no service and reads no storage or environment.
 */
export function InvitationsPage({ teamId }: { readonly teamId: string }) {
  const { snapshot, emit } = useInvitations();
  const { sessionState } = snapshot;

  // The page reports that it is on screen and for which team. What that starts
  // is the manager's decision (FE-MGR-2).
  useEffect(() => emit(new SessionRequested()), [emit]);
  useEffect(() => emit(new InvitationsRequested(teamId)), [emit, teamId]);

  switch (sessionState.kind) {
    case "SessionIdle":
    case "SessionChecking":
      return <p>{invitationsCopy.checkingSession}</p>;
    case "SessionSignedOut":
      return <p>{invitationsCopy.signedOut}</p>;
    case "SessionFailed":
      return <p role="alert">{sessionState.failure.message}</p>;
    case "SessionAuthenticated":
      return <InvitationsFlow />;
  }
}

function InvitationsFlow() {
  const { snapshot, emit } = useInvitations();
  const { flowState, draft, view } = snapshot;

  const heading = (
    <header>
      <h1>{invitationsCopy.title}</h1>
      <p>{pendingSummary(view.pendingCount)}</p>
    </header>
  );
  const form = (
    <InvitationForm
      initialDraft={draft}
      view={view}
      onDraftChange={(next) => emit(new DraftChanged(next))}
      onSubmit={() => emit(new SubmitRequested())}
    />
  );

  switch (flowState.kind) {
    case "FlowIdle":
    case "FlowLoading":
      return <p>{invitationsCopy.loading}</p>;
    case "FlowLoaded":
      return (
        <main>
          {heading}
          {form}
          <label>
            {invitationsCopy.directory}
            <input
              type="search"
              value={flowState.directory.query}
              onChange={(event) => emit(new DirectorySearchRequested(event.target.value))}
            />
          </label>
          <DirectoryResults directory={flowState.directory} />
          <InvitationList
            invitations={flowState.invitations}
            onRevoke={(invitationId) => emit(new RevokeRequested(invitationId))}
          />
        </main>
      );
    case "FlowSubmitting":
      return (
        <main>
          {heading}
          {form}
          <p>{invitationsCopy.saving}</p>
          <InvitationList invitations={flowState.invitations} />
        </main>
      );
    case "FlowFailed":
      return (
        <main>
          {heading}
          <p role="alert">{flowState.failure.message}</p>
          <button type="button" onClick={() => emit(new InvitationsRequested(flowState.teamId))}>
            {invitationsCopy.retry}
          </button>
          <InvitationList invitations={flowState.invitations} />
        </main>
      );
  }
}

function DirectoryResults({ directory }: { readonly directory: DirectorySearch }) {
  switch (directory.status) {
    case "idle":
      return null;
    case "searching":
      return <p>{invitationsCopy.searching}</p>;
    case "loaded":
      if (directory.members.length === 0) {
        return <p>{invitationsCopy.noMembers}</p>;
      }
      return (
        <ul>
          {directory.members.map((member) => (
            <li key={member.id}>
              {member.name} ({member.email})
            </li>
          ))}
        </ul>
      );
  }
}
