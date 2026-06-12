const MAX_MESSAGE_BODY_LENGTH = 1600;

class MessageValidationError extends Error {}
class CredentialValidationError extends Error {}

function missingSettings(env, names) {
  return names.filter(function(name) {
    return !settingValue(env[name]);
  });
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
  const supportedLevels = {
    debug: 'debug',
    info: 'info',
    warn: 'warn',
    warning: 'warn',
    error: 'error',
    silent: 'silent'
  };
  return supportedLevels[value] || 'info';
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

function cliErrorMessage(error) {
  if (error instanceof MessageValidationError || error instanceof CredentialValidationError) {
    return error.message;
  }
  return 'Twilio request failed.';
}

function createMessagePayload(env) {
  env = env || process.env;
  const missingMessageSettings = missingSettings(env, [
    'TWILIO_FROM',
    'TWILIO_TO',
    'TWILIO_BODY'
  ]);
  if (missingMessageSettings.length) {
    throw new MessageValidationError(
      'Missing required Twilio message settings: ' + missingMessageSettings.join(', ')
    );
  }

  const payload = {
    from: settingValue(env.TWILIO_FROM),
    to: settingValue(env.TWILIO_TO),
    body: settingValue(env.TWILIO_BODY)
  };
  if (payload.body.length > MAX_MESSAGE_BODY_LENGTH) {
    throw new MessageValidationError(
      'Twilio message body must be ' + MAX_MESSAGE_BODY_LENGTH + ' characters or fewer.'
    );
  }
  return payload;
}

async function sendMessage(env, clientFactory) {
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

  const missingCredentials = missingSettings(env, [
    'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN'
  ]);
  if (missingCredentials.length) {
    throw new CredentialValidationError(
      'Missing required Twilio credentials: ' + missingCredentials.join(', ')
    );
  }

  const accountSid = settingValue(env.TWILIO_ACCOUNT_SID);
  const authToken = settingValue(env.TWILIO_AUTH_TOKEN);
  const createClient = clientFactory || require('twilio');
  const client = createClient(accountSid, authToken);
  client.logLevel = twilioLogLevel(env);

  const message = await client.messages.create(payload);
  console.log('Created message: ' + redactPhone(message.sid || 'unknown'));
  return message;
}

async function runCli(env, logError, clientFactory) {
  env = env || process.env;
  logError = logError || console.error;

  try {
    await sendMessage(env, clientFactory);
    return 0;
  } catch (error) {
    logError(cliErrorMessage(error));
    return 1;
  }
}

if (require.main === module) {
  runCli().then(function(exitCode) {
    process.exitCode = exitCode;
  });
}

module.exports = {
  cliErrorMessage,
  CredentialValidationError,
  createMessagePayload,
  MAX_MESSAGE_BODY_LENGTH,
  MessageValidationError,
  redactPhone,
  runCli,
  sendMessage,
  shouldSendLive,
  twilioLogLevel
};
