/** Resolved once at the route and passed inward as plain data (FE-MGR-4). */
export interface InvitationFlags {
  readonly expiryEnabled: boolean;
}

/** The slice of the build environment this experience reads. */
export interface InvitationFlagsEnv {
  readonly VITE_INVITATION_EXPIRY?: string;
}

const ENABLED_VALUES = ["true", "1", "yes"];

/** Off unless the variable is exactly one of the enabling values; `false`, `0`, `no` and anything else are off. */
export function isExpiryEnabled(env: InvitationFlagsEnv): boolean {
  const value = (env.VITE_INVITATION_EXPIRY ?? "").trim().toLowerCase();
  return ENABLED_VALUES.includes(value);
}
