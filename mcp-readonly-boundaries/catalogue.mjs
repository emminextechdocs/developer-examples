// Synthetic documentation only. This is an export boundary, not a secrets store.
export const catalogue = new Map([
  ['getting-started', {
    title: 'Getting started',
    body: 'Create a sandbox project, then request a test API key. Never paste a production key into a support ticket.',
  }],
  ['rate-limits', {
    title: 'Rate limits',
    body: 'This demonstration API allows 60 requests per minute. A 429 response includes a Retry-After header.',
  }],
  ['oversized-fixture', {
    title: 'Oversized fixture',
    body: '界'.repeat(2000),
  }],
  ['internal-notes', {
    title: 'Internal notes',
    body: 'PRIVATE_FIXTURE_DO_NOT_EXPORT',
  }],
]);

export const publicDocumentIds = new Set([
  'getting-started', 'rate-limits', 'oversized-fixture',
]);
