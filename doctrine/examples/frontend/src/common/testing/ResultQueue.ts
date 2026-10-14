/**
 * T-4: a fake built on this queue fails loudly. Each call takes the next queued
 * result, and a call nobody queued a result for throws instead of returning a default.
 */
export class ResultQueue<T> {
  private readonly queued: Array<() => Promise<T>> = [];

  constructor(private readonly label: string) {}

  resolveNext(result: T): void {
    this.queued.push(() => Promise.resolve(result));
  }

  rejectNext(error: Error): void {
    this.queued.push(() => Promise.reject(error));
  }

  /** Queues a result the test settles later, so events can be emitted while the call is in flight. */
  deferNext(): (result: T) => void {
    const { promise, resolve } = Promise.withResolvers<T>();
    this.queued.push(() => promise);
    return resolve;
  }

  next(): Promise<T> {
    const produce = this.queued.shift();
    if (produce === undefined) {
      throw new Error(`${this.label} was called more times than results were queued`);
    }
    return produce();
  }
}
