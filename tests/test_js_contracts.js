const assert = require('assert');
const fs = require('fs');
const path = require('path');
const sample = require('../test.js');

const env = {
  TWILIO_TO: 'to-4567',
  TWILIO_FROM: 'from-4321',
  TWILIO_BODY: 'hello from node'
};

const payload = sample.createMessagePayload(env);
assert.deepStrictEqual(payload, {
  from: 'from-4321',
  to: 'to-4567',
  body: 'hello from node'
});

assert.strictEqual(sample.redactPhone('to-4567'), '***4567');
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: 'true' }), true);
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: ' TRUE ' }), true);
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: 'false' }), false);
assert.strictEqual(sample.twilioLogLevel({}), 'info');
assert.strictEqual(sample.twilioLogLevel({ TWILIO_LOG_LEVEL: ' DEBUG ' }), 'debug');
assert.strictEqual(sample.twilioLogLevel({ TWILIO_LOG_LEVEL: ' WARNING ' }), 'warn');
assert.strictEqual(sample.twilioLogLevel({ TWILIO_LOG_LEVEL: 'noisy' }), 'info');
assert.ok(
  fs.readFileSync(path.join(__dirname, '..', 'test.js'), 'utf8')
    .includes('client.logLevel = twilioLogLevel(env);')
);
assert.throws(
  () => sample.createMessagePayload({ TWILIO_TO: 'to-4567' }),
  /TWILIO_FROM/
);
assert.throws(
  () => sample.createMessagePayload({
    TWILIO_FROM: 'from-4321',
    TWILIO_TO: 'to-4567',
    TWILIO_BODY: '   '
  }),
  /TWILIO_BODY/
);
assert.deepStrictEqual(sample.createMessagePayload({
  TWILIO_FROM: '  from-4321  ',
  TWILIO_TO: '  to-4567  ',
  TWILIO_BODY: '  hello  '
}), {
  from: 'from-4321',
  to: 'to-4567',
  body: 'hello'
});

sample.sendMessage(env).then((result) => {
  assert.strictEqual(result.dryRun, true);
  assert.strictEqual(result.to, '***4567');
  assert.strictEqual(result.from, '*****4321');
  assert.strictEqual(result.bodyLength, 15);
  let createdClient;
  let seenAccountSid;
  let seenAuthToken;
  let seenPayload;
  const liveEnv = {
    TWILIO_SEND_LIVE: 'true',
    TWILIO_ACCOUNT_SID: 'AC123',
    TWILIO_AUTH_TOKEN: 'secret',
    TWILIO_TO: 'to-4567',
    TWILIO_FROM: 'from-4321',
    TWILIO_BODY: 'live body'
  };
  return sample.sendMessage(liveEnv, function(accountSid, authToken) {
    seenAccountSid = accountSid;
    seenAuthToken = authToken;
    createdClient = {
      logLevel: null,
      messages: {
        create: async function(payload) {
          seenPayload = payload;
          return { sid: 'SMNODE123' };
        }
      }
    };
    return createdClient;
  }).then((message) => {
    assert.strictEqual(seenAccountSid, 'AC123');
    assert.strictEqual(seenAuthToken, 'secret');
    assert.strictEqual(createdClient.logLevel, 'info');
    assert.deepStrictEqual(seenPayload, {
      from: 'from-4321',
      to: 'to-4567',
      body: 'live body'
    });
    assert.strictEqual(message.sid, 'SMNODE123');
  });
}).catch((error) => {
  console.error(error);
  process.exit(1);
});
