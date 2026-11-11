import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

export async function connect() {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('./server.mjs', import.meta.url))],
    env: {},
    stderr: 'pipe',
  });
  const client = new Client({ name: 'boundary-test-client', version: '1.0.0' }, {
    versionNegotiation: { mode: 'auto' },
  });
  const errors = [];
  transport.stderr?.on('data', chunk => errors.push(chunk.toString()));
  try { await client.connect(transport); }
  catch (error) { await client.close(); throw error; }
  return { client, errors };
}
