SendAtom
=======

Alternative feed of system events other than using emails.

Setup/Install
-------------

Currently in development. to test, deploy test/sendatom.conf to one of the following:

  * ~/.config/sendatom.conf
  * /etc/sendatom.conf

and edit it appropriately.

Running
--------

execute sendatomd.py with an optional argument of -c --config CONFIG

you can use bin/sendatom to send a new feed item to a locally running server.
example:

    bin/sendatom 'title' 'content'

if your sendatom server is not running locally, you can use a config at:

  * ~/.config/sendatom-client.conf
  * /etc/sendatom-client.conf

to send to a remote sendatom server.

Dependencies
-------------

Pipfile includes a list of python 3 modules you need:

  * feedgen
  * flask

Note: sendatom depends on python 3.x
