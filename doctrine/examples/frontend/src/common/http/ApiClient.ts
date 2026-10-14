import { clearAuthTokens, readAccessToken, readRefreshToken, writeAccessToken } from "../auth/AuthStorage";
import { HttpError } from "./HttpError";

export interface TransportRequest {
  readonly method: string;
  readonly headers: Readonly<Record<string, string>>;
  readonly body?: string;
}

/** The seam tests replace. The default is the only `fetch` call in the client (FE-SVC-4). */
export type Transport = (url: string, request: TransportRequest) => Promise<Response>;

export interface JsonRequest {
  readonly method?: "GET" | "POST";
  readonly query?: Readonly<Record<string, string>>;
  readonly body?: unknown;
}

export interface ApiClientOptions {
  readonly baseUrl: string;
  readonly storage: Storage;
  readonly transport?: Transport;
}

const REFRESH_PATH = "/api/auth/token/refresh/";

/**
 * FE-SVC-4: the one place that builds URLs, sets headers, parses the error
 * contract and applies authentication. Services call it; nothing else calls `fetch`.
 */
export class ApiClient {
  private readonly baseUrl: string;
  private readonly storage: Storage;
  private readonly transport: Transport;

  constructor({ baseUrl, storage, transport = (url, request) => fetch(url, request) }: ApiClientOptions) {
    this.baseUrl = baseUrl;
    this.storage = storage;
    this.transport = transport;
  }

  requestJson<T>(path: string, request: JsonRequest = {}): Promise<T> {
    return this.send<T>(path, request, null);
  }

  /**
   * FE-SVC-5: refresh once on 401 and retry once. Tokens are cleared only when the
   * session is provably dead: no refresh token, a rejected refresh, or a second 401.
   * Every other failure is rethrown with the tokens intact.
   */
  async requestAuthenticatedJson<T>(path: string, request: JsonRequest = {}): Promise<T> {
    const access = readAccessToken(this.storage);
    if (access === null) {
      throw sessionExpired();
    }
    try {
      return await this.send<T>(path, request, access);
    } catch (error) {
      if (!hasStatus(error, 401)) {
        throw error;
      }
    }
    const refreshed = await this.refreshAccessToken();
    try {
      return await this.send<T>(path, request, refreshed);
    } catch (error) {
      if (hasStatus(error, 401)) {
        clearAuthTokens(this.storage);
      }
      throw error;
    }
  }

  private async refreshAccessToken(): Promise<string> {
    const refresh = readRefreshToken(this.storage);
    if (refresh === null) {
      clearAuthTokens(this.storage);
      throw sessionExpired();
    }
    try {
      const body = await this.requestJson<{ access: string }>(REFRESH_PATH, { method: "POST", body: { refresh } });
      writeAccessToken(this.storage, body.access);
      return body.access;
    } catch (error) {
      // A 503 or a network error says nothing about the session, so the tokens stay.
      if (hasStatus(error, 401) || hasStatus(error, 403)) {
        clearAuthTokens(this.storage);
        throw sessionExpired();
      }
      throw error;
    }
  }

  private async send<T>(path: string, request: JsonRequest, access: string | null): Promise<T> {
    const response = await this.transport(this.url(path, request.query), {
      method: request.method ?? "GET",
      headers: {
        Accept: "application/json",
        ...(request.body === undefined ? {} : { "Content-Type": "application/json" }),
        ...(access === null ? {} : { Authorization: `Bearer ${access}` }),
      },
      ...(request.body === undefined ? {} : { body: JSON.stringify(request.body) }),
    });
    if (!response.ok) {
      throw new HttpError(response.status, await errorMessage(response));
    }
    try {
      return (await response.json()) as T;
    } catch {
      // A 2xx that is not JSON (a proxy page, an empty body) is an error, not a crash.
      throw new HttpError(response.status, "The server sent an unexpected response.");
    }
  }

  private url(path: string, query: Readonly<Record<string, string>> = {}): string {
    const search = new URLSearchParams(query).toString();
    return `${this.baseUrl}${path}${search === "" ? "" : `?${search}`}`;
  }
}

/** CT-1: the API has one error shape, `{"error": "<message>"}`. Anything else gets a status-based message. */
async function errorMessage(response: Response): Promise<string> {
  const body: unknown = await response.json().catch(() => null);
  if (typeof body === "object" && body !== null && "error" in body && typeof body.error === "string") {
    return body.error;
  }
  return `The request failed (HTTP ${response.status}).`;
}

function hasStatus(error: unknown, status: number): boolean {
  return error instanceof HttpError && error.status === status;
}

function sessionExpired(): HttpError {
  return new HttpError(401, "Your session has expired. Sign in again.");
}
