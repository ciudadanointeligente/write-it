---
layout : post
title : Design up-front
---
At the devteam we are not very fans of the design up-front, but we know that we have to make some decisions before start "writeit", in order to discuss and to clear up our ideas. And this in this first post I'm writing about this first day of discussion and it's result, the entities for this new poplus project. In this first approach we are drawing the relationships between a person, it's contacts and the messages (not emails yet, they are going to be implemented as a part of the first plugin).


![Entities](https://docs.google.com/drawings/d/13cAidHSrI7nrlUwpKyeYSDaciyDdxwsysSXfAlIyXZQ/pub?w=960&amp;h=720)


## The plugin structure

In this project because we don't know what the comunication ways are going to be in the future or in other countries, we plan to use plugins to achieve this extensibility. Here it is where the [django-plugins](http://pythonhosted.org/django-plugins/) package comes in, allowing the creation of new features (SMS messages, Fax, Mental comunication, Whatsapp, Twitter).

Of the previous drawing we already know that several classes are going to be extended in order to create new behaviour, of these classes the most obvious is the Message, but also Contact. Here we have an issue not yet solved. Should the contacts come from Popit, as well as People? We know that Popit is not holding any private information from [this issue](https://github.com/mysociety/popit/issues/241). So, if we wanted to have private contacts, the approach should be to create a new reusable django app holding them (May be it is part of a new poplus project).
