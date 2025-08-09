interface EventPayload {
  [key: string]: unknown;
}

// Simple analytics tracker placeholder. In production this would send events
// to a telemetry backend.
export function track(event: string, payload: EventPayload): void {
  // eslint-disable-next-line no-console
  console.log('track', event, payload);
}
