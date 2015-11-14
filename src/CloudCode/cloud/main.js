
// Use Parse.Cloud.define to define as many cloud functions as you want.
// For example:
// Parse.Cloud.define("hello", function(request, response) {
//   response.success("Hello world!");
// });

var twilio = require("twilio");
twilio.initialize("AC0bec7092250cd3794b159a91b9dd1074","1569df3a5048cdcdbb2779b8b45924f1");

Parse.Cloud.define("inviteWithTwilio", function(request, response) {
  twilio.sendSMS({
    From: "2267740367",
    To: request.params.number,
    Body: request.params.message
  }, {
    success: function(httpResponse) {
      console.log(httpResponse);
      response.success("SMS sent!",request.params.number);
    },
    error: function(httpResponse) {
      console.error(httpResponse);
      response.error("Uh oh, something went wrong");
    }
  });
});