import { useState } from "react";
import type { InvitationsView } from "../manager/InvitationsView";
import type { InvitationDraft } from "../models/InvitationDraft";
import { ROLES } from "../models/Role";
import { invitationsCopy, roleLabel, submitLabel } from "./invitationsCopy";

interface InvitationFormProps {
  readonly initialDraft: InvitationDraft;
  readonly view: InvitationsView;
  readonly onDraftChange: (draft: InvitationDraft) => void;
  readonly onSubmit: () => void;
}

/**
 * FE-UI-1 and FE-MGR-5: the form owns the text in its inputs and nothing else.
 * It reports the whole draft on every change. Whether the draft can be sent,
 * and whether the expiry field exists, are read from `view`.
 */
export function InvitationForm({ initialDraft, view, onDraftChange, onSubmit }: InvitationFormProps) {
  const [draft, setDraft] = useState(initialDraft);

  function change(changes: Partial<InvitationDraft>): void {
    const next = { ...draft, ...changes };
    setDraft(next);
    onDraftChange(next);
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label>
        {invitationsCopy.email}
        <input type="email" value={draft.email} onChange={(event) => change({ email: event.target.value })} />
      </label>
      <fieldset>
        <legend>{invitationsCopy.role}</legend>
        {ROLES.map((role) => (
          <label key={role}>
            <input type="radio" name="role" checked={draft.role === role} onChange={() => change({ role })} />
            {roleLabel(role)}
          </label>
        ))}
      </fieldset>
      <label>
        {invitationsCopy.message}
        <textarea value={draft.message} onChange={(event) => change({ message: event.target.value })} />
      </label>
      {view.showExpiryField && (
        <label>
          {invitationsCopy.expiresOn}
          <input type="date" value={draft.expiresOn} onChange={(event) => change({ expiresOn: event.target.value })} />
        </label>
      )}
      {/* FE-UI-4: end-to-end tests select on this hook. */}
      <button type="submit" data-testid="invitation-submit" disabled={!view.canSubmit}>
        {submitLabel(view.submitIntent)}
      </button>
    </form>
  );
}
