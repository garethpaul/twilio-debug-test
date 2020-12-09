# TWILIO HELPER LIB DEBUGGING

Below are examples in each language

## Python 
```
client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
logging.basicConfig()
client.http_client.logger.setLevel(logging.INFO)
```

## NodeJS
```
const client = require('twilio')(accountSid, authToken)
client.logLevel = 'debug'
```

## Ruby
```
@client = Twilio::REST::Client.new account_sid, auth_token
myLogger = Logger.new(STDOUT)
myLogger.level = Logger::DEBUG
@client.logger = myLogger
```

## PHP
```
$client = new Twilio\Rest\Client($sid, $token);
$client->setLogLevel('debug');
```

## Java
```
Twilio.init(accountSid, authToken);
Twilio.setLoggerConfiguration("path/to/log4j2.xml");
```

```
<?xml version="1.0" encoding="UTF-8"?>
<!--logging configuration file example-->
<Configuration status="warn" name="MyApp" packages="">
    <Appenders>
        <Console name="STDOUT" target="SYSTEM_OUT">
            <PatternLayout pattern="%d [%t] %-5p %c - %m%n"/>
        </Console>
    </Appenders>
    <Loggers>
        <Root level="debug">
            <AppenderRef ref="STDOUT"/>
        </Root>
    </Loggers>
</Configuration>
```
