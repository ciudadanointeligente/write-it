# Integration Guide

There are essentially two ways to use WriteIt. Either have users interact with WriteIt directly or integrate it with another application and only use WriteIt as a backend for sending and receiving messages.

This guide assumes you have WriteIt setup and wish fully integrate it into your application, i.e. users will not know that WriteIt is involved at all.

## Sending messages

Your application will need to create messages using WriteIt's HTTP API. It will need to POST message details in JSON to the correct endpoint.

For details of what you need to do this, first login as an administrator for the Site you want send emails with. Then visit the `/manage/settings/api/` page for full details of what's required, e.g.

https://australia-representatives.writeit.ciudadanointeligente.org/manage/settings/api/

You should see a screen like this:

![API settings screenshot](http://i.imgur.com/tEHefQu.png)

It contains all the details you need for sending a message via the API. You can use a `curl` command similar to the following to test this from the command line:

```
curl -H "Content-Type: application/json" \
     -X POST \
     -d '{"content": "This is an API test message", "writeitinstance": "/api/v1/instance/1893/","persons":["https://everypolitician-writeinpublic.herokuapp.com/Australia/Senate/persons/person/b6b705a5-0355-4f1c-8951-273aed19156d"], "author_name": "Henare API", "author_email": "henare@example.org", "subject": "API test"}' \
     https://australia-representatives.writeit.ciudadanointeligente.org/api/v1/message/?format=json&username=henare&api_key=ABC123
```

## Templates

There are 3 message templates in WriteIt; _Mail Template_, _Confirmation Template_, and _New answer notification template_. These are configured on the Templates page which is at the `/manage/settings/templates/` address of your Site, e.g.

https://australia-representatives.writeit.ciudadanointeligente.org/manage/settings/templates/

### Mail Template

This template should probably be emptied out to only contain:

    {content}

This will give your application the greatest control over the messages it sends as you will be able to specify the full content and subject in your API call.

### Confirmation Template

WriteIt should be configured by default to not require confirmation for messages sent via the API, therefore this template will not be used. You can check this setting at the `/manage/api/settings/` address for your site, e.g.

https://australia-representatives.writeit.ciudadanointeligente.org/manage/api/settings/

### New answer notification template

If WriteIt is integrated into your application you probably want your application to be responsible for sending new answer notifications instead of them being sent by WriteIt. When your application receives a message from WriteIt it should notify the original sender that they have a new message and to visit your application to see it.

To achieve this set the `author_email` to an administrator mailbox you control when you create new messgaes via the API. This will redirect these WriteIt new answer messages to you and is a handy check that your application should be getting messages from WriteIt.

## Receiving messages

TODO: When someone replies to a message, how does it get to your application?
