import { left, right } from "fp-ts/Either";
import type { Either } from "fp-ts/Either";
import { describe, expect, it } from "vitest";
import { AppFailure, SESSION_EXPIRED } from "../../../common/failures/AppFailure";
import { ResultQueue } from "../../../common/testing/ResultQueue";
import type { Invitation } from "../models/Invitation";
import { emptyDraft } from "../models/InvitationDraft";
import type { InvitationDraft, InvitationSubmission } from "../models/InvitationDraft";
import type { TeamMember } from "../models/TeamMember";
import {
  DIRECTORY_SEARCH_FAILED,
  INVITATION_SUBMIT_FAILED,
  INVITATIONS_LOAD_FAILED,
} from "../services/IInvitationService";
import type { IInvitationService } from "../services/IInvitationService";
import { SESSION_READ_FAILED } from "../services/ISessionService";
import type { ISessionService } from "../services/ISessionService";
import {
  DirectorySearchRequested,
  DraftChanged,
  InvitationsRequested,
  RevokeRequested,
  SessionRequested,
  SubmitRequested,
} from "./InvitationsEvent";
import type { InvitationsEvent } from "./InvitationsEvent";
import { InvitationsManager } from "./InvitationsManager";
import type { InvitationsSnapshot } from "./InvitationsManager";
import {
  FlowFailed,
  FlowLoaded,
  FlowLoading,
  FlowSubmitting,
  SessionAuthenticated,
  SessionChecking,
  SessionFailed,
  SessionSignedOut,
  idleDirectory,
} from "./InvitationsState";

type InvitationsResult = Either<AppFailure, readonly Invitation[]>;

/** T-4: each method answers from its own queue, so an unexpected call throws. */
class FakeSessionService implements ISessionService {
  readonly results = new ResultQueue<Either<AppFailure, TeamMember>>("readSession");

  readSession() {
    return this.results.next();
  }
}

class FakeInvitationService implements IInvitationService {
  readonly calls: unknown[][] = [];
  readonly loads = new ResultQueue<InvitationsResult>("loadInvitations");
  readonly creates = new ResultQueue<InvitationsResult>("createInvitation");
  readonly revokes = new ResultQueue<InvitationsResult>("revokeInvitation");
  readonly searches = new ResultQueue<Either<AppFailure, readonly TeamMember[]>>("searchDirectory");

  loadInvitations(teamId: string) {
    this.calls.push(["loadInvitations", teamId]);
    return this.loads.next();
  }

  createInvitation(teamId: string, submission: InvitationSubmission) {
    this.calls.push(["createInvitation", teamId, submission]);
    return this.creates.next();
  }

  revokeInvitation(invitationId: string) {
    this.calls.push(["revokeInvitation", invitationId]);
    return this.revokes.next();
  }

  searchDirectory(teamId: string, query: string) {
    this.calls.push(["searchDirectory", teamId, query]);
    return this.searches.next();
  }
}

function invitation(id: string, email: string, status: Invitation["status"] = "pending"): Invitation {
  return {
    id,
    teamId: "team-1",
    email,
    role: "member",
    status,
    message: "",
    expiresAt: null,
    createdAt: "2030-01-01T09:00:00+00:00",
  };
}

const owner: TeamMember = { id: "user-1", email: "owner@example.com", name: "Owner" };
const ben: TeamMember = { id: "user-2", email: "ben@example.com", name: "Ben" };
const ana = invitation("inv-1", "ana@example.com");
const revoked = invitation("inv-2", "old@example.com", "revoked");
const dee = invitation("inv-3", "dee@example.com");
const deeDraft: InvitationDraft = { ...emptyDraft, email: "dee@example.com" };

function setup({ expiryEnabled = false } = {}) {
  const sessionService = new FakeSessionService();
  const invitationService = new FakeInvitationService();
  const changes: InvitationsSnapshot[] = [];
  const manager = new InvitationsManager({
    sessionService,
    invitationService,
    expiryEnabled,
    onChange: (snapshot) => changes.push(snapshot),
  });
  return { manager, sessionService, invitationService, changes };
}

/** An authenticated session with team-1 loaded: one pending and one revoked invitation. */
async function setupLoaded(options: { expiryEnabled?: boolean } = {}) {
  const context = setup(options);
  context.sessionService.results.resolveNext(right(owner));
  context.invitationService.loads.resolveNext(right([ana, revoked]));
  await context.manager.emit(new SessionRequested());
  await context.manager.emit(new InvitationsRequested("team-1"));
  context.invitationService.calls.length = 0;
  context.changes.length = 0;
  return context;
}

/** A valid submission for dee is in flight; `settleCreate` lets the test decide when it lands. */
async function setupSubmitting() {
  const context = await setupLoaded();
  const settleCreate = context.invitationService.creates.deferNext();
  await context.manager.emit(new DraftChanged(deeDraft));
  const submitted = context.manager.emit(new SubmitRequested());
  return { ...context, settleCreate, submitted };
}

describe("InvitationsManager session", () => {
  it("moves through SessionChecking to SessionAuthenticated with the user", async () => {
    const { manager, sessionService, changes } = setup();
    sessionService.results.resolveNext(right(owner));

    await manager.emit(new SessionRequested());

    expect(changes.map((change) => change.sessionState)).toEqual([
      new SessionChecking(),
      new SessionAuthenticated(owner),
    ]);
  });

  it("moves to SessionSignedOut when the session read fails with SESSION_EXPIRED", async () => {
    const { manager, sessionService } = setup();
    sessionService.results.resolveNext(left(new AppFailure(SESSION_EXPIRED, "Your session has expired.")));

    await manager.emit(new SessionRequested());

    expect(manager.snapshot.sessionState).toEqual(new SessionSignedOut());
  });

  it("moves to SessionFailed with the failure when the session read fails for another reason", async () => {
    const { manager, sessionService } = setup();
    const failure = new AppFailure(SESSION_READ_FAILED, "Your session could not be checked.");
    sessionService.results.resolveNext(left(failure));

    await manager.emit(new SessionRequested());

    expect(manager.snapshot.sessionState).toEqual(new SessionFailed(failure));
  });

  it("stays SessionSignedOut when the session read lands after a flow request found the session expired", async () => {
    const { manager, sessionService, invitationService } = setup();
    const settleSession = sessionService.results.deferNext();
    invitationService.loads.resolveNext(left(new AppFailure(SESSION_EXPIRED, "Your session has expired.")));
    const checked = manager.emit(new SessionRequested());
    await manager.emit(new InvitationsRequested("team-1"));

    settleSession(right(owner));
    await checked;

    expect(manager.snapshot.sessionState).toEqual(new SessionSignedOut());
  });

  it("signs the session out when a flow request fails with SESSION_EXPIRED", async () => {
    const { manager, invitationService } = await setupLoaded();
    const failure = new AppFailure(SESSION_EXPIRED, "Your session has expired.");
    invitationService.searches.resolveNext(left(failure));

    await manager.emit(new DirectorySearchRequested("ben"));

    expect(manager.snapshot.sessionState).toEqual(new SessionSignedOut());
    expect(manager.snapshot.flowState).toEqual(new FlowFailed(failure, "team-1", [ana, revoked]));
  });
});

describe("InvitationsManager loading", () => {
  it("moves through FlowLoading for the team to FlowLoaded with its invitations and an idle directory", async () => {
    const { manager, invitationService, changes } = setup();
    invitationService.loads.resolveNext(right([ana]));

    await manager.emit(new InvitationsRequested("team-1"));

    expect(changes.map((change) => change.flowState)).toEqual([
      new FlowLoading("team-1"),
      new FlowLoaded("team-1", [ana], idleDirectory),
    ]);
    expect(invitationService.calls).toEqual([["loadInvitations", "team-1"]]);
  });

  it("moves to FlowFailed with the failure, the team and no invitations when the load fails", async () => {
    const { manager, invitationService } = setup();
    const failure = new AppFailure(INVITATIONS_LOAD_FAILED, "The invitations could not be loaded.");
    invitationService.loads.resolveNext(left(failure));

    await manager.emit(new InvitationsRequested("team-1"));

    expect(manager.snapshot.flowState).toEqual(new FlowFailed(failure, "team-1", []));
  });

  it("exposes no invitations while a different team is loading", async () => {
    const { manager, invitationService } = await setupLoaded();
    invitationService.loads.deferNext();

    void manager.emit(new InvitationsRequested("team-2"));

    expect(manager.snapshot.flowState).toEqual(new FlowLoading("team-2"));
    expect(manager.snapshot.view.pendingCount).toBe(0);
  });

  it("drops the first team's result when it arrives after a second team was requested", async () => {
    const { manager, invitationService } = setup();
    const settleTeam1 = invitationService.loads.deferNext();
    const settleTeam2 = invitationService.loads.deferNext();
    const team1 = manager.emit(new InvitationsRequested("team-1"));
    const team2 = manager.emit(new InvitationsRequested("team-2"));

    settleTeam1(right([ana]));
    await team1;

    expect(manager.snapshot.flowState).toEqual(new FlowLoading("team-2"));

    settleTeam2(right([]));
    await team2;

    expect(manager.snapshot.flowState).toEqual(new FlowLoaded("team-2", [], idleDirectory));
  });
});

describe("InvitationsManager directory search", () => {
  it("searches as sub-state of FlowLoaded, keeping the invitations, then holds the members", async () => {
    const { manager, invitationService, changes } = await setupLoaded();
    invitationService.searches.resolveNext(right([ben]));

    await manager.emit(new DirectorySearchRequested("ben"));

    expect(changes.map((change) => change.flowState)).toEqual([
      new FlowLoaded("team-1", [ana, revoked], { query: "ben", status: "searching", members: [] }),
      new FlowLoaded("team-1", [ana, revoked], { query: "ben", status: "loaded", members: [ben] }),
    ]);
    expect(invitationService.calls).toEqual([["searchDirectory", "team-1", "ben"]]);
  });

  it("drops the result of an older query when a newer query is searching", async () => {
    const { manager, invitationService } = await setupLoaded();
    const settleOlder = invitationService.searches.deferNext();
    invitationService.searches.deferNext();
    const older = manager.emit(new DirectorySearchRequested("b"));
    void manager.emit(new DirectorySearchRequested("be"));

    settleOlder(right([ben]));
    await older;

    expect(manager.snapshot.flowState).toEqual(
      new FlowLoaded("team-1", [ana, revoked], { query: "be", status: "searching", members: [] }),
    );
  });

  it("drops a search result for another team even when the query text is the same", async () => {
    const { manager, invitationService } = await setupLoaded();
    const settleTeam1 = invitationService.searches.deferNext();
    invitationService.loads.resolveNext(right([]));
    invitationService.searches.deferNext();
    const team1Search = manager.emit(new DirectorySearchRequested("ben"));
    await manager.emit(new InvitationsRequested("team-2"));
    void manager.emit(new DirectorySearchRequested("ben"));

    settleTeam1(right([ben]));
    await team1Search;

    expect(manager.snapshot.flowState).toEqual(
      new FlowLoaded("team-2", [], { query: "ben", status: "searching", members: [] }),
    );
  });

  it("moves to FlowFailed keeping the invitations when the search fails", async () => {
    const { manager, invitationService } = await setupLoaded();
    const failure = new AppFailure(DIRECTORY_SEARCH_FAILED, "The team directory could not be searched.");
    invitationService.searches.resolveNext(left(failure));

    await manager.emit(new DirectorySearchRequested("ben"));

    expect(manager.snapshot.flowState).toEqual(new FlowFailed(failure, "team-1", [ana, revoked]));
    expect(manager.snapshot.sessionState).toEqual(new SessionAuthenticated(owner));
  });
});

describe("InvitationsManager submitting", () => {
  it("moves through FlowSubmitting to FlowLoaded with the snapshot, sending no expiry when the flag is off", async () => {
    const { manager, invitationService, changes } = await setupLoaded({ expiryEnabled: false });
    invitationService.creates.resolveNext(right([ana, revoked, dee]));
    await manager.emit(new DraftChanged({ ...deeDraft, expiresOn: "2030-01-31" }));
    changes.length = 0;

    await manager.emit(new SubmitRequested());

    expect(changes.map((change) => change.flowState)).toEqual([
      new FlowSubmitting("team-1", [ana, revoked]),
      new FlowLoaded("team-1", [ana, revoked, dee], idleDirectory),
    ]);
    expect(invitationService.calls).toEqual([
      ["createInvitation", "team-1", { email: "dee@example.com", role: "member" }],
    ]);
  });

  it("sends the expiry when the flag is on", async () => {
    const { manager, invitationService } = await setupLoaded({ expiryEnabled: true });
    invitationService.creates.resolveNext(right([ana, revoked, dee]));
    await manager.emit(new DraftChanged({ ...deeDraft, expiresOn: "2030-01-31" }));

    await manager.emit(new SubmitRequested());

    expect(invitationService.calls).toEqual([
      [
        "createInvitation",
        "team-1",
        { email: "dee@example.com", role: "member", expiresAt: "2030-01-31T23:59:59+00:00" },
      ],
    ]);
  });

  it("makes no request and keeps the state when the draft is invalid or already invited", async () => {
    const { manager, invitationService, changes } = await setupLoaded();

    await manager.emit(new SubmitRequested());
    await manager.emit(new DraftChanged({ ...emptyDraft, email: "ana@example.com" }));
    await manager.emit(new SubmitRequested());

    expect(invitationService.calls).toEqual([]);
    expect(changes.map((change) => change.flowState.kind)).toEqual(["FlowLoaded"]);
  });

  it("moves to FlowFailed keeping the invitations when the submission fails", async () => {
    const { manager, settleCreate, submitted } = await setupSubmitting();
    const failure = new AppFailure(INVITATION_SUBMIT_FAILED, "Enter a valid email address");

    settleCreate(left(failure));
    await submitted;

    expect(manager.snapshot.flowState).toEqual(new FlowFailed(failure, "team-1", [ana, revoked]));
  });

  it("ignores load, search, submit and revoke requests while submitting", async () => {
    const { manager, invitationService, changes } = await setupSubmitting();
    const submitting = manager.snapshot.flowState;
    invitationService.calls.length = 0;
    changes.length = 0;

    await manager.emit(new InvitationsRequested("team-1"));
    await manager.emit(new DirectorySearchRequested("ben"));
    await manager.emit(new SubmitRequested());
    await manager.emit(new RevokeRequested("inv-1"));

    expect(invitationService.calls).toEqual([]);
    expect(changes).toEqual([]);
    expect(manager.snapshot.flowState).toBe(submitting);
    expect(submitting).toEqual(new FlowSubmitting("team-1", [ana, revoked]));
  });

  it("stays FlowSubmitting when a directory search succeeds mid-submit", async () => {
    const context = await setupLoaded();
    const settleSearch = context.invitationService.searches.deferNext();
    const settleCreate = context.invitationService.creates.deferNext();
    const searched = context.manager.emit(new DirectorySearchRequested("ben"));
    await context.manager.emit(new DraftChanged(deeDraft));
    const submitted = context.manager.emit(new SubmitRequested());
    const submitting = context.manager.snapshot.flowState;

    settleSearch(right([ben]));
    await searched;

    expect(submitting).toEqual(new FlowSubmitting("team-1", [ana, revoked]));
    expect(context.manager.snapshot.flowState).toBe(submitting);

    settleCreate(right([ana, revoked, dee]));
    await submitted;

    expect(context.manager.snapshot.flowState).toEqual(new FlowLoaded("team-1", [ana, revoked, dee], idleDirectory));
  });

  it("stays FlowSubmitting when a directory search fails mid-submit", async () => {
    const context = await setupLoaded();
    const settleSearch = context.invitationService.searches.deferNext();
    context.invitationService.creates.deferNext();
    const searched = context.manager.emit(new DirectorySearchRequested("ben"));
    await context.manager.emit(new DraftChanged(deeDraft));
    void context.manager.emit(new SubmitRequested());
    const submitting = context.manager.snapshot.flowState;

    settleSearch(left(new AppFailure(DIRECTORY_SEARCH_FAILED, "The team directory could not be searched.")));
    await searched;

    expect(submitting).toEqual(new FlowSubmitting("team-1", [ana, revoked]));
    expect(context.manager.snapshot.flowState).toBe(submitting);
  });
});

describe("InvitationsManager revoking", () => {
  it("moves through FlowSubmitting to FlowLoaded with the returned snapshot", async () => {
    const { manager, invitationService, changes } = await setupLoaded();
    const afterRevoke = [{ ...ana, status: "revoked" as const }, revoked];
    invitationService.revokes.resolveNext(right(afterRevoke));

    await manager.emit(new RevokeRequested("inv-1"));

    expect(changes.map((change) => change.flowState)).toEqual([
      new FlowSubmitting("team-1", [ana, revoked]),
      new FlowLoaded("team-1", afterRevoke, idleDirectory),
    ]);
    expect(invitationService.calls).toEqual([["revokeInvitation", "inv-1"]]);
  });

  it("makes no request for an invitation that is not pending or not in the list", async () => {
    const { manager, invitationService, changes } = await setupLoaded();

    await manager.emit(new RevokeRequested("inv-2"));
    await manager.emit(new RevokeRequested("inv-404"));

    expect(invitationService.calls).toEqual([]);
    expect(changes).toEqual([]);
  });
});

describe("InvitationsManager dispatch", () => {
  it("rejects an event whose kind it does not know", async () => {
    const { manager } = setup();
    const unknown = { kind: "ThemeToggled" } as unknown as InvitationsEvent;

    await expect(manager.emit(unknown)).rejects.toThrow("Unhandled event");
  });
});
