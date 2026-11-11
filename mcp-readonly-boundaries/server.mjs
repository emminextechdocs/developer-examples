import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { createServer } from './factory.mjs';

serveStdio(createServer);
