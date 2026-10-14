// FE-SVC-6: the key strings live here and nowhere else. Signed-in browsers already
// hold tokens under them, so renaming one signs every user out.
const ACCESS_TOKEN_KEY = "acme.auth.access";
const REFRESH_TOKEN_KEY = "acme.auth.refresh";

export interface AuthTokens {
  readonly access: string;
  readonly refresh: string;
}

export function readAccessToken(storage: Storage): string | null {
  return storage.getItem(ACCESS_TOKEN_KEY);
}

export function readRefreshToken(storage: Storage): string | null {
  return storage.getItem(REFRESH_TOKEN_KEY);
}

export function writeAuthTokens(storage: Storage, tokens: AuthTokens): void {
  storage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  storage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
}

export function writeAccessToken(storage: Storage, access: string): void {
  storage.setItem(ACCESS_TOKEN_KEY, access);
}

export function clearAuthTokens(storage: Storage): void {
  storage.removeItem(ACCESS_TOKEN_KEY);
  storage.removeItem(REFRESH_TOKEN_KEY);
}
