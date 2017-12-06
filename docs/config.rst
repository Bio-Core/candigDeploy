Manual Configuration
===============================

The servers are automatically configured through the deployment program.

An alternative way to configure them is to this manually. Most of this information can be found in the Keycloak documentation.

You will likely have to recreate a new configuration file for the deployment program to load on each new major Keycloak release.

Log into the Keycloak server. By default, the server will listen on
``127.0.0.1:8080``. You can change the IP address through the ``-b`` option.

For first-time use, you need to create the default admin account. 
There are two ways to do this:

1. Through the shell script
2. Through the administration console

Create a new realm with the realm name ``CanDIG``.

Under the ``CanDIG`` realm, create two clients:

The first will be for the GA4GH server. Use the ``Client ID`` ``ga4gh``. 
Click on the ga4gh client in the list. 
Change ``Access Type`` to ``Confidential``. 
Add a ``Valid Redirect URIs`` for ``http://127.0.0.1:8000/*``.
The asterisk will allow all URLs under the IP and port number using
HTTP to be allowed.
Set the ``Base URL`` to ``http://127.0.0.1:8000``.

For the funnel client, set ``Client ID`` to ``funnel``.
Set the ``Access Type`` to ``Confidental``. 
Add a ``Valid Redirect URIs`` for ``http://127.0.0.1:3002/*``.
Set the ``Base URL`` to ``http://127.0.0.1:3002``.

Go to the ``Users`` menu and select ``Add user``.
Set the ``username`` to ``user``.
Go back to the ``Users`` menu and choose ``View all users``.
Go to ``Edit`` under the newly created user ``user``.
Go to ``Credentials`` and set a new password.
Under ``Manage Password``, set both ``New Password`` and 
``Password Confirmation`` to ``user``.
Deactivate ``Temporary`` to ``OFF``.

Exporting the Configuration
-------------------------------

Stop the server.

Use bin/standalone.sh to perform a full export of the realm.
Not only will this include the clients, but it will also
include the users as well as other information.
Perform an export into a single JSON file.

::

    ./bin/standalone.sh -Dkeycloak.migration.action=export -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file=keycloakConfig.json

Keycloak will start a new server instance that will export into the file
``keycloakConfig.json``.

You can then halt the server shortly after it started to retrieve the configuration file. You can tell that the file is finished being written to once its file size stops growing.


Importing the Configuration
------------------------------------

Import the configuration when running ``standalone.sh`` using:

::

    bin/standalone.sh -Dkeycloak.migration.action=import -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file=keycloakConfig.json -Dkeycloak.migration.strategy=OVERWRITE_EXISTING

This will cause the Keycloak server to be loaded with the full configuration.

For this to be successful on non-root singularity containers, the container must be built as ``--writable`` and the user must be executing as ``--writable`` with write permissions. The image must also be resized to offer sufficient space for the database to be written to.
