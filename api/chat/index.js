module.exports = async function (context, req) {
  const body = req.body || {};
  let { messages } = body;
  const maxTokens = Math.min(Math.max(parseInt(body.maxTokens) || 300, 1), 2000);

  if (!messages || !Array.isArray(messages)) {
    context.res = { status: 400, body: { error: 'messages array required' } };
    return;
  }

  // Prevent runaway context windows — keep last 20 turns
  if (messages.length > 20) messages = messages.slice(-20);

  const endpoint   = process.env.AZURE_OPENAI_ENDPOINT;
  const apiKey     = process.env.AZURE_OPENAI_API_KEY;
  const deployment = process.env.AZURE_OPENAI_DEPLOYMENT  || 'gpt-4o-mini';
  const apiVersion = process.env.AZURE_OPENAI_API_VERSION || '2024-12-01-preview';

  if (!endpoint || !apiKey) {
    context.res = { status: 503, body: { error: 'Azure OpenAI not configured on server' } };
    return;
  }

  const url = `${endpoint}/openai/deployments/${deployment}/chat/completions?api-version=${apiVersion}`;

  try {
    const upstream = await fetch(url, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'api-key': apiKey },
      body:    JSON.stringify({ messages, max_tokens: maxTokens }),
    });

    const data = await upstream.json();
    context.res = { status: upstream.status, body: data };
  } catch (err) {
    context.res = { status: 502, body: { error: err.message } };
  }
};
