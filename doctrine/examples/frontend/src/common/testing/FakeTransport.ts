import type { Transport, TransportRequest } from "../http/ApiClient";
import { ResultQueue } from "./ResultQueue";

export interface RecordedRequest extends TransportRequest {
  readonly url: string;
}

/**
 * T-1: the HTTP client and the services are tested against this instead of the
 * network. It records every request and answers from a queue that throws on an
 * unexpected extra request (T-4).
 */
export class FakeTransport {
  readonly requests: RecordedRequest[] = [];
  private readonly responses = new ResultQueue<Response>("FakeTransport");

  readonly send: Transport = (url, request) => {
    this.requests.push({ url, ...request });
    return this.responses.next();
  };

  respondJson(status: number, body: unknown): void {
    this.responses.resolveNext(new Response(JSON.stringify(body), { status }));
  }

  respondText(status: number, body: string): void {
    this.responses.resolveNext(new Response(body, { status }));
  }

  failNext(error: Error): void {
    this.responses.rejectNext(error);
  }
}
