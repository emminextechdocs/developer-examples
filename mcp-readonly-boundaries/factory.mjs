import { McpServer } from '@modelcontextprotocol/server';
import * as z from 'zod/v4';
import { readPublicDocument } from './policy.mjs';

export function createServer() {
  const server = new McpServer({ name: 'public-docs', version: '1.0.0' });
  server.registerTool('get_public_doc', {
    description: 'Read a public demonstration document by ID. IDs: getting-started, rate-limits, oversized-fixture. The last ID demonstrates a size-limit error. No file paths, URLs, private documents, or writes. Successful JSON text is limited to 4096 UTF-8 bytes.',
    inputSchema: z.strictObject({
      documentId: z.string().min(1).max(64).regex(/^[a-z0-9-]+$/),
    }),
    annotations: { readOnlyHint: true, openWorldHint: false },
  }, async ({ documentId }) => readPublicDocument(documentId));
  return server;
}
