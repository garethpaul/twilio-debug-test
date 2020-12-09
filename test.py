import os
import logging

from twilio.rest import Client

class CompanyComms:

    def sendMsg(self, to_number, from_number, body):
        """Run basic send message"""

        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        #logging.basicConfig()
        #client.http_client.logger.setLevel(logging.INFO)

        message = client.messages.create(to=os.getenv('TWILIO_TO'),
                                        from_=os.getenv('TWILIO_FROM'),
                                        body=body)
        return message


if __name__ == "__main__":
    c = CompanyComms()
    c.sendMsg('+14242059482', '+12135236830', 'hello')
