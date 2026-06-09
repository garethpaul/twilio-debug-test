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
}).catch((error) => {
  console.error(error);
  process.exit(1);
});
