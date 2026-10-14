import { isLeft, match } from "fp-ts/Either";
import type { Either } from "fp-ts/Either";
import { pipe } from "fp-ts/function";
import { SESSION_EXPIRED } from "../../../common/failures/AppFailure";
import type { AppFailure } from "../../../common/failures/AppFailure";
import { Invitation } from "../models/Invitation";
import { emptyDraft, submissionFromDraft } from "../models/InvitationDraft";
import type { InvitationDraft } from "../models/InvitationDraft";
import type { InvitationFlags } from "../models/InvitationFlags";
import type { TeamMember } from "../models/TeamMember";
import type { IInvitationService } from "../services/IInvitationService";
import type { ISessionService } from "../services/ISessionService";
import type { InvitationsEvent } from "./InvitationsEvent";
import {
  FlowFailed,
  FlowIdle,
  FlowLoaded,
  FlowLoading,
  FlowSubmitting,
  SessionAuthenticated,
  SessionChecking,
  SessionFailed,
  SessionIdle,
  SessionSignedOut,
  idleDirectory,
} from "./InvitationsState";
import type { FlowState, SessionState } from "./InvitationsState";
import { deriveView } from "./InvitationsView";
import type { InvitationsView } from "./InvitationsView";

/** Everything presentation needs to render, as one immutable value. */
export interface InvitationsSnapshot {
  readonly sessionState: SessionState;
  readonly flowState: FlowState;
  readonly draft: InvitationDraft;
  readonly view: InvitationsView;
}

export interface InvitationsManagerOptions {
  readonly sessionService: ISessionService;
  readonly invitationService: IInvitationService;
  readonly expiryEnabled: boolean;
  readonly onChange: (snapshot: InvitationsSnapshot) => void;
}

/**
 * FE-MGR-1: a plain class with no UI framework import. Events come in through
 * `emit`, snapshots go out through `onChange`, and a unit test can drive it with
 * fake services. The promise `emit` returns settles when the event is fully
 * handled; presentation ignores it and tests await it.
 */
export class InvitationsManager {
  private sessionState: SessionState = new SessionIdle();
  private flowState: FlowState = new FlowIdle();
  private draft: InvitationDraft = emptyDraft;
  private readonly sessionService: ISessionService;
  private readonly invitationService: IInvitationService;
  private readonly flags: InvitationFlags;
  private readonly onChange: (snapshot: InvitationsSnapshot) => void;

  constructor({ sessionService, invitationService, expiryEnabled, onChange }: InvitationsManagerOptions) {
    this.sessionService = sessionService;
    this.invitationService = invitationService;
    this.flags = { expiryEnabled };
    this.onChange = onChange;
  }

  get snapshot(): InvitationsSnapshot {
    const { sessionState, flowState, draft, flags } = this;
    return { sessionState, flowState, draft, view: deriveView({ sessionState, flowState, draft, flags }) };
  }

  async emit(event: InvitationsEvent): Promise<void> {
    // FE-STATE-3: a new event without a case here fails the type check in `assertNever`.
    switch (event.kind) {
      case "SessionRequested":
        return this.checkSession();
      case "InvitationsRequested":
        return this.loadInvitations(event.teamId);
      case "DirectorySearchRequested":
        return this.searchDirectory(event.query);
      case "DraftChanged":
        return this.changeDraft(event.draft);
      case "SubmitRequested":
        return this.submit();
      case "RevokeRequested":
        return this.revoke(event.invitationId);
      default:
        return assertNever(event);
    }
  }

  private async checkSession(): Promise<void> {
    this.updateSession(() => new SessionChecking());
    const result = await this.sessionService.readSession();
    this.updateSession((current) => {
      // FE-MGR-3: a flow request may have found the session expired while this read was in flight.
      if (current.kind !== "SessionChecking") {
        return current;
      }
      return pipe(
        result,
        match<AppFailure, TeamMember, SessionState>(
          // FE-SVC-2: branch on the code, never on the message text.
          (failure) => (failure.code === SESSION_EXPIRED ? new SessionSignedOut() : new SessionFailed(failure)),
          (user) => new SessionAuthenticated(user),
        ),
      );
    });
  }

  private async loadInvitations(teamId: string): Promise<void> {
    // FE-STATE-6: a submission owns the flow until it settles.
    if (this.flowState.kind === "FlowSubmitting") {
      return;
    }
    // FE-STATE-7: whatever was loaded before is dropped the moment the key is requested.
    this.updateFlow(() => new FlowLoading(teamId));
    const result = await this.invitationService.loadInvitations(teamId);
    this.updateFlow((current) => {
      // FE-MGR-3: another team may have been requested while this one was in flight.
      if (current.kind !== "FlowLoading" || current.teamId !== teamId) {
        return current;
      }
      return pipe(
        result,
        match<AppFailure, readonly Invitation[], FlowState>(
          (failure) => new FlowFailed(failure, teamId, []),
          (invitations) => new FlowLoaded(teamId, invitations, idleDirectory),
        ),
      );
    });
    this.signOutIfExpired(result);
  }

  private async searchDirectory(query: string): Promise<void> {
    const loaded = this.flowState;
    // Not loaded covers FE-STATE-6 too: a search requested mid-submit is ignored.
    if (loaded.kind !== "FlowLoaded") {
      return;
    }
    // FE-STATE-5: searching is a field of the loaded state. The previous members
    // belong to another query, so they are not carried over (FE-STATE-7).
    this.updateFlow(() => loaded.withDirectory({ query, status: "searching", members: [] }));
    const result = await this.invitationService.searchDirectory(loaded.teamId, query);
    this.updateFlow((current) => {
      // FE-MGR-3 and FE-STATE-6: the result applies only if this exact search is
      // still the one on screen. A submission, a reload or a newer query wins.
      if (current.kind !== "FlowLoaded" || current.teamId !== loaded.teamId || current.directory.query !== query) {
        return current;
      }
      return pipe(
        result,
        match<AppFailure, readonly TeamMember[], FlowState>(
          (failure) => new FlowFailed(failure, current.teamId, current.invitations),
          (members) => current.withDirectory({ query, status: "loaded", members }),
        ),
      );
    });
    this.signOutIfExpired(result);
  }

  private changeDraft(draft: InvitationDraft): void {
    this.draft = draft;
    this.onChange(this.snapshot);
  }

  private async submit(): Promise<void> {
    const loaded = this.flowState;
    // FE-MGR-2: the manager decides whether a submission may start, with the same
    // derivation the button is rendered from.
    if (loaded.kind !== "FlowLoaded" || !this.snapshot.view.canSubmit) {
      return;
    }
    const submission = submissionFromDraft(this.draft, this.flags);
    await this.write(loaded, () => this.invitationService.createInvitation(loaded.teamId, submission));
  }

  private async revoke(invitationId: string): Promise<void> {
    const loaded = this.flowState;
    if (loaded.kind !== "FlowLoaded") {
      return;
    }
    // Only a pending invitation can be revoked; the API answers 400 for any other.
    const target = loaded.invitations.find((invitation) => invitation.id === invitationId);
    if (target === undefined || !Invitation.isPending(target)) {
      return;
    }
    await this.write(loaded, () => this.invitationService.revokeInvitation(invitationId));
  }

  private async write(
    loaded: FlowLoaded,
    request: () => Promise<Either<AppFailure, readonly Invitation[]>>,
  ): Promise<void> {
    this.updateFlow(() => new FlowSubmitting(loaded.teamId, loaded.invitations));
    const result = await request();
    this.updateFlow((current) => {
      if (current.kind !== "FlowSubmitting") {
        return current;
      }
      return pipe(
        result,
        match<AppFailure, readonly Invitation[], FlowState>(
          (failure) => new FlowFailed(failure, current.teamId, current.invitations),
          // CT-5: the write answers with the full list, which replaces the old one.
          (invitations) => new FlowLoaded(current.teamId, invitations, idleDirectory),
        ),
      );
    });
    this.signOutIfExpired(result);
  }

  /** FE-STATE-4: any service can discover a dead session; that changes the session union only. */
  private signOutIfExpired(result: Either<AppFailure, unknown>): void {
    if (isLeft(result) && result.left.code === SESSION_EXPIRED) {
      this.updateSession(() => new SessionSignedOut());
    }
  }

  /** FE-MGR-3: every transition is a function of the state at the moment it is applied. */
  private updateFlow(next: (current: FlowState) => FlowState): void {
    this.flowState = next(this.flowState);
    this.onChange(this.snapshot);
  }

  private updateSession(next: (current: SessionState) => SessionState): void {
    this.sessionState = next(this.sessionState);
    this.onChange(this.snapshot);
  }
}

function assertNever(event: never): never {
  throw new Error(`Unhandled event: ${JSON.stringify(event)}`);
}
