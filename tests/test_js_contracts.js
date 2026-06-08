const assert = require('assert');
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
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: 'false' }), false);
assert.throws(
  () => sample.createMessagePayload({ TWILIO_TO: 'to-4567' }),
  /TWILIO_FROM/
);

sample.sendMessage(env).then((result) => {
  assert.strictEqual(result.dryRun, true);
  assert.strictEqual(result.to, '***4567');
  assert.strictEqual(result.from, '*****4321');
  assert.strictEqual(result.bodyLength, 15);
}).catch((error) => {
  console.error(error);
  process.exit(1);
});
