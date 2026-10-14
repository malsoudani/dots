// The build-time variables this client reads. Everything here is inlined into
// the bundle and readable by anyone, so it never holds a secret (FE-SVC-9).
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_INVITATION_EXPIRY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
