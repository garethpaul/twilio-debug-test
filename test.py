import os
import logging
import re
import sys

TWILIO_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "silent": logging.CRITICAL + 10,
}
MAX_MESSAGE_BODY_LENGTH = 1600
E164_PHONE_PATTERN = re.compile(r"^\+[1-9][0-9]{1,14}$")
ACCOUNT_SID_PATTERN = re.compile(r"^AC[0-9A-Fa-f]{32}$")
AUTH_TOKEN_PATTERN = re.compile(r"^[0-9A-Fa-f]{32}$")


class MessageValidationError(ValueError):
    pass


class CredentialValidationError(RuntimeError):
    pass


SAFE_CLI_ERROR_TYPES = (MessageValidationError, CredentialValidationError)


class CompanyComms:

    def __init__(self, env=None, client_factory=None):
        self.env = env if env is not None else os.environ
        self.client_factory = client_factory

    def sendMsg(self, to_number=None, from_number=None, body=None):
        """Run basic send message"""
        return self.send_msg(to_number, from_number, body)

    def send_msg(self, to_number=None, from_number=None, body=None):
        payload = self._message_payload(to_number, from_number, body)

        if not should_send_live(self.env):
            return {
                "dry_run": True,
                "to": redact_phone(payload["to"]),
                "from": redact_phone(payload["from"]),
                "body_length": len(payload["body"]),
            }

        validate_live_recipient(self.env, payload["to"])

        missing = [
            name for name in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")
            if not setting_value(self.env.get(name))
        ]
        if missing:
            raise CredentialValidationError(
                "Missing required Twilio credentials: " + ", ".join(missing)
            )

        account_sid = setting_value(self.env.get("TWILIO_ACCOUNT_SID"))
        auth_token = setting_value(self.env.get("TWILIO_AUTH_TOKEN"))
        validate_credentials(account_sid, auth_token)

        client_factory = self.client_factory
        if client_factory is None:
            from twilio.rest import Client
            client_factory = Client

        client = client_factory(
            account_sid,
            auth_token,
        )
        client.http_client.logger.setLevel(twilio_log_level(self.env))

        return client.messages.create(
            to=payload["to"],
            from_=payload["from"],
            body=payload["body"],
        )

    def _message_payload(self, to_number=None, from_number=None, body=None):
        payload = {
            "to": message_setting(to_number, self.env, "TWILIO_TO"),
            "from": message_setting(from_number, self.env, "TWILIO_FROM"),
            "body": message_setting(body, self.env, "TWILIO_BODY"),
        }
        missing = [key for key, value in payload.items() if not value]
        if missing:
            raise MessageValidationError(
                "Missing required Twilio message settings: " + ", ".join(missing)
            )
        validate_phone(payload["to"], "TWILIO_TO")
        validate_phone(payload["from"], "TWILIO_FROM")
        if len(payload["body"]) > MAX_MESSAGE_BODY_LENGTH:
            raise MessageValidationError(
                "Twilio message body must be %d characters or fewer."
                % MAX_MESSAGE_BODY_LENGTH
            )
        return payload


def should_send_live(env=None):
    env = env if env is not None else os.environ
    return setting_value(env.get("TWILIO_SEND_LIVE", "")).lower() == "true"


def twilio_log_level(env=None):
    env = env if env is not None else os.environ
    return TWILIO_LOG_LEVELS.get(
        setting_value(env.get("TWILIO_LOG_LEVEL", "")).lower(),
        logging.INFO,
    )


def setting_value(value):
    if value is None:
        return ""
    return str(value).strip()


def message_setting(override, env, name):
    if override is None:
        return setting_value(env.get(name))
    return setting_value(override)


def validate_phone(value, name):
    if not E164_PHONE_PATTERN.fullmatch(value):
        raise MessageValidationError(
            "{} must be an E.164 phone number.".format(name)
        )


def validate_credentials(account_sid, auth_token):
    if not ACCOUNT_SID_PATTERN.fullmatch(account_sid):
        raise CredentialValidationError("TWILIO_ACCOUNT_SID has an invalid format.")
    if not AUTH_TOKEN_PATTERN.fullmatch(auth_token):
        raise CredentialValidationError("TWILIO_AUTH_TOKEN has an invalid format.")


def validate_live_recipient(env, to_number):
    confirmation = setting_value(env.get("TWILIO_CONFIRM_TO"))
    if not confirmation:
        raise MessageValidationError(
            "Missing required live recipient confirmation: TWILIO_CONFIRM_TO"
        )
    validate_phone(confirmation, "TWILIO_CONFIRM_TO")
    if confirmation != to_number:
        raise MessageValidationError("TWILIO_CONFIRM_TO must match TWILIO_TO.")


def redact_phone(value):
    value = setting_value(value)
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return ("*" * (len(value) - 4)) + value[-4:]


def cli_error_message(error):
    if isinstance(error, SAFE_CLI_ERROR_TYPES):
        return str(error)
    return "Twilio request failed."


def main():
    try:
        result = CompanyComms().send_msg()
    except Exception as error:
        print(cli_error_message(error), file=sys.stderr)
        return 1

    if isinstance(result, dict) and result.get("dry_run"):
        print(
            "Dry run message: to={to} from={from} body_length={body_length}".format(
                **result
            )
        )
    else:
        print(
            "Created message: {}".format(
                redact_phone(getattr(result, "sid", "unknown"))
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
