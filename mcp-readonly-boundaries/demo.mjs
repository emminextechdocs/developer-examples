import { connect } from './client.mjs';
const { client } = await connect();
try {
  for (const documentId of ['getting-started', 'internal-notes', 'oversized-fixture']) {
    const result = await client.callTool({ name: 'get_public_doc', arguments: { documentId } });
    console.log(JSON.stringify({ documentId, isError: result.isError === true, payload: JSON.parse(result.content[0].text) }, null, 2));
  }
} finally { await client.close(); }
