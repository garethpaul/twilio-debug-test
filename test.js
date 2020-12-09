var accountSid = process.env.TWILIO_ACCOUNT_SID; // Your Account SID from www.twilio.com/console
var authToken = process.env.TWILIO_AUTH_TOKEN;   // Your Auth Token from www.twilio.com/console

const client = require('twilio')(accountSid, authToken)
//client.logLevel = 'debug'

// 
let to = process.env.TWILIO_TO;
let from = process.env.TWILIO_FROM;

// Send message using promise
var promise = client.messages.create({
    from: from,
    to: to,
    body: 'create using promises'
});

// After Sending Message Get the Message Sid
promise.then(function(message) {
    console.log('Created message using promises');
    console.log(message.sid);
 });
