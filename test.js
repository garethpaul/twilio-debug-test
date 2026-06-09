function required(env, name) {
  const value = settingValue(env[name]);
  if (!value) {
    throw new Error('Missing required Twilio setting: ' + name);
  }
  return value;
}

function settingValue(value) {
  if (value === undefined || value === null) {
    return '';
  }
  return String(value).trim();
}

function shouldSendLive(env) {
  env = env || process.env;
  return settingValue(env.TWILIO_SEND_LIVE).toLowerCase() === 'true';
}

function twilioLogLevel(env) {
  env = env || process.env;
  const value = settingValue(env.TWILIO_LOG_LEVEL).toLowerCase();
  if (['debug', 'info', 'warn', 'error', 'silent'].indexOf(value) !== -1) {
    return value;
  }
  return 'info';
}

function redactPhone(value) {
  value = settingValue(value);
  if (!value) {
    return '';
  }
  if (value.length <= 4) {
    return '****';
  }
  return '*'.repeat(value.length - 4) + value.slice(-4);
}

function createMessagePayload(env) {
  env = env || process.env;
  return {
    from: required(env, 'TWILIO_FROM'),
    to: required(env, 'TWILIO_TO'),
    body: required(env, 'TWILIO_BODY')
  };
}

async function sendMessage(env) {
  env = env || process.env;
  const payload = createMessagePayload(env);

  if (!shouldSendLive(env)) {
    const result = {
      dryRun: true,
      from: redactPhone(payload.from),
      to: redactPhone(payload.to),
      bodyLength: payload.body.length
    };
    console.log(JSON.stringify(result));
    return result;
  }

  const accountSid = required(env, 'TWILIO_ACCOUNT_SID');
  const authToken = required(env, 'TWILIO_AUTH_TOKEN');
  const client = require('twilio')(accountSid, authToken);
  client.logLevel = twilioLogLevel(env);

  const message = await client.messages.create(payload);
  console.log('Created message using promises');
  console.log(message.sid);
  return message;
}

if (require.main === module) {
  sendMessage().catch(function(error) {
    console.error(error.message);
    process.exit(1);
  });
}

module.exports = {
  createMessagePayload,
  redactPhone,
  sendMessage,
  shouldSendLive,
  twilioLogLevel
};
