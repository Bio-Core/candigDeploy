#!/bin/python                                                                                                                              

import json
import sys

# this program rewrites the client_secrets.json file in the root
# directory of the ga4gh server code as part of the registration
# process with keycloak

# the client_secrets.json file is rewritten so that the client 
# secret matches the client secret stored by the keycloak server
# and that the client id matches that with the keycloak server

# the URLs that indicate keycloak's REST endpoints for the
# authentication process are updated so that they match with 
# the IP, port, and realm keycloak is configured to used

# gather the command line argments

fileName = sys.argv[1]
keycloakIp = sys.argv[2]
clientId = sys.argv[3]
clientSecret = sys.argv[4]
ga4ghIp = sys.argv[5]
realmName = sys.argv[6]
keycloakPort = sys.argv[7]
ga4ghPort = sys.argv[8]

# create the URLs for the data

keycloakRootUrl="http://" + keycloakIp + ":" + keycloakPort + "/auth"

issuer = keycloakRootUrl + "/realms/" + realmName
openidUri =  issuer + "/protocol/openid-connect"
authUri = openidUri + "/auth"
tokenUri =  openidUri + "/token"
tokenIntrospectUri = tokenUri + "/introspect"
userinfoUri = openidUri + "/userinfo"

redirectUri="http://" + ga4ghIp + ":" + ga4ghPort + "/oidc_callback"

uriList = [ redirectUri ]

# generate the json data

webDict = { "auth_uri" : authUri, "issuer" : issuer, "client_id" : clientId, \
"client_secret" : clientSecret, "redirect_uris" : uriList, \
"token_uri" : tokenUri, "token_introspection_uri" : tokenIntrospectUri, \
"userinfo_endpoint" : userinfoUri }

keycloakSecret = { 'web' : webDict }

jsonData = json.dumps(keycloakSecret)

# Rewrite the client_secrets.json file with the new configuration

fileHandle = open(fileName, 'w')
fileHandle.write(jsonData)
fileHandle.close()

exit()


