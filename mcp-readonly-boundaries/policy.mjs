import { catalogue, publicDocumentIds } from './catalogue.mjs';

export const MAX_CONTENT_BYTES = 4096;

function failure(code, message) {
  return { isError: true, content: [{ type: 'text', text: JSON.stringify({ code, message }) }] };
}

export function readPublicDocument(documentId) {
  if (!publicDocumentIds.has(documentId)) {
    return failure('DOCUMENT_NOT_AVAILABLE', 'Choose a public document ID from the tool description.');
  }
  const doc = catalogue.get(documentId);
  if (!doc) {
    return failure('DOCUMENT_NOT_AVAILABLE', 'Choose a public document ID from the tool description.');
  }
  const text = JSON.stringify({ documentId, title: doc.title, body: doc.body });
  if (Buffer.byteLength(text, 'utf8') > MAX_CONTENT_BYTES) {
    return failure('DOCUMENT_TOO_LARGE', 'This document exceeds the export limit. Ask the maintainer for a smaller published section.');
  }
  return { content: [{ type: 'text', text }] };
}
