# Build a small HTTP JSON client

This Node.js example focuses on one task: fetch JSON with explicit error handling and a deadline. It uses the built-in `fetch`, `AbortSignal.timeout`, and test runner. No npm dependencies are required.

## 1. Read the implementation

Open [client.mjs](client.mjs). It sends an `Accept: application/json` header, rejects redirects, checks the HTTP status, handles `204 No Content`, and parses a successful response as JSON.

`fetch` does not reject merely because a server returns `404` or `503`. That is why the example checks `response.ok` before parsing. JSON parsing can fail separately, even when the HTTP status is successful.

## 2. Run the tests

From the repository root, using Node.js 22 or 24:

```sh
node --test http-json-client/client.test.mjs
```

Expected result: the success, empty-body, HTTP error, malformed JSON, redirect, timeout, and invalid-configuration cases pass. The test server binds to a temporary port on `127.0.0.1`; it does not create cloud resources. Cleanup runs at the end of the test.

## 3. Use the function

```js
import { getJson } from './client.mjs';

// Replace with a trusted endpoint you control that returns JSON.
const result = await getJson('https://your-api.example/status', { timeoutMs: 3000 });
console.log(result);
```

The URL above is a placeholder, not a service. The runnable tests provide a real local endpoint.

## Before adapting it for production

- Pass only trusted URLs. This example does not implement SSRF defenses for user-supplied addresses.
- Add response-size limits and schema validation appropriate to your API.
- Design authentication without logging tokens or sensitive response bodies.
- Define retry safety per operation. A timeout does not prove that a remote write never happened; this example deliberately makes GET requests only and does not retry.
- Decide whether redirects should be supported and validate every redirect target if needed.
- Report network, parsing, and HTTP errors distinctly in the application UI.

## Official references

- [Node.js fetch](https://nodejs.org/api/globals.html#fetch)
- [Node.js AbortSignal.timeout](https://nodejs.org/api/globals.html#static-method-abortsignaltimeoutdelay)
- [Node.js test runner](https://nodejs.org/api/test.html)
- [MDN: using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
