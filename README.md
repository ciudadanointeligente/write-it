You write it, and we deliver it.
================================

[![Build Status](https://travis-ci.org/ciudadanointeligente/write-it.png?branch=master)](https://travis-ci.org/ciudadanointeligente/write-it)
[![Coverage Status](https://coveralls.io/repos/ciudadanointeligente/write-it/badge.png?branch=master)](https://coveralls.io/r/ciudadanointeligente/write-it)

Write-it is an application that aims to deliver messages to people whose contacts are to be private or the messages should be public, for example: members of congress. 

Write-it is a layer on top of [popit](http://popit.mysociety.org) from where it takes the people and adds contacts. The way it delivers messages is using plugins for example: mailit. And this approach allows for future ways of delivering for example: twitter, whatsapp, fax or pager.

Future uses are in [votainteligente](http://www.votainteligente.cl) to replace the old "preguntales" (You can [check here](http://municipales2012.votainteligente.cl/valdivia/preguntales), to see how it used to work) feature, could be in the way for the site [writetothem](http://www.writetothem.com/) and any parlamentary monitoring site.



Installation
------------

First step, create a virtualenv

`mkvirtualenv writeit`

Install the requirements

`pip install -r requirements.txt`

(I think I missed half of the commands but that is sort of close)

Testing
-------
For testing you could run ./test.sh

Coverage Analysis
-----------------
For coverage analysis run ./coverage.sh