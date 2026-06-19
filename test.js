const MAX_MESSAGE_BODY_LENGTH = 1600;
const PROVIDER_REQUEST_TIMEOUT_MS = 30000;
const E164_PHONE_PATTERN = /^\+[1-9][0-9]{1,14}$/;
const ACCOUNT_SID_PATTERN = /^AC[0-9A-Fa-f]{32}$/;
const AUTH_TOKEN_PATTERN = /^[0-9A-Fa-f]{32}$/;

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

function validatePhone(value, name) {
  if (!E164_PHONE_PATTERN.test(value)) {
    throw new MessageValidationError(name + ' must be an E.164 phone number.');
  }
}

function validateCredentials(accountSid, authToken) {
  if (!ACCOUNT_SID_PATTERN.test(accountSid)) {
    throw new CredentialValidationError('TWILIO_ACCOUNT_SID has an invalid format.');
  }
  if (!AUTH_TOKEN_PATTERN.test(authToken)) {
    throw new CredentialValidationError('TWILIO_AUTH_TOKEN has an invalid format.');
  }
}

function validateLiveRecipient(env, toNumber) {
  const confirmation = settingValue(env.TWILIO_CONFIRM_TO);
  if (!confirmation) {
    throw new MessageValidationError(
      'Missing required live recipient confirmation: TWILIO_CONFIRM_TO'
    );
  }
  validatePhone(confirmation, 'TWILIO_CONFIRM_TO');
  if (confirmation !== toNumber) {
    throw new MessageValidationError('TWILIO_CONFIRM_TO must match TWILIO_TO.');
  }
}

async function defaultPromptRecipient(prompt) {
  const readline = require('readline/promises');
  const promptInterface = readline.createInterface({
    input: process.stdin,
    output: process.stderr
  });
  try {
    return await promptInterface.question(prompt);
  } finally {
    promptInterface.close();
  }
}

async function confirmLiveExecution(env, toNumber, confirmationOptions) {
  confirmationOptions = confirmationOptions || {};
  const isInteractive = confirmationOptions.isInteractive === undefined
    ? Boolean(process.stdin.isTTY && process.stderr.isTTY)
    : confirmationOptions.isInteractive;
  if (!isInteractive) {
    if (settingValue(env.TWILIO_ALLOW_NONINTERACTIVE).toLowerCase() === 'true') {
      return;
    }
    throw new MessageValidationError(
      'Live sends require a TTY confirmation or TWILIO_ALLOW_NONINTERACTIVE=true.'
    );
  }

  const promptRecipient = confirmationOptions.promptRecipient || defaultPromptRecipient;
  const prompt = "Type 'send " + toNumber.slice(-4) + "' to send live to " +
    redactPhone(toNumber) + ': ';
  let confirmation;
  try {
    confirmation = settingValue(await promptRecipient(prompt)).toLowerCase();
  } catch (error) {
    throw new MessageValidationError('Interactive confirmation did not match TWILIO_TO.');
  }
  if (confirmation !== 'send ' + toNumber.slice(-4)) {
    throw new MessageValidationError('Interactive confirmation did not match TWILIO_TO.');
  }
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
  validatePhone(payload.to, 'TWILIO_TO');
  validatePhone(payload.from, 'TWILIO_FROM');
  if (payload.body.length > MAX_MESSAGE_BODY_LENGTH) {
    throw new MessageValidationError(
      'Twilio message body must be ' + MAX_MESSAGE_BODY_LENGTH + ' characters or fewer.'
    );
  }
  return payload;
}

async function sendMessage(env, clientFactory, confirmationOptions) {
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

  validateLiveRecipient(env, payload.to);
  await confirmLiveExecution(env, payload.to, confirmationOptions);

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
  validateCredentials(accountSid, authToken);
  const createClient = clientFactory || require('twilio');
  const client = createClient(accountSid, authToken, {
    autoRetry: false,
    timeout: PROVIDER_REQUEST_TIMEOUT_MS
  });
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
  confirmLiveExecution,
  CredentialValidationError,
  createMessagePayload,
  MAX_MESSAGE_BODY_LENGTH,
  MessageValidationError,
  PROVIDER_REQUEST_TIMEOUT_MS,
  redactPhone,
  runCli,
  sendMessage,
  shouldSendLive,
  twilioLogLevel
};
