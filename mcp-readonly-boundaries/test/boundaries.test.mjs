import assert from 'node:assert/strict';
import { before, after, test } from 'node:test';
import { catalogue } from '../catalogue.mjs';
import { readPublicDocument, MAX_CONTENT_BYTES } from '../policy.mjs';
import { connect } from '../client.mjs';

let client;
let errors;
const initialCatalogue = JSON.stringify([...catalogue]);
before(async () => { ({ client, errors } = await connect()); });
after(async () => { await client?.close(); });
const read = (documentId, extra = {}) => client.callTool({ name: 'get_public_doc', arguments: { documentId, ...extra } });
const body = result => JSON.parse(result.content[0].text);

test('advertises one bounded read tool, not a generic file reader', async () => {
  const { tools } = await client.listTools();
  assert.deepEqual(tools.map(tool => tool.name), ['get_public_doc']);
  assert.equal(tools[0].annotations.readOnlyHint, true);
  assert.equal(tools[0].inputSchema.additionalProperties, false);
  assert.deepEqual(tools[0].inputSchema.required, ['documentId']);
});

test('returns the exact approved document', async () => {
  const result = await read('getting-started');
  assert.notEqual(result.isError, true);
  assert.deepEqual(body(result), {
    documentId: 'getting-started',
    title: 'Getting started',
    body: 'Create a sandbox project, then request a test API key. Never paste a production key into a support ticket.',
  });
  assert.ok(Buffer.byteLength(result.content[0].text, 'utf8') <= MAX_CONTENT_BYTES);
});

test('private and nonexistent document IDs receive the same application error', async () => {
  const privateResult = await read('internal-notes');
  const missingResult = await read('missing-doc');
  assert.equal(privateResult.isError, true);
  assert.deepEqual(privateResult, missingResult);
  assert.equal(body(privateResult).code, 'DOCUMENT_NOT_AVAILABLE');
  assert.doesNotMatch(JSON.stringify(privateResult), /PRIVATE_FIXTURE_DO_NOT_EXPORT/);
});

for (const [name, arguments_] of [
  ['relative traversal', { documentId: '../internal-notes' }],
  ['absolute path', { documentId: '/etc/passwd' }],
  ['URL', { documentId: 'https://example.com' }],
  ['non-string ID', { documentId: 42 }],
  ['oversized ID', { documentId: 'a'.repeat(65) }],
  ['extra path argument', { documentId: 'getting-started', path: '../internal-notes' }],
]) {
  test(`rejects ${name} through the MCP schema`, async () => {
    const result = await client.callTool({ name: 'get_public_doc', arguments: arguments_ });
    assert.equal(result.isError, true);
    assert.doesNotMatch(JSON.stringify(result), /PRIVATE_FIXTURE_DO_NOT_EXPORT/);
  });
}

test('blocks an allowed document whose UTF-8 payload exceeds the limit', async () => {
  assert.ok(catalogue.get('oversized-fixture').body.length < MAX_CONTENT_BYTES);
  assert.ok(Buffer.byteLength(catalogue.get('oversized-fixture').body, 'utf8') > MAX_CONTENT_BYTES);
  const result = await read('oversized-fixture');
  assert.equal(result.isError, true);
  assert.equal(body(result).code, 'DOCUMENT_TOO_LARGE');
  assert.ok(Buffer.byteLength(result.content[0].text, 'utf8') <= MAX_CONTENT_BYTES);
});

test('an unknown tool is a protocol error, not a successful empty result', async () => {
  await assert.rejects(() => client.callTool({ name: 'read_any_file', arguments: {} }));
});

test('a valid read still works after rejected requests', async () => {
  assert.equal(body(await read('rate-limits')).documentId, 'rate-limits');
  assert.deepEqual(errors, []);
});

test('policy calls leave the local synthetic catalogue unchanged', () => {
  readPublicDocument('getting-started');
  readPublicDocument('internal-notes');
  assert.equal(JSON.stringify([...catalogue]), initialCatalogue);
});
