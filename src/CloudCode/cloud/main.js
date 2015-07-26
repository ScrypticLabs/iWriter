// -*- coding: utf-8 -*-
// @Author: Abhi
// @Date:   2015-06-11 14:34:24
// @Last Modified by:   Abhi Gupta
// @Last Modified time: 2015-06-11 17:36:27

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