/** Small GET-only example. Not a retrying SDK or an untrusted-URL proxy. */
export async function getJson(url, { timeoutMs = 5000 } = {}) {
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 60000) {
    throw new RangeError('timeoutMs must be an integer between 1 and 60000');
  }
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(timeoutMs),
    redirect: 'error',
  });
  if (!response.ok) {
    await response.body?.cancel();
    throw new Error(`HTTP ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}
