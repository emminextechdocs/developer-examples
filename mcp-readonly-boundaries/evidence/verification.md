# Verification record

Date: 11 November 2026. Environment: macOS, Node.js 22.18.0 and 24.10.0. Fixture: synthetic public and internal documentation only.

- `npm test`: 13 passed, 0 failed on Node 22.18.0 and 24.10.0. Actual SDK client spawns the shipped server entry point over stdio. Test output is retained in `tests.txt` and `tests-node24.txt`.
- `npm run demo`: approved document returned; private ID rejected with `DOCUMENT_NOT_AVAILABLE`; oversized allowed fixture rejected with `DOCUMENT_TOO_LARGE`. Output retained in `demo.txt`.
- `npm audit --audit-level=high`: no vulnerabilities reported at verification time. This is a dated package-audit result, not a future security guarantee.
- Temporary mutation: removing the allowlist check fails the private/missing-ID assertion. Restored afterward.
- Temporary mutation: using string length instead of UTF-8 byte length fails the oversized fixture assertion. Restored afterward.
- Final unchanged fixture passes all tests. Mutation outcomes are in `mutation-checks.json`.

## Primary-source checks

- https://ts.sdk.modelcontextprotocol.io/v2/ documents stable split v2 package imports; the installed official npm packages were verified as server/client 2.4.0.
- https://ts.sdk.modelcontextprotocol.io/v2/serving/stdio.html documents `serveStdio(factory)`, stdout protocol use, and cleanup.
- https://ts.sdk.modelcontextprotocol.io/v2/clients/connect.html documents stdio client transport and client lifecycle.
- https://ts.sdk.modelcontextprotocol.io/v2/servers/errors.html documents `isError` tool results; the tests independently observed schema rejections as tool errors and unknown tools as rejected protocol calls.
- https://zod.dev/api?id=objects documents strict object schemas; the extra-argument test verifies their use here.
- https://nodejs.org/api/buffer.html#static-method-bufferbytelengthstring-encoding documents encoding-aware byte measurement; Unicode fixture and mutation checks establish the application's behavior.
- https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ explains that annotations are hints, not enforcement.
- https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization distinguishes HTTP authorization from local stdio credentials.
- https://blog.modelcontextprotocol.io/posts/2026-07-28/ establishes the dated specification work referenced in the article. It does not establish search volume or commercial demand.

## Scope limitations

No AI host evaluation, prompt-injection resistance claim, performance benchmark, remote OAuth implementation, per-user or tenant authorization, adversarial process isolation, full request-size bound, or production deployment test. The payload ceiling applies to the JSON text content, not the complete wire envelope. Direct policy immutability checks inspect a local catalogue; child-process protocol tests inspect responses.
