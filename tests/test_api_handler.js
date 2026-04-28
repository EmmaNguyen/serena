// Validation and security tests for api/chat/index.js (Azure Functions v3 format)
// Uses Node.js built-in test runner (Node >= 18)
// Run: node --test tests/test_api_handler.js

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const handler = require(path.join(__dirname, '..', 'api', 'chat', 'index.js'));

function makeCtx() { return { res: null }; }
function makeReq(body) { return { body: body ?? {} }; }

// Helper: mock fetch + env, run handler, restore
async function withMockAzure(reqBody, mockResponse, fn) {
  const savedEndpoint = process.env.AZURE_OPENAI_ENDPOINT;
  const savedKey      = process.env.AZURE_OPENAI_API_KEY;
  process.env.AZURE_OPENAI_ENDPOINT = 'https://test.openai.azure.com/';
  process.env.AZURE_OPENAI_API_KEY  = 'test-key';

  const captured = {};
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (_url, options) => {
    captured.body    = JSON.parse(options.body);
    captured.headers = options.headers;
    return { status: 200, json: async () => mockResponse };
  };

  try {
    const ctx = makeCtx();
    const req = makeReq(reqBody);
    await handler(ctx, req);
    await fn(ctx, captured);
  } finally {
    globalThis.fetch = origFetch;
    if (savedEndpoint !== undefined) process.env.AZURE_OPENAI_ENDPOINT = savedEndpoint;
    else delete process.env.AZURE_OPENAI_ENDPOINT;
    if (savedKey !== undefined) process.env.AZURE_OPENAI_API_KEY = savedKey;
    else delete process.env.AZURE_OPENAI_API_KEY;
  }
}

// ── Input validation ────────────────────────────────────────────────────────

test('missing messages field returns 400', async () => {
  const ctx = makeCtx();
  await handler(ctx, makeReq({}));
  assert.equal(ctx.res.status, 400);
  assert.equal(ctx.res.body.error, 'messages array required');
});

test('null messages returns 400', async () => {
  const ctx = makeCtx();
  await handler(ctx, makeReq({ messages: null }));
  assert.equal(ctx.res.status, 400);
});

test('string messages returns 400', async () => {
  const ctx = makeCtx();
  await handler(ctx, makeReq({ messages: 'not an array' }));
  assert.equal(ctx.res.status, 400);
});

test('object messages (not array) returns 400', async () => {
  const ctx = makeCtx();
  await handler(ctx, makeReq({ messages: { role: 'user', content: 'hi' } }));
  assert.equal(ctx.res.status, 400);
});

test('null body is treated as empty — returns 400 for missing messages', async () => {
  const ctx = makeCtx();
  await handler(ctx, { body: null });
  assert.equal(ctx.res.status, 400);
});

// ── Missing env vars ────────────────────────────────────────────────────────

test('missing env vars returns 503', async () => {
  const savedEndpoint = process.env.AZURE_OPENAI_ENDPOINT;
  const savedKey      = process.env.AZURE_OPENAI_API_KEY;
  delete process.env.AZURE_OPENAI_ENDPOINT;
  delete process.env.AZURE_OPENAI_API_KEY;

  try {
    const ctx = makeCtx();
    await handler(ctx, makeReq({ messages: [{ role: 'user', content: 'hi' }] }));
    assert.equal(ctx.res.status, 503);
    assert.match(ctx.res.body.error, /not configured/);
  } finally {
    if (savedEndpoint !== undefined) process.env.AZURE_OPENAI_ENDPOINT = savedEndpoint;
    if (savedKey      !== undefined) process.env.AZURE_OPENAI_API_KEY  = savedKey;
  }
});

test('missing API key alone returns 503', async () => {
  const savedEndpoint = process.env.AZURE_OPENAI_ENDPOINT;
  const savedKey      = process.env.AZURE_OPENAI_API_KEY;
  process.env.AZURE_OPENAI_ENDPOINT = 'https://test.openai.azure.com/';
  delete process.env.AZURE_OPENAI_API_KEY;

  try {
    const ctx = makeCtx();
    await handler(ctx, makeReq({ messages: [{ role: 'user', content: 'hi' }] }));
    assert.equal(ctx.res.status, 503);
  } finally {
    if (savedEndpoint !== undefined) process.env.AZURE_OPENAI_ENDPOINT = savedEndpoint;
    else delete process.env.AZURE_OPENAI_ENDPOINT;
    if (savedKey      !== undefined) process.env.AZURE_OPENAI_API_KEY  = savedKey;
    else delete process.env.AZURE_OPENAI_API_KEY;
  }
});

// ── maxTokens clamping ──────────────────────────────────────────────────────

test('maxTokens above 2000 is clamped to 2000', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }], maxTokens: 999999 },
    mockResp,
    (_ctx, captured) => { assert.equal(captured.body.max_tokens, 2000); }
  );
});

test('maxTokens below 1 is clamped to 1', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }], maxTokens: -50 },
    mockResp,
    (_ctx, captured) => { assert.equal(captured.body.max_tokens, 1); }
  );
});

test('absent maxTokens defaults to 300', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }] },
    mockResp,
    (_ctx, captured) => { assert.equal(captured.body.max_tokens, 300); }
  );
});

test('non-numeric maxTokens ("abc") defaults to 300', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }], maxTokens: 'abc' },
    mockResp,
    (_ctx, captured) => { assert.equal(captured.body.max_tokens, 300); }
  );
});

test('null maxTokens defaults to 300', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }], maxTokens: null },
    mockResp,
    (_ctx, captured) => { assert.equal(captured.body.max_tokens, 300); }
  );
});

// ── messages truncation ─────────────────────────────────────────────────────

test('messages array with 30 entries is truncated to last 20', async () => {
  const msgs = Array.from({ length: 30 }, (_, i) => ({ role: 'user', content: `msg ${i}` }));
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: msgs },
    mockResp,
    (_ctx, captured) => {
      assert.equal(captured.body.messages.length, 20);
      assert.equal(captured.body.messages[0].content, 'msg 10');
    }
  );
});

test('messages array with exactly 20 entries is not truncated', async () => {
  const msgs = Array.from({ length: 20 }, (_, i) => ({ role: 'user', content: `msg ${i}` }));
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: msgs },
    mockResp,
    (_ctx, captured) => { assert.equal(captured.body.messages.length, 20); }
  );
});

// ── API key not leaked in response ──────────────────────────────────────────

test('API key is not included in the response body', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }] },
    mockResp,
    (ctx, _captured) => {
      assert.doesNotMatch(JSON.stringify(ctx.res.body), /test-key/);
    }
  );
});

test('API key is sent in request header not body', async () => {
  const mockResp = { choices: [{ message: { content: 'ok' } }] };
  await withMockAzure(
    { messages: [{ role: 'user', content: 'hi' }] },
    mockResp,
    (_ctx, captured) => {
      assert.equal(captured.headers['api-key'], 'test-key');
      assert.equal(JSON.stringify(captured.body).includes('test-key'), false);
    }
  );
});
