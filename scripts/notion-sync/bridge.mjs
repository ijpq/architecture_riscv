// Reuse the authenticated local Codex MCP connection; never start a model turn.
import WebSocket from 'ws';

let input = '';
for await (const chunk of process.stdin) input += chunk;
const { endpoint, token, threadId, tool, arguments: args, server = 'notion' } = JSON.parse(input);
if (!endpoint.startsWith('unix://')) throw new Error('A local Unix runtime is required');
const socket = new WebSocket(`ws+unix://${endpoint.slice(7)}:/`, {
    headers: { Host: 'localhost', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    perMessageDeflate: false,
    handshakeTimeout: 5000,
});
let sequence = 0;
const pending = new Map();
function request(method, params) {
    return new Promise((resolve, reject) => {
        const id = ++sequence;
        const timer = setTimeout(() => {
            pending.delete(id);
            reject(new Error(`${method} timed out; do not blindly retry a write`));
        }, 45000);
        pending.set(id, { resolve, reject, timer });
        socket.send(JSON.stringify({ id, method, params }));
    });
}
function rejectPending(error) {
    for (const entry of pending.values()) {
        clearTimeout(entry.timer);
        entry.reject(error);
    }
    pending.clear();
}
socket.on('message', raw => {
    const message = JSON.parse(raw.toString());
    if (message.method || !pending.has(message.id)) return;
    const entry = pending.get(message.id);
    pending.delete(message.id);
    clearTimeout(entry.timer);
    if (message.error) entry.reject(new Error(message.error.message));
    else entry.resolve(message.result);
});
socket.on('error', error => rejectPending(error));
socket.on('close', () => rejectPending(new Error('Runtime connection closed')));
try {
    await new Promise((resolve, reject) => {
        socket.once('open', resolve);
        socket.once('error', reject);
    });
    await request('initialize', {
        clientInfo: { name: 'hapi', title: 'HAPI', version: '1' },
        capabilities: { experimentalApi: true },
    });
    socket.send(JSON.stringify({ method: 'initialized', params: {} }));
    const result = await request('mcpServer/tool/call', {
        threadId, server, tool, arguments: args,
    });
    if (result.isError) throw new Error(JSON.stringify(result.content));
    process.stdout.write(JSON.stringify(result));
} catch (error) {
    console.error(error.message);
    process.exitCode = 1;
} finally {
    socket.close();
}
