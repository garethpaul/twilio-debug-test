import os
import logging

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

        missing = [
            name for name in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")
            if not setting_value(self.env.get(name))
        ]
        if missing:
            raise RuntimeError(
                "Missing required Twilio credentials: " + ", ".join(missing)
            )

        client_factory = self.client_factory
        if client_factory is None:
            from twilio.rest import Client
            client_factory = Client

        client = client_factory(
            setting_value(self.env.get("TWILIO_ACCOUNT_SID")),
            setting_value(self.env.get("TWILIO_AUTH_TOKEN")),
        )
        client.http_client.logger.setLevel(logging.INFO)

        return client.messages.create(
            to=payload["to"],
            from_=payload["from"],
            body=payload["body"],
        )

    def _message_payload(self, to_number=None, from_number=None, body=None):
        payload = {
            "to": (
                setting_value(to_number) or setting_value(self.env.get("TWILIO_TO"))
            ),
            "from": (
                setting_value(from_number) or setting_value(self.env.get("TWILIO_FROM"))
            ),
            "body": (
                setting_value(body) or setting_value(self.env.get("TWILIO_BODY"))
            ),
        }
        missing = [key for key, value in payload.items() if not value]
        if missing:
            raise ValueError(
                "Missing required Twilio message settings: " + ", ".join(missing)
            )
        return payload


def should_send_live(env=None):
    env = env if env is not None else os.environ
    return setting_value(env.get("TWILIO_SEND_LIVE", "")).lower() == "true"


def setting_value(value):
    if value is None:
        return ""
    return str(value).strip()


def redact_phone(value):
    value = setting_value(value)
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return ("*" * (len(value) - 4)) + value[-4:]


def main():
    result = CompanyComms().send_msg()
    if isinstance(result, dict) and result.get("dry_run"):
        print(
            "Dry run message: to={to} from={from} body_length={body_length}".format(
                **result
            )
        )
    else:
        print("Created message: {}".format(getattr(result, "sid", "<unknown>")))


if __name__ == "__main__":
    main()
