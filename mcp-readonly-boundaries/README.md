# Read-only MCP access boundaries

A self-contained, synthetic documentation-reader example from [Emminex Techdocs](https://emminextechdocs.com). It demonstrates explicit document-ID export policy, strict argument validation, a UTF-8 response-size limit, and tests using a real SDK client and child server over stdio.

## Requirements

- Node.js 22 or newer and npm. Verified with Node.js 22.18.0 on macOS on 11 November 2026.
- Dependencies are pinned in `package.json` and `package-lock.json`: `@modelcontextprotocol/server` 2.4.0, `@modelcontextprotocol/client` 2.4.0, Zod 4.6.7.
- No AI model, API keys, cloud account, Docker, or private files are needed. Installation uses npm; the tests and demonstration run locally afterward.

## Run

From this directory:

```bash
npm ci
npm test
npm run demo
```

The verified result is 13 passing tests. `demo` requests a permitted document, a private fixture ID, and an oversized public fixture. Their outcomes are success, `DOCUMENT_NOT_AVAILABLE`, and `DOCUMENT_TOO_LARGE`, respectively. Recorded output is under `evidence/`.

`npm start` starts only the server, which waits for MCP requests on stdin. It is not the demonstration client. Avoid adding `console.log` to the server because stdout carries protocol messages.

## Files

- `catalogue.mjs`: synthetic documents and explicit export allowlist.
- `policy.mjs`: export decision and 4,096-byte maximum for the serialized successful text payload.
- `factory.mjs`: one `get_public_doc` tool with a strict input schema.
- `server.mjs`: the actual stdio entry point.
- `client.mjs`: local client helper and child process connection.
- `test/boundaries.test.mjs`: discovery, exact response, rejected inputs, private-data rejection, Unicode size limit, protocol errors, subsequent valid requests, and direct-policy catalogue immutability checks.
- `demo.mjs`: three readable example calls.

`internal-notes` contains only a test marker, not real confidential information. `oversized-fixture` is deliberately allowed but too large to export. These make rejection behavior observable.

## Limits

This is a public export rule, not per-user authorization. All callers have the same access. Tool annotations do not enforce access rules or sandbox the process. The process has its launching user's OS permissions; the SDK may provide default environment values even when the environment override is empty.

The byte ceiling applies to the JSON string placed in `content[0].text`. It does not bound the full protocol envelope, model tokens, input transport size, or the memory needed to load documents. The tests do not establish prompt-injection resistance, protection from malicious dependencies, or production readiness.

There is no database, file-path input, arbitrary URL fetch, or write tool. Private or remote deployments need their own identity, authorization, tenancy, storage, caching, and operational controls.

## Cleanup

The tests and demo close the client and child process automatically. If you launched `npm start` manually, stop it with Ctrl+C. Removing this example directory removes its local dependencies and fixtures; there are no external resources to delete.

## Sources

- [MCP TypeScript SDK v2](https://ts.sdk.modelcontextprotocol.io/v2/)
- [Stdio server entry point](https://ts.sdk.modelcontextprotocol.io/v2/serving/stdio.html)
- [SDK client connections](https://ts.sdk.modelcontextprotocol.io/v2/clients/connect.html)
- [SDK errors](https://ts.sdk.modelcontextprotocol.io/v2/servers/errors.html)
- [Tool annotations and their limits](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/)
- [MCP authorization](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization)
- [Node Buffer byte length](https://nodejs.org/api/buffer.html#static-method-bufferbytelengthstring-encoding)

Original example code is covered by the repository's [MIT license](../LICENSE). Third-party packages retain their own licenses.
