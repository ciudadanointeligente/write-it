# Integration Guide

There are essentially two ways to use WriteIt. Either have users interact with WriteIt directly or integrate it with another application and only use WriteIt as a backend for sending and receiving messages.

This guide assumes you have WriteIt setup and wish fully integrate it into your application, i.e. users will not know that WriteIt is involved at all.

## Sending messages

Your application will need to create messages using WriteIt's HTTP API. It will need to POST message details in JSON to the correct endpoint.

For details of what you need to do this, first login as an administrator for the Site you want send emails with. Then visit the `/manage/settings/api/` page for full details of what's required, e.g.

https://australia-representatives.writeit.ciudadanointeligente.org/manage/settings/api/

You should see a screen like this:

![API screenshot](http://i.imgur.com/tEHefQu.png)

It contains all the details you need for sending a message via the API. You can use a `curl` command similar to the following to test this from the command line:

```
curl -H "Content-Type: application/json" \
     -X POST \
     -d '{"content": "This is an API test message", "writeitinstance": "/api/v1/instance/1893/","persons":["https://everypolitician-writeinpublic.herokuapp.com/Australia/Senate/persons/person/b6b705a5-0355-4f1c-8951-273aed19156d"], "author_name": "Henare API", "subject": "API test"}' \
     https://australia-representatives.writeit.ciudadanointeligente.org/api/v1/message/?format=json&username=henare&api_key=ABC123
```

## Templates

TODO: You need to ensure the email templates are configured correctly as the standard ones will send people to the WriteIt interface.

## Receiving messages

TODO: When someone replies to a message, how does it get to your application?
