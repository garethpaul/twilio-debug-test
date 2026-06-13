const assert = require('assert');
const childProcess = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const sample = require('../test.js');
const VALID_ACCOUNT_SID = 'AC' + '0123456789abcdef'.repeat(2);
const VALID_AUTH_TOKEN = '0123456789abcdef'.repeat(2);

const preloadDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'twilio-debug-cli-'));
const preloadPath = path.join(preloadDirectory, 'before-exit.js');
fs.writeFileSync(
  preloadPath,
  "process.on('beforeExit', function() { process.stdout.write('BEFORE_EXIT\\n'); });\n"
);
try {
  const cliResult = childProcess.spawnSync(
    process.execPath,
    ['--require', preloadPath, path.join(__dirname, '..', 'test.js')],
    {
      encoding: 'utf8',
      env: {
        TWILIO_FROM: '+12025550124',
        TWILIO_TO: '+12025550123',
        TWILIO_BODY: 'subprocess body'
      }
    }
  );
  assert.strictEqual(cliResult.status, 0);
  assert.strictEqual(cliResult.stderr, '');
  assert.strictEqual(
    cliResult.stdout,
    '{"dryRun":true,"from":"********0124","to":"********0123","bodyLength":15}\nBEFORE_EXIT\n'
  );

  const failedCliResult = childProcess.spawnSync(
    process.execPath,
    ['--require', preloadPath, path.join(__dirname, '..', 'test.js')],
    { encoding: 'utf8', env: {} }
  );
  assert.strictEqual(failedCliResult.status, 1);
  assert.strictEqual(failedCliResult.stdout, 'BEFORE_EXIT\n');
  assert.strictEqual(
    failedCliResult.stderr,
    'Missing required Twilio message settings: TWILIO_FROM, TWILIO_TO, TWILIO_BODY\n'
  );
} finally {
  fs.rmSync(preloadDirectory, { recursive: true });
}

const env = {
  TWILIO_TO: '+12025550123',
  TWILIO_FROM: '+12025550124',
  TWILIO_BODY: 'hello from node'
};

const payload = sample.createMessagePayload(env);
assert.deepStrictEqual(payload, {
  from: '+12025550124',
  to: '+12025550123',
  body: 'hello from node'
});

assert.strictEqual(sample.redactPhone('+12025550123'), '********0123');
assert.strictEqual(sample.redactPhone('SM1234567890'), '********7890');
assert.strictEqual(
  sample.cliErrorMessage(new Error('provider response included auth-token-secret')),
  'Twilio request failed.'
);
assert.strictEqual(
  sample.cliErrorMessage(new Error('Missing required Twilio credentials: auth-token-secret')),
  'Twilio request failed.'
);
assert.strictEqual(
  sample.cliErrorMessage(new Error('Missing required Twilio message settings: customer-phone-number')),
  'Twilio request failed.'
);
assert.strictEqual(
  sample.cliErrorMessage(new Error('Twilio message body must be credential-secret')),
  'Twilio request failed.'
);
assert.strictEqual(
  sample.cliErrorMessage(new sample.MessageValidationError('Missing required Twilio message settings: TWILIO_TO')),
  'Missing required Twilio message settings: TWILIO_TO'
);
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: 'true' }), true);
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: ' TRUE ' }), true);
assert.strictEqual(sample.shouldSendLive({ TWILIO_SEND_LIVE: 'false' }), false);
assert.strictEqual(sample.twilioLogLevel({}), 'info');
assert.strictEqual(sample.twilioLogLevel({ TWILIO_LOG_LEVEL: ' DEBUG ' }), 'debug');
assert.strictEqual(sample.twilioLogLevel({ TWILIO_LOG_LEVEL: ' WARNING ' }), 'warn');
assert.strictEqual(sample.twilioLogLevel({ TWILIO_LOG_LEVEL: 'noisy' }), 'info');
assert.strictEqual(typeof sample.runCli, 'function');
assert.strictEqual(sample.MAX_MESSAGE_BODY_LENGTH, 1600);
assert.ok(
  fs.readFileSync(path.join(__dirname, '..', 'test.js'), 'utf8')
    .includes('client.logLevel = twilioLogLevel(env);')
);
assert.throws(
  () => sample.createMessagePayload({ TWILIO_TO: '+12025550123' }),
  /Missing required Twilio message settings: TWILIO_FROM, TWILIO_BODY/
);
assert.throws(
  () => sample.createMessagePayload({
    TWILIO_FROM: '+12025550124',
    TWILIO_TO: '+12025550123',
    TWILIO_BODY: '   '
  }),
  /TWILIO_BODY/
);
assert.throws(
  () => sample.createMessagePayload({
    TWILIO_FROM: '+12025550124',
    TWILIO_TO: '+12025550123',
    TWILIO_BODY: 'x'.repeat(sample.MAX_MESSAGE_BODY_LENGTH + 1)
  }),
  /1600 characters/
);
assert.deepStrictEqual(sample.createMessagePayload({
  TWILIO_FROM: '  +12025550124  ',
  TWILIO_TO: '  +12025550123  ',
  TWILIO_BODY: '  hello  '
}), {
  from: '+12025550124',
  to: '+12025550123',
  body: 'hello'
});
assert.deepStrictEqual(sample.createMessagePayload({
  TWILIO_FROM: '+123456789012345',
  TWILIO_TO: '+12',
  TWILIO_BODY: 'hello'
}), {
  from: '+123456789012345',
  to: '+12',
  body: 'hello'
});
[
  '15551234567',
  '+05551234567',
  '+1 5551234567',
  '+1-555-123-4567',
  '+12025550123x9',
  '+١٢',
  '+1234567890123456'
].forEach((invalidValue) => {
  ['TWILIO_TO', 'TWILIO_FROM'].forEach((field) => {
    const invalidEnv = {
      TWILIO_FROM: '+12025550124',
      TWILIO_TO: '+12025550123',
      TWILIO_BODY: 'hello'
    };
    invalidEnv[field] = invalidValue;
    assert.throws(
      () => sample.createMessagePayload(invalidEnv),
      new RegExp(field + ' must be an E\\.164 phone number')
    );
  });
});

sample.sendMessage(env).then((result) => {
  assert.strictEqual(result.dryRun, true);
  assert.strictEqual(result.to, '********0123');
  assert.strictEqual(result.from, '********0124');
  assert.strictEqual(result.bodyLength, 15);
  let dryRunFactoryCalls = 0;
  return sample.sendMessage({
    TWILIO_ACCOUNT_SID: 'not-an-account-sid',
    TWILIO_AUTH_TOKEN: 'not-an-auth-token',
    TWILIO_TO: '+12025550123',
    TWILIO_FROM: '+12025550124',
    TWILIO_BODY: 'dry run'
  }, function() {
    dryRunFactoryCalls += 1;
  }).then((dryRunResult) => {
    assert.strictEqual(dryRunResult.dryRun, true);
    assert.strictEqual(dryRunFactoryCalls, 0);

    const validCredentials = {
      TWILIO_SEND_LIVE: 'true',
      TWILIO_ACCOUNT_SID: VALID_ACCOUNT_SID,
      TWILIO_AUTH_TOKEN: VALID_AUTH_TOKEN,
      TWILIO_TO: '+12025550123',
      TWILIO_FROM: '+12025550124',
      TWILIO_BODY: 'live body'
    };
    const invalidCredentials = [
      ['TWILIO_ACCOUNT_SID', 'SK' + VALID_ACCOUNT_SID.slice(2)],
      ['TWILIO_ACCOUNT_SID', VALID_ACCOUNT_SID.slice(0, -1)],
      ['TWILIO_ACCOUNT_SID', VALID_ACCOUNT_SID + '0'],
      ['TWILIO_ACCOUNT_SID', VALID_ACCOUNT_SID.slice(0, -1) + 'G'],
      ['TWILIO_ACCOUNT_SID', 'AC０' + VALID_ACCOUNT_SID.slice(3, -1)],
      ['TWILIO_AUTH_TOKEN', VALID_AUTH_TOKEN.slice(0, -1)],
      ['TWILIO_AUTH_TOKEN', VALID_AUTH_TOKEN + '0'],
      ['TWILIO_AUTH_TOKEN', VALID_AUTH_TOKEN.slice(0, -1) + 'G'],
      ['TWILIO_AUTH_TOKEN', '０' + VALID_AUTH_TOKEN.slice(1, -1)]
    ];
    let invalidFactoryCalls = 0;

    return invalidCredentials.reduce((promise, invalidCredential) => {
      return promise.then(() => {
        const invalidEnv = Object.assign({}, validCredentials);
        invalidEnv[invalidCredential[0]] = invalidCredential[1];
        return sample.sendMessage(invalidEnv, function() {
          invalidFactoryCalls += 1;
        }).then(() => {
          assert.fail('malformed credentials must reject');
        }, (error) => {
          assert(error instanceof sample.CredentialValidationError);
          assert.strictEqual(
            error.message,
            invalidCredential[0] + ' has an invalid format.'
          );
        });
      });
    }, Promise.resolve()).then(() => {
      assert.strictEqual(invalidFactoryCalls, 0);
    });
  }).then(() => {
  let createdClient;
  let seenAccountSid;
  let seenAuthToken;
  let seenPayload;
  const liveEnv = {
    TWILIO_SEND_LIVE: 'true',
    TWILIO_ACCOUNT_SID: VALID_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN: VALID_AUTH_TOKEN,
    TWILIO_TO: '+12025550123',
    TWILIO_FROM: '+12025550124',
    TWILIO_BODY: 'live body'
  };
  const liveLogs = [];
  const originalConsoleLog = console.log;
  console.log = function(message) {
    liveLogs.push(String(message));
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
    assert.strictEqual(seenAccountSid, VALID_ACCOUNT_SID);
    assert.strictEqual(seenAuthToken, VALID_AUTH_TOKEN);
    assert.strictEqual(createdClient.logLevel, 'info');
    assert.deepStrictEqual(seenPayload, {
      from: '+12025550124',
      to: '+12025550123',
      body: 'live body'
    });
    assert.strictEqual(message.sid, 'SMNODE123');
    assert.deepStrictEqual(liveLogs, ['Created message: *****E123']);
    assert.strictEqual(liveLogs.join('\n').includes('SMNODE123'), false);
    return sample.sendMessage(liveEnv, function() {
      return {
        logLevel: null,
        messages: {
          create: async function() {
            return {};
          }
        }
      };
    }).then((messageWithoutSid) => {
      assert.deepStrictEqual(messageWithoutSid, {});
      assert.strictEqual(liveLogs[liveLogs.length - 1], 'Created message: ***nown');
    }).then(() => {
      console.log = originalConsoleLog;
      const cliErrors = [];
      return sample.runCli({}, function(message) {
        cliErrors.push(message);
      }).then((exitCode) => {
        assert.strictEqual(exitCode, 1);
        assert.deepStrictEqual(cliErrors, [
          'Missing required Twilio message settings: TWILIO_FROM, TWILIO_TO, TWILIO_BODY'
        ]);

        const invalidPhoneErrors = [];
        return sample.runCli({
          TWILIO_FROM: '+12025550124',
          TWILIO_TO: 'not-a-phone',
          TWILIO_BODY: 'live body'
        }, function(message) {
          invalidPhoneErrors.push(message);
        }).then((invalidPhoneExitCode) => {
          assert.strictEqual(invalidPhoneExitCode, 1);
          assert.deepStrictEqual(invalidPhoneErrors, [
            'TWILIO_TO must be an E.164 phone number.'
          ]);

          const credentialErrors = [];
          return sample.runCli({
            TWILIO_SEND_LIVE: 'true',
            TWILIO_FROM: '+12025550124',
            TWILIO_TO: '+12025550123',
            TWILIO_BODY: 'live body'
          }, function(message) {
            credentialErrors.push(message);
          }).then((credentialExitCode) => {
            assert.strictEqual(credentialExitCode, 1);
            assert.deepStrictEqual(credentialErrors, [
              'Missing required Twilio credentials: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN'
            ]);
            const providerErrors = [];
            let providerCalls = 0;
            return sample.runCli(liveEnv, function(message) {
              providerErrors.push(message);
            }, function() {
              return {
                logLevel: null,
                messages: {
                  create: async function() {
                    providerCalls += 1;
                    throw new Error('provider response included auth-token-secret');
                  }
                }
              };
            }).then((providerExitCode) => {
              assert.strictEqual(providerExitCode, 1);
              assert.strictEqual(providerCalls, 1);
              assert.deepStrictEqual(providerErrors, ['Twilio request failed.']);
            });
          });
        });
      });
    });
  }).catch((error) => {
    console.log = originalConsoleLog;
    throw error;
  });
  });
}).catch((error) => {
  console.error(error);
  process.exit(1);
});
