import { createServer } from 'node:http';
import { once } from 'node:events';
import test from 'node:test';
import assert from 'node:assert/strict';
import { getJson } from './client.mjs';

test('HTTP JSON client against a local server', async (t) => {
  const server = createServer((req, res) => {
    if (req.url === '/slow') return; // Intentionally waits until client aborts.
    if (req.url === '/error') { res.writeHead(503).end('Unavailable'); return; }
    if (req.url === '/empty') { res.writeHead(204).end(); return; }
    if (req.url === '/redirect') { res.writeHead(302, { Location: '/ok' }).end(); return; }
    if (req.url === '/invalid') { res.writeHead(200, { 'Content-Type': 'application/json' }).end('{'); return; }
    res.writeHead(200, { 'Content-Type': 'application/json' }).end('{"status":"ok"}');
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(async () => {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  await t.test('parses JSON', async () => assert.deepEqual(await getJson(`${base}/ok`), { status: 'ok' }));
  await t.test('handles no content', async () => assert.equal(await getJson(`${base}/empty`), null));
  await t.test('rejects HTTP failures', async () => assert.rejects(getJson(`${base}/error`), /HTTP 503/));
  await t.test('rejects invalid JSON', async () => assert.rejects(getJson(`${base}/invalid`), SyntaxError));
  await t.test('rejects redirects', async () => assert.rejects(getJson(`${base}/redirect`), TypeError));
  await t.test('aborts slow requests', async () => assert.rejects(getJson(`${base}/slow`, { timeoutMs: 50 }), { name: 'TimeoutError' }));
  await t.test('validates timeout', async () => assert.rejects(getJson(`${base}/ok`, { timeoutMs: 0 }), RangeError));
});
